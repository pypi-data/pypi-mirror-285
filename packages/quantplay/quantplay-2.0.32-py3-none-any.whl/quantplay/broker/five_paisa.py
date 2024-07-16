import codecs
import pickle
import traceback
from typing import Dict

import polars as pl
import pyotp
from py5paisa import FivePaisaClient
from retrying import retry  # type: ignore

from quantplay.broker.generics.broker import Broker
from quantplay.exception.exceptions import (
    BrokerException,
    InvalidArgumentException,
    QuantplayOrderPlacementException,
    RetryableException,
    TokenException,
    retry_exception,
)
from quantplay.model.broker import UserBrokerProfileResponse
from quantplay.utils.constant import Constants, OrderStatus

logger = Constants.logger


class FivePaisa(Broker):
    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def __init__(
        self,
        app_source: str | None = None,
        app_user_id: str | None = None,
        app_password: str | None = None,
        user_key: str | None = None,
        encryption_key: str | None = None,
        client_id: str | None = None,
        totp_key: str | None = None,
        pin: str | None = None,
        client=None,
        load_instrument: bool = True,
    ):
        self.broker_name = "FivePaisa_OpenAPI"
        try:
            if client:
                self.set_client(client)
            else:
                client = FivePaisaClient(
                    cred={
                        "APP_SOURCE": app_source,
                        "APP_NAME": f"5P{client_id}",
                        "USER_ID": app_user_id,
                        "USER_KEY": user_key,
                        "PASSWORD": app_password,
                        "ENCRYPTION_KEY": encryption_key,
                    }
                )
                self.user_key = user_key
                self.client: FivePaisaClient = client

                if totp_key is None:
                    raise InvalidArgumentException("TOTP Key is Missing")

                self.client.get_totp_session(client_id, pyotp.TOTP(totp_key).now(), pin)

                try:
                    self.margins()
                except TokenException:
                    raise RetryableException("Generating token again")

        except RetryableException:
            raise

        except Exception as e:
            raise e

        self.set_user_id()

        if load_instrument:
            self.load_instrument()
        super(FivePaisa, self).__init__()

    def set_client(self, serialized_client):
        self.client = pickle.loads(codecs.decode(serialized_client.encode(), "base64"))

    def set_user_id(self):
        self.user_id = self.client.client_code

    def get_client(self):
        return codecs.encode(pickle.dumps(self.client), "base64").decode()

    def load_instrument(self, file_name: str | None = None):
        super().load_instrument("5paisa_instruments")

    def handle_exception(self, e):
        if "Unauthorized" in e.reason:
            raise TokenException("Token Expired")
        raise RetryableException(e.reason)

    def set_access_token(self, access_token: str):
        self.access_token = access_token

    def get_product(self, product):
        if product == "NRML":
            return "D"
        elif product == "CNC":
            return "D"
        elif product == "MIS":
            return "I"
        return product

    def get_lot_size(self, exchange, tradingsymbol: str):
        tradingsymbol = self.get_symbol(tradingsymbol, exchange)
        return int(self.symbol_data["{}:{}".format(exchange, tradingsymbol)]["lot_size"])

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def profile(self):
        response: UserBrokerProfileResponse = {
            "user_id": self.client.client_code,
        }

        return response

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def ltp(self, exchange, tradingsymbol: str) -> float:
        tradingsymbol = self.get_symbol(tradingsymbol, exchange)
        exchange_name = self.get_exchange(exchange)
        exchange_type = self.get_exchange_type(exchange)
        token = self.symbol_attribute(exchange, tradingsymbol, "token")
        req_list_ = [
            {"Exch": exchange_name, "ExchType": exchange_type, "ScripCode": token}
        ]

        return self.client.fetch_market_feed_scrip(req_list_)["Data"][0]["LastRate"]  # type: ignore

    def add_exchange(self, data: pl.DataFrame):
        data["exchange"] = None

        return data.with_columns(
            pl.when((pl.col("Exch").eq("N")) & (pl.col("ExchType").eq("D")))
            .then(pl.lit("NFO"))
            .alias("exchange"),
            pl.when((pl.col("Exch").eq("N")) & (pl.col("ExchType").eq("C")))
            .then(pl.lit("NFO"))
            .alias("exchange"),
            pl.when((pl.col("Exch").eq("B")) & (pl.col("ExchType").eq("D")))
            .then(pl.lit("NFO"))
            .alias("exchange"),
            pl.when((pl.col("Exch").eq("B")) & (pl.col("ExchType").eq("C")))
            .then(pl.lit("NFO"))
            .alias("exchange"),
        )

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def holdings(self):
        holdings = self.client.holdings()
        if holdings is None:
            raise TokenException("5Paisa Token expired")
        if len(holdings) == 0:
            return pl.DataFrame(schema=self.holidings_schema)

        holdings = pl.from_dicts(holdings)

        holdings = holdings.rename(
            {
                "Symbol": "tradingsymbol",
                "AvgRate": "average_price",
                "CurrentPrice": "price",
                "NseCode": "token",
                "Quantity": "quantity",
                "DPQty": "pledged_quantity",
                "Exch": "exchange",
            }
        )

        holdings = holdings.with_columns(
            pl.col("exchange")
            .replace_strict({"B": "BSE", "N": "NSE"}, default=None)
            .alias("exchange"),
        ).with_columns(
            pl.lit(None).alias("isin"),
            pl.when(pl.col("exchange") == "BSE")
            .then(pl.col("BseCode"))
            .otherwise(pl.col("token"))
            .alias("token"),
            (pl.col("quantity").mul(pl.col("average_price"))).alias("buy_value"),
            (pl.col("quantity").mul(pl.col("price"))).alias("current_value"),
            (((pl.col("price") / (pl.col("average_price"))).sub(1)).mul(100)).alias(
                "pct_change"
            ),
        )

        return holdings

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def positions(self, drop_cnc: bool = True):
        positions = self.client.positions()

        if positions is None:
            raise TokenException("5Paisa Token expired")

        if len(positions) == 0:
            return pl.DataFrame(schema=self.positions_schema)

        positions = pl.from_dicts(positions)

        positions = positions.rename(
            {
                "ScripName": "tradingsymbol",
                "AvgRate": "average_price",
                "SellQty": "sell_quantity",
                "BuyQty": "buy_quantity",
                "SellValue": "sell_value",
                "BuyValue": "buy_value",
                "LTP": "ltp",
                "ScripCode": "token",
                "NetQty": "quantity",
            }
        )
        positions = positions.with_columns(
            pl.when(pl.col("CFQty").lt(0))
            .then(pl.col("sell_quantity") - pl.col("CFQty"))
            .otherwise(pl.col("sell_quantity"))
            .alias("sell_quantity"),
            pl.when(pl.col("CFQty").gt(0))
            .then(pl.col("buy_quantity") + pl.col("CFQty"))
            .otherwise(pl.col("buy_quantity"))
            .alias("buy_quantity"),
            (pl.col("buy_value").add(pl.col("CFQty").mul(pl.col("AvgCFQty")))).alias(
                "buy_value"
            ),
        ).with_columns(
            (
                (pl.col("sell_value").add(pl.col("buy_value"))).add(
                    (pl.col("buy_quantity") - pl.col("sell_quantity")) * pl.col("ltp")
                )
            ).alias("pnl"),
        )

        self.add_exchange(positions)

        positions = positions.with_columns(
            pl.when(pl.col("exchange").is_in(["NFO", "BFO"]))
            .then(pl.col("tradingsymbol").str.split(" ").list.get(-2))
            .otherwise(None)
            .alias("option_type"),
            pl.col("OrderFor")
            .replace_strict({"I": "MIS", "D": "NRML"}, default=None)
            .alias("product"),
        ).with_columns(
            pl.when(
                (pl.col("exchange").is_in(["NFO", "BFO"]))
                & (pl.col("product").ne("NRML"))
            )
            .then(pl.lit("CNC"))
            .otherwise(pl.col("product"))
            .alias("product"),
        )

        if drop_cnc:
            positions = positions.filter(pl.col("product").ne("CNC"))

        return positions

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def orders(self, tag: str | None = None, add_ltp: bool = True):
        orders = self.client.order_book()
        if orders is None:
            raise BrokerException(
                "Invalid data response. AngelOne sent incorrect data, Please check."
            )

        if len(orders) == 0:
            return pl.DataFrame(schema=self.orders_schema)

        orders = pl.from_dicts(orders)

        self.add_exchange(orders)

        orders = orders.rename(
            {
                "OrderRequesterCode": "user_id",
                "ExchOrderID": "order_id",
                "ScripCode": "token",
                "ScripName": "tradingsymbol",
                "BuySell": "transaction_type",
                "AveragePrice": "average_price",
                "Qty": "quantity",
                "Rate": "price",
                "SLTriggerRate": "trigger_price",
                "OrderStatus": "status",
                "TradedQty": "filled_quantity",
                "PendingQty": "pending_quantity",
                "BrokerOrderTime": "order_timestamp",
                "Reason": "status_message",
            }
        )

        if tag:
            orders = orders.filter(pl.col("tag") == tag)

        orders = (
            orders.with_columns(
                pl.when(pl.col("AtMarket") == "Y")
                .then(pl.lit("MARKET"))
                .otherwise(pl.lit("LIMIT"))
                .alias("order_type"),
            )
            .with_columns(
                pl.when((pl.col("order_type") == "LIMIT") & (pl.col("WithSL") == "Y"))
                .then(pl.lit("SL"))
                .otherwise(pl.col("order_type"))
                .alias("order_type"),
                pl.col("transaction_type")
                .replace_strict({"S": "SELL", "B": "BUY"}, default=None)
                .alias("transaction_type"),
                pl.when(pl.col("exchange") == "NSE")
                .then(pl.col("tradingsymbol").str.replace("-EQ", ""))
                .otherwise(pl.col("tradingsymbol"))
                .alias("tradingsymbol"),
                pl.col("status")
                .replace_strict(
                    {
                        "Pending": OrderStatus.open,
                        "Modified": OrderStatus.open,
                        "Cancelled": OrderStatus.cancelled,
                        "Fully Executed": OrderStatus.complete,
                    },
                    default=None,
                )
                .alias("status"),
                pl.col("order_timestamp").alias("update_timestamp"),
                pl.lit(None).alias("status_message_raw"),
                pl.lit("regular").alias("variety"),
                pl.col("DelvIntra")
                .replace_strict({"D": "CNC", "I": "MIS"}, default=None)
                .alias("product"),
            )
            .with_columns(
                pl.when(pl.col("status").str.to_lowercase().str.contains("rejected"))
                .then(OrderStatus.rejected)
                .otherwise(pl.col("status"))
                .alias("status"),
                pl.when(
                    pl.col("product")
                    == "CNC" & (pl.col("exchange").is_in(["NFO", "BFO"]))
                )
                .then(pl.lit("NRML"))
                .otherwise(pl.col("product"))
                .alias("product"),
            )
            .with_columns(
                pl.when((pl.col("status") == "OPEN") & (pl.col("order_type") == "SL"))
                .then(OrderStatus.trigger_pending)
                .otherwise(pl.col("status"))
                .alias("status")
            )
        )

        orders = orders.with_columns(
            (pl.col("order_timestamp").str.slice(6, 10).cast(pl.Int64) * 1000)
            .cast(pl.Datetime)
            .alias("order_timestamp")
        )
        orders = orders.with_columns(
            (pl.col("update_timestamp").str.slice(6, 10).cast(pl.Int64) * 1000)
            .cast(pl.Datetime)
            .alias("update_timestamp")
        )

        if add_ltp:
            positions = self.positions()
            positions = positions.sort("product").group_by("tradingsymbol").head(1)

            orders = orders.join(
                positions.select(["tradingsymbol", "ltp"]), on="tradingsymbol", how="left"
            )

            orders = orders.with_columns(
                (
                    (pl.col("ltp") * pl.col("filled_quantity"))
                    - (pl.col("average_price") * pl.col("filled_quantity"))
                ).alias("pnl")
            ).with_columns(
                pl.when(pl.col("transaction_type") == "SELL")
                .then(-pl.col("pnl"))
                .otherwise(pl.col("pnl"))
            )
        else:
            orders = orders.with_columns(pl.lit(None).cast(pl.Float64).alias("ltp"))

        return orders

    def get_symbol(self, symbol, exchange=None):
        if symbol not in self.quantplay_symbol_map:
            return symbol
        return self.quantplay_symbol_map[symbol]

    @staticmethod
    def is_intraday(product: str):
        if product in ["MIS"]:
            return True

        return False

    def get_exchange(self, exchange):
        return exchange[0]

    @staticmethod
    def get_exchange_type(exchange):
        if exchange in ["NSE", "BSE"]:
            return "C"
        elif exchange in ["NFO", "BFO"]:
            return "D"
        raise InvalidArgumentException(f"exchange {exchange} not supported")

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
            if trigger_price is None:
                trigger_price = 0

            product = self.get_product(product)
            tradingsymbol = self.get_symbol(tradingsymbol)

            try:
                token = self.symbol_attribute(exchange, tradingsymbol, "token")
            except Exception:
                raise InvalidArgumentException(
                    f"Invalid symbol {tradingsymbol} for exchange {exchange}"
                )

            Constants.logger.info(
                f"[PLACING_ORDER] {tradingsymbol} {transaction_type[0]} {exchange} {token} {quantity}"
            )
            response = self.client.place_order(
                OrderType=transaction_type[0],
                Exchange=self.get_exchange(exchange),
                ExchangeType=FivePaisa.get_exchange_type(exchange),
                ScripCode=token,
                Qty=quantity,
                Price=price,
                IsIntraday=FivePaisa.is_intraday(product),
                StopLossPrice=trigger_price,
            )

            logger.info(f"[PLACE_ORDER_RESPONSE] {self.broker_name} {response}")
            if response is None:
                raise QuantplayOrderPlacementException("Failed to place order on 5Paisa")

            if "Status" in response and response["Status"] == 1:
                logger.error(
                    f"[ORDER_PLACED_FAILED] {self.broker_name}-{self.user_id} {response}"
                )
                raise QuantplayOrderPlacementException(response["Message"])

            if "BrokerOrderID" in response:
                return response["BrokerOrderID"]

        except (QuantplayOrderPlacementException, InvalidArgumentException) as e:
            raise e

        except Exception as e:
            traceback.print_exc()
            logger.error(
                f"[PLACE_ORDER_FAILED] {self.broker_name} Order placement failed with error [{e}]"
            )

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def margins(self) -> Dict[str, float]:
        margins = self.client.margin()
        if margins is None:
            raise TokenException("5Paisa Token expired")
        margins = margins[0]

        margins = {
            "margin_used": margins["MarginUtilized"],
            "margin_available": margins["NetAvailableMargin"],
        }
        return margins

    def account_summary(self):
        margins = self.margins()
        response = {
            "margin_used": margins["margin_used"],
            "margin_available": margins["margin_available"],
            "pnl": float(self.positions()["pnl"].sum()),
        }
        return response

    def get_quantplay_product(self, exchange, product):
        product_map = {"D": "CNC", "I": "MIS"}
        if product in product_map:
            product = product_map[product]
        if product == "CNC" and exchange in ["NFO", "BFO"]:
            product = "NRML"

        return product
