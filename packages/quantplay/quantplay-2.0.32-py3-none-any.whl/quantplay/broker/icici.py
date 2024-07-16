from breeze_connect import BreezeConnect
from datetime import datetime, timedelta
import itertools
import polars as pl

# Initialize SDK


class ICICI:
    index_map = {"FINNIFTY": "NIFFIN", "BANKNIFTY": "CNXBAN", "MIDCPNIFTY": "NIFSEL"}

    def __init__(self) -> None:
        self.breeze = BreezeConnect(api_key="33P1=&0TDx6`K1563U95!49K7j6T&802")
        self.breeze.generate_session(
            api_secret="277YlG400231P14m3fd63%9Mz1845I2m", session_token=39256896
        )

    def get_interval(interval):
        if interval == "minute":
            return "1minute"

    def historical_data(
        self,
        exchange: str,
        tradingsymbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime,
        instrument_type: str,
        strike: int,
        expiry: datetime,
    ) -> pl.DataFrame:
        if exchange == "NFO" and strike is not None:
            product = "options"
        elif exchange == "NFO":
            product = "futures"
            instrument_type = "others"

        df = []
        while start_date < end_date:
            # restriction of 1k candles only
            if interval == "1minute":
                accepted_end_time = start_date + timedelta(days=2)
            if accepted_end_time > end_date:
                accepted_end_time = end_date

            print(
                f"Querying data for {tradingsymbol}-{strike}-{expiry.date()} from {start_date} {end_date}"
            )
            data = self.breeze.get_historical_data_v2(
                interval=interval,
                from_date=start_date.isoformat()[:19] + ".000Z",
                to_date=accepted_end_time.isoformat()[:19] + ".000Z",
                stock_code=tradingsymbol,
                exchange_code=exchange,
                right=instrument_type,
                strike_price=str(strike),
                expiry_date=expiry.isoformat()[:19] + ".000Z",
                product_type=product,
            )
            data = data["Success"]

            df.append(
                pl.from_dicts(
                    data,
                    schema={
                        "datetime": pl.String,
                        "open": pl.Float32,
                        "high": pl.Float32,
                        "low": pl.Float32,
                        "close": pl.Float32,
                        "volume": pl.Int32,
                    },
                )
            )
            start_date = accepted_end_time
        data = pl.concat(df)

        return data

    def get_options_data(self):
        index = "MIDCPNIFTY"
        expiry_prefix = "24MAR"
        expiry = datetime.now().replace(
            day=26, month=3, year=2024, second=0, hour=16, microsecond=0
        )
        exchange = "NFO"

        end_date = expiry
        interval = "1minute"
        tradingsymbol = ICICI.index_map[index]
        start_date = end_date - timedelta(days=200)
        instrument_type = "put"
        strike = None

        self = ICICI()
        data = self.historical_data(
            exchange,
            tradingsymbol,
            interval,
            start_date,
            end_date,
            instrument_type,
            strike,
            expiry,
        )

        symbol_name = f"{index}{expiry_prefix}FUT"
        print(f"Final tradingsymbol is {symbol_name}")
        new_data = data.with_columns(pl.lit(symbol_name).alias("symbol"))
        new_data.write_parquet(f"~/.quantplay/NFO/FUT/minute/{symbol_name}.parquet")

    def expiry_data():
        nifty_data = pl.read_csv(
            "/Users/ashok/.quantplay/NSE_MARKET_DATA/expiry_data.csv"
        )
        nifty_data = nifty_data.filter(pl.col("symbol").eq("MIDCPNIFTY")).sort(
            "expiry_date"
        )
        
        nifty_data = nifty_data.group_by(["expiry_date"]).last()

        with pl.Config(tbl_rows=500):
            print(nifty_data.sort("expiry_date").tail(500))
