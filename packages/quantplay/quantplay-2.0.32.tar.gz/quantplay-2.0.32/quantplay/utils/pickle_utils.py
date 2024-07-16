import pickle
from typing import Any, Dict
from threading import Lock


class PickleUtils:
    @staticmethod
    def save_data(data: Any, file_name: str):
        with open("/tmp/{}.pickle".format(file_name), "wb") as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_data(file_name: str):
        with open("/tmp/{}.pickle".format(file_name), "rb") as disk_data:
            unserialized_data = pickle.load(disk_data)

        return unserialized_data


class InstrumentData:
    __instance = None

    @staticmethod
    def get_instance():
        # TODO: Better Return Typings
        if InstrumentData.__instance is None:
            InstrumentData()

        return InstrumentData.__instance

    def __init__(self):
        if InstrumentData.__instance is not None:
            raise Exception("Instrument Data load failed")

        self.instrument_data: Dict = {}
        self.lock = Lock()

        InstrumentData.__instance = self

    def load_data(self, file_name: str):
        if file_name in self.instrument_data:
            return self.instrument_data[file_name]

        try:
            self.lock.acquire()
            with open("/tmp/{}.pickle".format(file_name), "rb") as disk_data:
                unserialized_data = pickle.load(disk_data)
            self.instrument_data[file_name] = unserialized_data
            self.lock.release()
        except Exception:
            self.lock.release()
            raise Exception(f"file [{file_name}] not found on disk")

        return self.instrument_data[file_name]
