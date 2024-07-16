import boto3
import pandas as pd
import os
from boto3.s3.transfer import TransferConfig
from threading import Lock
from quantplay.utils.constant import Constants
from retrying import retry  # type: ignore


lock = Lock()

TransferConfig(use_threads=False)


class S3Bucket:
    quantplay_market_data = "quantplay-market-data"


class S3Utils:
    @staticmethod
    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=2,
    )
    def read_csv(bucket: str, key: str, read_from_local: bool = True) -> pd.DataFrame:
        full_path = f"/tmp/{bucket}/{key}"
        try:
            if not read_from_local:
                raise Exception("read from local is false")
            try:
                lock.acquire()
                data = pd.read_csv(full_path)  # type: ignore
                return data
            except Exception:
                Constants.logger.error("[S3_READ_FAILED] failed to read from s3")
                lock.release()
                raise

            lock.release()

        except Exception:
            print("Data not found for {}".format(key))

        print("fetching bucket from s3 {} key {}".format(bucket, key))

        client = boto3.client("s3")  # type: ignore
        raw_stream = client.get_object(Bucket=bucket, Key=key)
        content = raw_stream["Body"].read().decode("utf-8")

        print("Saving data at {}".format("/tmp/" + key))
        full_folder_path = full_path[0 : full_path.rfind("/")]
        if not os.path.exists(full_folder_path):
            os.makedirs(full_folder_path)

        text_file = open(full_path, "w")
        text_file.write(content)
        text_file.close()

        return pd.read_csv(full_path)  # type: ignore
