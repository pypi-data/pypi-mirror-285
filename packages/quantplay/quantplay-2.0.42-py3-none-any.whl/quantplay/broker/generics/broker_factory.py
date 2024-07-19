import os
import traceback
from dataclasses import dataclass
from typing import Any, Dict

from quantplay.broker.aliceblue import Aliceblue
from quantplay.broker.angelone import AngelOne

from quantplay.broker.five_paisa import FivePaisa
from quantplay.broker.flattrade import FlatTrade
from quantplay.broker.iifl_xts import IIFL as IIFL_XTS
from quantplay.broker.motilal import Motilal
from quantplay.broker.shoonya import FinvAsia
from quantplay.broker.upstox import Upstox
from quantplay.broker.zerodha import Zerodha
from quantplay.exception.exceptions import InvalidArgumentException

from quantplay.utils.pickle_utils import PickleUtils
from quantplay.utils.caching import InstrumentCache

BrokerType = (
    Aliceblue
    | AngelOne
    | FlatTrade
    | Motilal
    | FinvAsia
    | Upstox
    | Zerodha
    | IIFL_XTS
    | FivePaisa
)

instrument_cache = InstrumentCache()


@dataclass
class Broker:
    ZERODHA = "Zerodha"
    UPSTOX = "Upstox"
    ALICEBLUE = "Aliceblue"
    FIVEPAISA_OPENAPI = "5Paisa_OpenAPI"
    FINVASIA = "Finvasia"
    FLATTRADE = "Flattrade"
    IIFL_XTS = "IIFL_XTS"
    MOTILAL = "Motilal"
    ANGELONE = "Angelone"


class BrokerFactory:
    broker_instruments_map = {
        Broker.ZERODHA: "zerodha_instruments",
        Broker.FINVASIA: "shoonya_instruments",
        Broker.FLATTRADE: "shoonya_instruments",
        Broker.IIFL_XTS: "xts_instruments",
        Broker.MOTILAL: "motilal_instruments",
        Broker.ANGELONE: "angelone_instruments",
        Broker.ALICEBLUE: "aliceblue_instruments",
        Broker.UPSTOX: "upstox_instruments",
        Broker.FIVEPAISA_OPENAPI: "5paisa_instruments",
    }

    def __init__(self):
        self.client_broker_data: Dict[str, BrokerType] = {}

    def get_broker_key(self, username: str, broker_name: str) -> str:
        return "{}:{}".format(username, broker_name)

    def set_broker_instruments(self, broker_name: str, broker: BrokerType) -> None:
        symbol_data_key = f"{broker_name}_instruments"
        quantplay_symbol_key = f"{broker_name}_qplay_symbols"
        broker_symbol_key = f"{broker_name}_broker_symbols"

        symbol_data = instrument_cache.get(symbol_data_key)
        quantplay_symbol_map = instrument_cache.get(quantplay_symbol_key)
        broker_symbol_map = instrument_cache.get(broker_symbol_key)

        if symbol_data is not None:
            broker.symbol_data = symbol_data

            if broker_name != "Zerodha":
                if quantplay_symbol_map is not None and broker_symbol_map is not None:
                    broker.quantplay_symbol_map = quantplay_symbol_map
                    broker.broker_symbol_map = broker_symbol_map

                else:
                    broker.initialize_broker_symbol_map()
                    instrument_cache.set(
                        quantplay_symbol_key, broker.quantplay_symbol_map
                    )
                    instrument_cache.set(broker_symbol_key, broker.broker_symbol_map)

            return

        try:
            symbol_data = PickleUtils.load_data(
                BrokerFactory.broker_instruments_map[broker_name]
            )
            broker.symbol_data = symbol_data

            if broker_name != "Zerodha":
                broker.initialize_broker_symbol_map()
                instrument_cache.set(quantplay_symbol_key, broker.quantplay_symbol_map)

            instrument_cache.set(symbol_data_key, symbol_data)

        except Exception:
            traceback.print_exc()

            if broker_name != "Zerodha":
                broker.load_instrument(BrokerFactory.broker_instruments_map[broker_name])
            else:
                broker.initialize_symbol_data()

    def store_broker_client(
        self, broker_info: Dict[str, Any], load_instrument: bool = True
    ) -> None:
        username = broker_info["username"]
        nickname = broker_info["nickname"]

        broker_key = self.get_broker_key(username, nickname)

        broker_data = broker_info["broker_data"]
        broker = broker_info["broker"]

        broker_client: BrokerType | None = None

        if broker == "Motilal":
            motial_headers = broker_data["headers"]
            broker_client = Motilal(
                headers=motial_headers, load_instrument=load_instrument
            )

        elif broker == "Zerodha":
            broker_client = Zerodha(
                wrapper=broker_data["zerodha_wrapper"],
                load_instrument=load_instrument,
            )

        elif broker == "Angelone":
            broker_client = AngelOne(
                user_id=broker_data["user_id"],
                api_key=broker_data["api_key"],
                access_token=broker_data["access_token"],
                refresh_token=broker_data["refresh_token"],
                feed_token=broker_data["feed_token"],
                load_instrument=load_instrument,
            )

        elif broker == Broker.ALICEBLUE:
            broker_client = Aliceblue(client=broker_data["client"])

        elif broker == Broker.UPSTOX:
            broker_client = Upstox(
                access_token=broker_data["access_token"],
                user_id=broker_data["user_id"],
            )

        elif broker == Broker.FINVASIA:
            finvasia_data = broker_data
            broker_client = FinvAsia(
                order_updates=None,
                user_id=finvasia_data["user_id"],
                password=finvasia_data["password"],
                user_token=finvasia_data["user_token"],
                load_instrument=load_instrument,
            )

        elif broker == Broker.FLATTRADE:
            flattrade_data = broker_data
            broker_client = FlatTrade(
                order_updates=None,
                user_id=flattrade_data["user_id"],
                password=flattrade_data["password"],
                user_token=flattrade_data["user_token"],
                load_instrument=load_instrument,
            )

        elif broker == Broker.FIVEPAISA_OPENAPI:
            broker_client = FivePaisa(
                client=broker_data["client"],
                load_instrument=load_instrument,
            )

            self.client_broker_data[broker_key] = broker_client

        elif broker == Broker.IIFL_XTS:
            iifl_xts_data = broker_data
            broker_client = IIFL_XTS(
                wrapper=broker_data["wrapper"],
                md_wrapper=broker_data["md_wrapper"],
                client_id=iifl_xts_data["user_id"],
                load_instrument=load_instrument,
            )

        else:
            raise InvalidArgumentException(f"Broker {broker} not supported")

        self.client_broker_data[broker_key] = broker_client
        self.set_broker_instruments(broker_name=broker, broker=broker_client)

    def get_broker_client(self, broker_info: Dict[str, Any]) -> BrokerType:
        username = broker_info["username"]
        nickname = broker_info["nickname"]

        broker_key = self.get_broker_key(username, nickname)

        if broker_key in self.client_broker_data:
            return self.client_broker_data[broker_key]

        self.store_broker_client(broker_info, load_instrument=False)

        if broker_key in self.client_broker_data:
            return self.client_broker_data[broker_key]
        else:
            raise InvalidArgumentException("Invalid broker API configuration")

    def clear_instrument_cache(self, broker: str) -> None:
        symbol_data_key = f"{broker}_instruments"
        instrument_cache.delete(symbol_data_key)

        file_name = self.broker_instruments_map[broker]
        os.system(f"rm /tmp/{file_name}*")
