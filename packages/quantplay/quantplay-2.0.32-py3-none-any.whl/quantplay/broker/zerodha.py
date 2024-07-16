import codecs
import pickle
import traceback
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Hashable, List

import pandas as pd
import polars as pl
from kiteconnect import KiteConnect, KiteTicker
from kiteconnect.exceptions import TokenException
from retrying import retry  # type: ignore

from quantplay.broker.generics.broker import Broker
from quantplay.broker.kite_utils import KiteUtils
from quantplay.exception.exceptions import (
    InvalidArgumentException,
    QuantplayOrderPlacementException,
    RetryableException,
    retry_exception,
)
from quantplay.exception.exceptions import TokenException as QuantplayTokenException
from quantplay.model.broker import (
    ExchangeType,
    ModifyOrderRequest,
    UserBrokerProfileResponse,
)
from quantplay.utils.constant import Constants
from quantplay.utils.pickle_utils import InstrumentData, PickleUtils


class Zerodha(Broker):
    stoploss = "stoploss"
    zerodha_api_key = "zerodha_api_key"
    zerodha_api_secret = "zerodha_api_secret"
    zerodha_wrapper = "zerodha_wrapper"

    def __init__(
        self,
        wrapper=None,
        user_id: str | None = None,
        api_key: str | None = None,
        api_secret: str | None = None,
        password: str | None = None,
        totp: str | None = None,
        load_instrument: bool = True,
    ):
        self.wrapper: KiteConnect
        try:
            if wrapper:
                self.set_wrapper(wrapper)
            else:
                self.generate_token(user_id, api_key, api_secret, password, totp)
        except Exception as e:
            raise e

        if load_instrument:
            self.initialize_symbol_data()
        self.broker_symbol_map = {}
        super(Zerodha, self).__init__()

    def set_wrapper(self, serialized_wrapper):
        self.wrapper = pickle.loads(codecs.decode(serialized_wrapper.encode(), "base64"))

    def initialize_symbol_data(self, save_as: str | None = None) -> None:
        try:
            self.symbol_data = InstrumentData.get_instance().load_data(  # type: ignore
                "zerodha_instruments"
            )
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from cache")
        except Exception:
            instruments = self.wrapper.instruments()
            self.symbol_data = {}
            for instrument in instruments:
                exchange = instrument["exchange"]
                tradingsymbol = instrument["tradingsymbol"]
                self.symbol_data["{}:{}".format(exchange, tradingsymbol)] = instrument

            PickleUtils.save_data(self.symbol_data, "zerodha_instruments")
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from server")

    def set_username(self, username: str):
        self.username = username

    def get_username(self):
        return self.username

    def on_ticks(self, kws, ticks):
        """Callback on live ticks"""
        # logger.info("[TEST_TICK] {}".format(ticks))
        pass

    def on_order_update(self, kws, data):
        """Callback on order update"""
        Constants.logger.info("[UPDATE_RECEIVED] {}".format(data))

        if self.order_updates is None:
            raise Exception("Event Queue Not Initalised")

        self.order_updates.put(data)

    def on_connect(self, kws, response):
        """Callback on successfull connect"""
        kws.subscribe([256265])
        kws.set_mode(kws.MODE_FULL, [256265])

    def stream_order_data(self):
        kite_ticker = KiteTicker(self.wrapper.api_key, self.wrapper.access_token)
        kite_ticker.on_order_update = self.on_order_update  # type:ignore
        kite_ticker.on_ticks = self.on_ticks  # type:ignore
        kite_ticker.on_connect = self.on_connect  # type:ignore

        kite_ticker.connect(threaded=True)

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def get_ltps(self, trading_symbols) -> Dict:
        response = self.wrapper.ltp(trading_symbols)
        if not isinstance(response, dict):
            raise InvalidArgumentException(
                "Invalid data response. Zerodha sent incorrect data, Please check."
            )
        api_response: Dict[Hashable, Any] = response
        return api_response

    def get_quantplay_symbol(self, symbol: str):
        return symbol

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def ltp(self, exchange: ExchangeType, tradingsymbol: str) -> float:
        try:
            key = "{}:".format(exchange) + tradingsymbol
            response = self.wrapper.ltp([key])
            if not isinstance(response, dict):
                raise InvalidArgumentException(
                    "Invalid data response. Zerodha sent incorrect data, Please check."
                )
            api_response: Dict[Hashable, Any] = response

            if key not in api_response:
                raise InvalidArgumentException(
                    "Symbol {} not listed on exchange".format(tradingsymbol)
                )

            return api_response[key]["last_price"]
        except TokenException:
            raise QuantplayTokenException("Zerodha token expired")
        except Exception as e:
            exception_message = "GetLtp call failed for [{}] with error [{}]".format(
                tradingsymbol, str(e)
            )
            raise RetryableException(exception_message)

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def get_orders(self, status=None):
        orders = self.wrapper.orders()
        if status:
            orders = [a for a in orders if a["status"] == status]
        return orders

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def modify_order(self, order_to_modify: ModifyOrderRequest) -> str:
        order_id = order_to_modify["order_id"]

        try:
            order_to_modify["variety"] = "regular"
            if "trigger_price" not in order_to_modify:
                order_to_modify["trigger_price"] = None
            Constants.logger.info(
                "Modifying order [{}] new price [{}]".format(
                    order_to_modify["order_id"], order_to_modify["price"]
                )
            )
            response = self.wrapper.modify_order(
                order_id=order_id,
                variety=order_to_modify["variety"],
                price=order_to_modify["price"],
                trigger_price=order_to_modify["trigger_price"],
                order_type=order_to_modify["order_type"],
            )
            return response
        except Exception as e:
            exception_message = (
                "OrderModificationFailed for {} failed with exception {}".format(
                    order_to_modify["order_id"], e
                )
            )
            if (
                "Order cannot be modified as it is being processed"
                not in exception_message
            ):
                Constants.logger.error("{}".format(exception_message))
        return order_id

    def cancel_order(self, order_id: str, variety="regular"):
        self.wrapper.cancel_order(order_id=order_id, variety=variety)

    def get_ltp_by_order(self, order):
        exchange = order["exchange"]
        tradingsymbol = order["tradingsymbol"]

        return self.ltp(exchange, tradingsymbol)

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def get_positions(self):
        return self.wrapper.positions()

    # @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def place_order(
        self,
        tradingsymbol=None,
        exchange=None,
        quantity=None,
        order_type=None,
        transaction_type=None,
        tag=None,
        product=None,
        price=None,
        trigger_price=None,
    ):
        try:
            Constants.logger.info(
                f"[PLACING_ORDER] {tradingsymbol} {exchange} {quantity} {tag}"
            )
            order_id = self.wrapper.place_order(
                variety="regular",
                tradingsymbol=tradingsymbol,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity=int(abs(quantity)),
                order_type=order_type,
                disclosed_quantity=None,
                price=price,
                trigger_price=trigger_price,
                product=product,
                tag=tag,
            )
            return order_id
        except Exception as e:
            raise QuantplayOrderPlacementException(str(e))

    def validate_config(self, quantplay_config):
        if quantplay_config is None:
            return False
        if Zerodha.zerodha_api_key not in quantplay_config["DEFAULT"]:
            return False
        if Zerodha.zerodha_api_secret not in quantplay_config["DEFAULT"]:
            return False

        return True

    def generate_token(
        self,
        user_id: str | None,
        api_key: str | None,
        api_secret: str | None,
        password: str | None,
        totp: str | None,
    ):
        kite = KiteConnect(api_key=api_key)

        try:
            request_token = KiteUtils.get_request_token(
                api_key=api_key, user_id=user_id, password=password, totp=totp
            )
            response = kite.generate_session(request_token, api_secret=api_secret)
            if not isinstance(response, dict):
                raise InvalidArgumentException(
                    "Invalid data response. Zerodha sent incorrect data, Please check."
                )
            data: Dict[Hashable, Any] = response

            kite.set_access_token(data["access_token"])
        except TokenException as e:
            message = str(e)
            if "Invalid" in message and "checksum" in message:
                raise InvalidArgumentException("Invalid API secret")
            raise
        except Exception as e:
            traceback.print_exc()
            print("Need token input " + kite.login_url())
            raise e

        self.kite = kite
        self.wrapper = kite

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def invoke_kite_api(self, api_func: Callable[..., Any]) -> Dict[Hashable, Any]:
        try:
            response = api_func()
            if not isinstance(response, dict):
                raise InvalidArgumentException(
                    "Invalid data response. Zerodha sent incorrect data, Please check."
                )
            api_response: Dict[Hashable, Any] = response
            return api_response
        except TokenException:
            raise QuantplayTokenException("Token Expired")
        except Exception:
            traceback.print_exc()
            raise RetryableException("Failed to fetch user profile")

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def kite_list_response(
        self, api_func: Callable[..., Any]
    ) -> List[Dict[Hashable, Any]]:
        try:
            response = api_func()
            if not isinstance(response, List):
                raise InvalidArgumentException(
                    "Invalid orders data response. Broker sent incorrect data. Please check."
                )
            api_response: List[Dict[Hashable, Any]] = response
            return api_response
        except TokenException:
            raise QuantplayTokenException("Token Expired")
        except Exception:
            traceback.print_exc()
            raise RetryableException("Failed to fetch user profile")

    def profile(self) -> UserBrokerProfileResponse:
        user_profile = self.invoke_kite_api(self.wrapper.profile)

        data: UserBrokerProfileResponse = {
            "user_id": user_profile["user_id"],
            "full_name": user_profile["user_name"],
            "segments": user_profile["exchanges"],
            "email": user_profile["email"],
        }

        return data

    def get_token(self, instrument_token: int):
        # exchange_map = {
        #     NSE: 1,
        #     NFO: 2,
        #     NCD: 3,
        #     BSE: 4,
        #     BFO: 5,
        #     BCD: 6,
        #     MFO: 7,
        #     MCX: 8,
        #     Indices: 9,
        # }

        return instrument_token // 256

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def holdings(self):
        holdings = self.kite_list_response(self.wrapper.holdings)

        for holding in holdings:
            holding["price"] = holding.pop("last_price")

        holdings_df = pl.DataFrame(holdings)
        if len(holdings_df) == 0:
            return pl.DataFrame(schema=self.holidings_schema)

        holdings_df = holdings_df.with_columns(
            pl.Series(
                "token",
                [self.get_token(x) for x in holdings_df["instrument_token"].to_list()],
            )
        )

        holdings_df = holdings_df.with_columns(
            (pl.col("quantity") * pl.col("price")).alias("value"),
            pl.lit(0).alias("pledged_quantity"),
            (pl.col("quantity") * pl.col("average_price")).alias("buy_value"),
            (pl.col("quantity") * pl.col("price")).alias("current_value"),
            ((pl.col("price") / pl.col("average_price") - 1) * 100).alias("pct_change"),
        )

        return holdings_df[list(self.holidings_schema.keys())].cast(self.holidings_schema)

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def positions(self, drop_cnc: bool = True) -> pl.DataFrame:
        positions = self.invoke_kite_api(self.wrapper.positions)

        positions_df = pl.DataFrame(positions.get("net", {}))

        if len(positions_df) == 0:
            return pl.DataFrame(schema=self.positions_schema)

        positions_df = positions_df.with_columns(
            (pl.col("exchange") + ":" + pl.col("tradingsymbol")).alias("exchange_symbol")
        )
        symbols = (
            positions_df.select(pl.col("exchange_symbol").unique()).to_series().to_list()
        )
        symbol_ltps = self.get_ltps(symbols)
        ltp_map = {}
        for exchange_symbol in symbol_ltps:
            ltp_map[exchange_symbol] = float(symbol_ltps[exchange_symbol]["last_price"])

        positions_df = positions_df.with_columns(
            pl.col("exchange_symbol")
            .replace_strict(ltp_map, default=0.0)
            .cast(pl.Float64)
            .alias("ltp")
        )

        positions_df = positions_df.with_columns(
            (pl.col("sell_value") - pl.col("buy_value")).alias("pnl")
        )
        positions_df = positions_df.with_columns(
            (pl.col("quantity") * pl.col("ltp") + pl.col("pnl")).alias("pnl")
        )

        positions_df = positions_df.with_columns(
            pl.when(pl.col("tradingsymbol").str.slice(-2) == "PE")
            .then(pl.lit("PE"))
            .otherwise(pl.lit("CE"))
            .alias("option_type")
        )
        positions_df = positions_df.with_columns(
            pl.when(pl.col("exchange").is_in(["NFO", "BFO"]))
            .then(pl.col("option_type"))
            .otherwise(None)
            .alias("option_type")
        )

        positions_df = positions_df.with_columns(
            pl.struct(["exchange", "tradingsymbol"])
            .map_elements(
                lambda x: int(
                    self.symbol_attribute(
                        x["exchange"], x["tradingsymbol"], "exchange_token"
                    )
                ),
                return_dtype=pl.Int64,
            )
            .alias("token")
        )

        if drop_cnc:
            positions_df = positions_df.filter(pl.col("product") != "CNC")

        return positions_df[list(self.positions_schema.keys())].cast(
            self.positions_schema
        )

    def orders(self, tag=None, add_ltp: bool = True) -> pl.DataFrame:
        orders = self.kite_list_response(self.wrapper.orders)
        for order in orders:
            order["user_id"] = order.pop("placed_by")
        orders_df = pl.DataFrame(orders, schema=self.orders_schema)

        if len(orders_df) == 0:
            return orders_df

        if add_ltp:
            positions = self.positions()
            positions = positions.sort("product").group_by("tradingsymbol").head(1)

            orders_df = orders_df.drop(["ltp"])
            orders_df = orders_df.join(
                positions.select(["tradingsymbol", "ltp"]), on="tradingsymbol", how="left"
            )
        else:
            orders_df = orders_df.with_columns(pl.lit(None).cast(pl.Float64).alias("ltp"))

        orders_df = orders_df.with_columns(
            (
                pl.col("ltp") * pl.col("filled_quantity")
                - pl.col("average_price") * pl.col("filled_quantity")
            ).alias("pnl")
        )

        orders_df = orders_df.with_columns(
            pl.when(pl.col("transaction_type") == "SELL")
            .then(-pl.col("pnl"))
            .otherwise(pl.col("pnl"))
            .alias("pnl")
        )

        if tag:
            orders_df = orders_df.filter(pl.col("tag") == tag)

        orders_df = orders_df.with_columns(
            pl.struct(["exchange", "tradingsymbol"])
            .map_elements(
                lambda x: int(
                    self.symbol_attribute(
                        x["exchange"], x["tradingsymbol"], "exchange_token"
                    )
                ),
                return_dtype=pl.Int64,
            )
            .alias("token")
        )

        return orders_df[list(self.orders_schema.keys())]

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def margins(self) -> Dict[str, Any]:
        try:
            response = self.wrapper.margins()
            if not isinstance(response, dict):
                raise InvalidArgumentException(
                    "Invalid margin data response. Broker sent incorrect data. Please check."
                )
            margins: Dict[str, Any] = response
            margins = {
                "margin_used": float(margins["equity"]["utilised"]["debits"]),
                "margin_available": float(margins["equity"]["net"]),
            }
            return margins
        except TokenException as e:
            raise QuantplayTokenException(str(e))
        except Exception:
            traceback.print_exc()
            raise RetryableException("Failed to fetch margins")

    def basket_margin(self, basket_orders) -> Dict[str, Any]:
        response = self.wrapper.basket_order_margins(basket_orders, mode="compact")
        if not isinstance(response, dict):
            raise InvalidArgumentException(
                "Invalid data response. Zerodha sent incorrect data, Please check."
            )
        api_response: Dict[Hashable, Any] = response

        charges = api_response["orders"]
        return {
            "initial": api_response["initial"]["total"],
            "final": api_response["final"]["total"],
            "total_charges": sum([a["charges"]["total"] for a in charges]),
            "exchange_turnover_charge": sum(
                [a["charges"]["exchange_turnover_charge"] for a in charges]
            ),
            "brokerage": sum([a["charges"]["brokerage"] for a in charges]),
            "transaction_tax": sum([a["charges"]["transaction_tax"] for a in charges]),
            "gst": sum([a["charges"]["gst"]["total"] for a in charges]),
        }

    def account_summary(self):
        margins = self.margins()
        response = {
            "margin_used": margins["margin_used"],
            "margin_available": margins["margin_available"],
            "pnl": float(self.positions()["pnl"].sum()),
        }
        return response

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def historical_data(
        self,
        exchange: ExchangeType,
        token=None,
        tradingsymbol=None,
        interval=None,
        start_time=None,
        end_time=datetime.now(),
        days=None,
    ):
        self.validate_exchange(exchange)
        if tradingsymbol:
            tradingsymbol = self.get_symbol(tradingsymbol, exchange=exchange)
            instrument_token = self.symbol_data[f"{exchange}:{tradingsymbol}"][
                "instrument_token"
            ]
            self.validate_existance(instrument_token, "Invalid trading symbol")
        else:
            instruments = self.symbol_data.values()
            t = [
                a
                for a in instruments
                if exchange == a["exchange"] and str(token) == str(a["exchange_token"])
            ]

            if len(t) != 1:
                raise InvalidArgumentException(f"Invalid token {token}")
            instrument_token = t[0]["instrument_token"]

        if days:
            start_time = datetime.now() - timedelta(days=days)
            end_time = datetime.now()

        Constants.logger.info(
            f"[HISTORICAL_DATA] requesting {interval} candles for {instrument_token}/{tradingsymbol} from {start_time} till {end_time}"
        )
        data = self.wrapper.historical_data(
            instrument_token,
            start_time,
            end_time,
            interval,
            continuous=False,
        )
        data = pd.DataFrame(data)

        if len(data) == 0:
            return data
        data["date"] = pd.to_datetime(data["date"]).dt.tz_localize(None)  # type: ignore
        return data.sort_values("date").reset_index(drop=True)
