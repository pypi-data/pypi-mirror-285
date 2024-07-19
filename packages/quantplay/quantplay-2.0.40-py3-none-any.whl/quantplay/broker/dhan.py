import codecs
import pickle
import traceback
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Hashable, List

import pandas as pd
import polars as pl
from kiteconnect import KiteConnect, KiteTicker  # type: ignore
from kiteconnect.exceptions import TokenException  # type: ignore
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
from quantplay.model.generics import (
    DhanTypes,
    NorenTypes,
    OrderTypeType,
    ProductType,
    TransactionType,
)
from quantplay.utils.constant import Constants, OrderType
from quantplay.utils.pickle_utils import InstrumentData, PickleUtils
from dhanhq import dhanhq


class Dhan(Broker):
    def __init__(self):
        self.dhan = dhanhq(
            client_id="1102866282",
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzIzODgxNjgxLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMjg2NjI4MiJ9.0dNR4gOdIQ3KeaAokEwbRt6v_6ESn73r6yOL9-7lzphVCAmP-pahgK6OIOxVUExBJa0SaxX0TNX7Vk0RBQ-lxQ",
        )
        self.dhan_w = dhanhq(
            client_id="1100799116",
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzIxMzc3ODM5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDc5OTExNiJ9.ykd4NYsnl7s1UegkUUY9tbP4OxxjqtskGi8JK0lyC9bRRPQRyxDv022JyDIl6crdFsQXfG7-6BsipPYxOtLR8g",
        )

        super(Dhan, self).__init__()

    def set_wrapper(self, serialized_wrapper: str):
        self.wrapper = pickle.loads(codecs.decode(serialized_wrapper.encode(), "base64"))

    def initialize_symbol_data(self, save_as: str | None = None) -> None:
        try:
            self.symbol_data = InstrumentData.get_instance().load_data(  # type: ignore
                "zerodha_instruments"
            )
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from cache")
        except Exception:
            instruments = self.wrapper.instruments()  # type: ignore
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

    def on_ticks(self, kws: KiteTicker, ticks: Any):
        """Callback on live ticks"""
        # logger.info("[TEST_TICK] {}".format(ticks))
        pass

    def on_order_update(self, kws: KiteTicker, data: Any):
        """Callback on order update"""
        Constants.logger.info(f"[UPDATE_RECEIVED] {data}")

        if self.order_updates is None:
            raise Exception("Event Queue Not Initalised")

        self.order_updates.put(data)

    def on_connect(self, kws: KiteTicker, response: Any):
        """Callback on successfull connect"""
        kws.subscribe([256265])  # type: ignore
        kws.set_mode(kws.MODE_FULL, [256265])  # type: ignore

    def stream_order_data(self):
        kite_ticker = KiteTicker(self.wrapper.api_key, self.wrapper.access_token)
        kite_ticker.on_order_update = self.on_order_update  # type:ignore
        kite_ticker.on_ticks = self.on_ticks  # type:ignore
        kite_ticker.on_connect = self.on_connect  # type:ignore

        kite_ticker.connect(threaded=True)  # type: ignore

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def get_ltps(self, trading_symbols: List[str]):
        response = self.wrapper.ltp(trading_symbols)  # type: ignore
        if not isinstance(response, dict):
            raise InvalidArgumentException(
                "Invalid data response. Zerodha sent incorrect data, Please check."
            )
        api_response: Dict[str, Any] = response
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
            key = f"{exchange}:{tradingsymbol}"
            response = self.wrapper.ltp([key])  # type: ignore
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
    def modify_order(self, order: Any) -> str:
        # TODO
        order_id = order["order_id"]

        try:
            order["variety"] = "regular"
            if "trigger_price" not in order:
                order["trigger_price"] = None
            Constants.logger.info(
                "Modifying order [{}] new price [{}]".format(
                    order["order_id"], order["price"]
                )
            )
            response = self.wrapper.modify_order(  # type: ignore
                order_id=order_id,
                variety=order["variety"],
                price=order["price"],
                trigger_price=order["trigger_price"],
                order_type=order["order_type"],
            )
            return response
        except Exception as e:
            exception_message = (
                "OrderModificationFailed for {} failed with exception {}".format(
                    order["order_id"], e
                )
            )
            if (
                "Order cannot be modified as it is being processed"
                not in exception_message
            ):
                Constants.logger.error("{}".format(exception_message))
        return order_id

    def cancel_order(self, order_id: str, variety: str | None = "regular"):
        self.wrapper.cancel_order(order_id=order_id, variety=variety)  # type: ignore

    def get_order_type(self, order_type: OrderTypeType) -> DhanTypes.OrderTypeType:
        if order_type == OrderType.market:
            return dhanhq.MARKET

        elif order_type == OrderType.sl:
            return dhanhq.SL

        elif order_type == OrderType.slm:
            return dhanhq.SLM

        elif order_type == OrderType.limit:
            return dhanhq.LIMIT

        return order_type

    def get_exchange_segment(self, exchange: ExchangeType):
        if exchange == "NSE":
            return dhanhq.NSE
        elif exchange == "NFO":
            return dhanhq.NSE_FNO
        elif exchange == "BSE":
            return dhanhq.BSE
        elif exchange == "BFO":
            return dhanhq.BSE_FNO
        raise InvalidArgumentException(f"Exchange {exchange} is not supported")

    def get_product(self, product: ProductType) -> DhanTypes.ProductType:
        if product == "NRML":
            return dhanhq.CNC
        elif product == "CNC":
            return dhanhq.CNC
        elif product == "MIS":
            return dhanhq.INTRA

        raise InvalidArgumentException(f"Product {product} not supported for trading")

    # @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def place_order(
        self,
        tradingsymbol: str,
        exchange: ExchangeType,
        quantity: int,
        order_type: OrderTypeType,
        transaction_type: TransactionType,
        tag: str | None,
        product: ProductType,
        price: float,
        trigger_price: float | None = None,
    ) -> str | None:
        try:
            Constants.logger.info(
                f"[PLACING_ORDER] {tradingsymbol} {exchange} {quantity} {tag}"
            )
            order_id = self.dhan.place_order(
                security_id="1333",  # hdfcbank
                exchange_segment=self.get_exchange_segment(exchange),
                transaction_type=transaction_type,
                quantity=quantity,
                order_type=self.get_order_type(order_type),
                product_type=self.get_product(product),
                price=price,
            )

            return order_id
        except Exception as e:
            raise QuantplayOrderPlacementException(str(e))

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def holdings(self):
        holdings = self.dhan_w.get_holdings()

        if not isinstance(holdings["data"], list):
            return pl.DataFrame(schema=self.holidings_schema)

        holdings_df = pl.DataFrame(holdings["data"])
        if len(holdings_df) == 0:
            return pl.DataFrame(schema=self.holidings_schema)

        holdings_df = holdings_df.with_columns(
            pl.col("securityId").alias("token"),
            pl.col("avgCostPrice").alias("average_price"),
            pl.col("totalQty").alias("quantity"),
            pl.col("tradingSymbol").alias("tradingsymbol"),
            pl.lit(0).alias("price"),
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
        positions = self.dhan_w.get_positions()

        positions_df = pl.DataFrame(positions.get("data", {}))

        if len(positions_df) == 0:
            return pl.DataFrame(schema=self.positions_schema)
        positions_df = positions_df.rename(
            {
                "tradingSymbol": "tradingsymbol",
                "securityId": "token",
                "exchangeSegment": "exchange",
                "productType": "product",
                "buyQty": "buy_quantity",
                "sellQty": "sell_quantity",
                "netQty": "quantity",
                "drvOptionType": "option_type",
            }
        )

        positions_df = positions_df.with_columns()

        positions_df = positions_df.with_columns(
            pl.lit(0.0).alias("ltp"),
            (pl.col("realizedProfit") + pl.col("unrealizedProfit")).alias("pnl"),
            (pl.col("carryForwardBuyValue") + pl.col("dayBuyValue")).alias("buy_value"),
            (pl.col("carryForwardSellValue") + pl.col("daySellValue")).alias(
                "sell_value"
            ),
        )

        positions_df = positions_df.with_columns(
            ((pl.col("buy_value") - pl.col("sell_value")) / pl.col("quantity")).alias(
                "average_price"
            )
        )
        positions_df = positions_df.with_columns(
            pl.when(pl.col("quantity") == 0)
            .then(0)
            .otherwise(pl.col("average_price"))
            .alias("average_price")
        )

        positions_df = positions_df.with_columns(
            pl.when(pl.col("product") == "INTRADAY").then(pl.lit("MIS")).alias("product"),
            pl.when(pl.col("exchange") == "NSE_FNO")
            .then(pl.lit("NFO"))
            .when(pl.col("exchange") == "BSE_FO")
            .then(pl.lit("BFO"))
            .when(pl.col("exchange") == "NSE_EQ")
            .then(pl.lit("NSE"))
            .when(pl.col("exchange") == "BSE_EQ")
            .then(pl.lit("BSE"))
            .alias("exchange"),
            pl.when(pl.col("option_type") == "PUT")
            .then(pl.lit("PE"))
            .when(pl.col("option_type") == "CALL")
            .then(pl.lit("CE"))
            .alias("option_type"),
        )

        if drop_cnc:
            positions_df = positions_df.filter(pl.col("product") != "CNC")

        return positions_df[list(self.positions_schema.keys())].cast(
            self.positions_schema
        )

    def orders(self, tag: str | None = None, add_ltp: bool = True) -> pl.DataFrame:
        orders = self.invoke_dhan_api(self.dhan.get_order_list)

        if not orders or "data" not in orders or not isinstance(orders["data"], list):
            return pl.DataFrame(schema=self.orders_schema)

        orders_df = pl.DataFrame(orders["data"])
        if len(orders_df) == 0:
            return pl.DataFrame(schema=self.orders_schema)

        orders_df = orders_df.rename(
            {
                "dhanClientId": "user_id",
                "orderId": "order_id",
                "securityId": "token",
                "tradingSymbol": "tradingsymbol",
                "orderStatus": "status",
                "transactionType": "transaction_type",
                "exchangeSegment": "exchange",
                "productType": "product",
                "filled_qty": "filled_quantity",
                "triggerPrice": "trigger_price",
                "orderType": "order_type",
            }
        )

        orders_df = orders_df.with_columns(
            pl.when(pl.col("product") == "INTRADAY").then(pl.lit("MIS")).alias("product"),
            pl.when(pl.col("exchange") == "NSE_FNO")
            .then(pl.lit("NFO"))
            .when(pl.col("exchange") == "BSE_FO")
            .then(pl.lit("BFO"))
            .when(pl.col("exchange") == "NSE_EQ")
            .then(pl.lit("NSE"))
            .when(pl.col("exchange") == "BSE_EQ")
            .then(pl.lit("BSE"))
            .alias("exchange"),
            pl.when(pl.col("order_type") == "STOP_LOSS_MARKET")
            .then(pl.lit("SL-M"))
            .when(pl.col("order_type") == "STOP_LOSS")
            .then(pl.lit("SL"))
            .alias("order_type"),
            pl.when(pl.col("status") == "TRADED")
            .then(pl.lit("COMPLETE"))
            .alias("status"),
        )

        orders_df = orders_df.with_columns(
            pl.lit(None).cast(pl.Float64).alias("ltp"),
            pl.lit(0.0).alias("average_price"),
            pl.lit(0).alias("pending_quantity"),
            pl.lit("regular").alias("variety"),
            pl.col("omsErrorDescription").alias("status_message"),
            pl.col("omsErrorDescription").alias("status_message_raw"),
        )

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
        if "tag" not in orders_df.columns:
            orders_df = orders_df.with_columns(pl.lit(None).alias("tag"))

        orders_df = orders_df.with_columns(
            pl.col("createTime")
            .str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
            .alias("order_timestamp"),
            pl.col("updateTime")
            .str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
            .alias("update_timestamp"),
        )

        if tag:
            orders_df = orders_df.filter(pl.col("tag") == tag)

        return orders_df[list(self.orders_schema.keys())]

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def invoke_dhan_api(self, fn: Any, *args: Any, **kwargs: Any) -> Any | None:
        try:
            response = fn(*args, **kwargs)
            return response
        except Exception:
            traceback.print_exc()
            raise RetryableException("Failed to Receive Data from broker. Retrying Again")

    def margins(self) -> Dict[str, Any]:
        response = self.invoke_dhan_api(self.dhan.get_fund_limits)
        if response:
            margins = {
                "margin_used": float(response["data"]["utilizedAmount"]),
                "margin_available": float(response["data"]["availabelBalance"]),
            }

            return margins
        return {}
