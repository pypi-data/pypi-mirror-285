import unittest

from quantplay.wrapper.aws.s3 import S3Utils


class S3Validation(unittest.TestCase):
    def test_cache_enabled(self):
        self.assertEqual(S3Utils.is_cache_enabled, True)

    def test_instrument_data(self):
        df = S3Utils.read_csv(
            "quantplay-market-data", "symbol_data/shoonya_instruments.csv"
        )

        actual_unique_exchanges = set(df.exchange.unique())
        expected_unique_exchanges = {"BSE", "NSE", "BFO", "NFO"}
        self.assertEqual(actual_unique_exchanges, expected_unique_exchanges)


if __name__ == "__main__":
    unittest.main()
