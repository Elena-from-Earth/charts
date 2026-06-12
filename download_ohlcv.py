from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.bitget_client import fetch_history_candles
from src.config import CATEGORY, INTERVAL, OUTPUT_DIR


INTERVAL_MS = {
    "1m": 60_000,
}


def now_closed_candle_ms(interval: str) -> int:
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    step = INTERVAL_MS[interval]
    return (now_ms // step) * step - step


def candles_to_dataframe(candles: list) -> pd.DataFrame:
    df = pd.DataFrame(
        candles,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume_base",
            "Volume",
        ],
    )

    df["time"] = df["time"].astype("int64")
    df["datetime_utc"] = pd.to_datetime(df["time"], unit="ms", utc=True)

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "Volume",
        "volume_base",
    ]

    for column in numeric_columns:
        df[column] = df[column].astype(float)

    return df[
        [
            "time",
            "open",
            "high",
            "low",
            "close",
            "Volume",
            "volume_base",
            "datetime_utc",
        ]
    ]


symbol = "BTCUSDT"

end_ms = now_closed_candle_ms(INTERVAL)
start_ms = end_ms - 10 * INTERVAL_MS[INTERVAL]

candles = fetch_history_candles(
    category=CATEGORY,
    symbol=symbol,
    interval=INTERVAL,
    start_time_ms=start_ms,
    end_time_ms=end_ms,
    limit=10,
)

df = candles_to_dataframe(candles)

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

first_bar = df["datetime_utc"].iloc[0].strftime("%Y-%m-%d(%H-%M-%S)")
last_bar = df["datetime_utc"].iloc[-1].strftime("%Y-%m-%d(%H-%M-%S)")

filename = f"Chart-0_{symbol}_{INTERVAL}_{first_bar}_{last_bar}.csv"
output_path = Path(OUTPUT_DIR) / filename

df.to_csv(output_path, index=False, mode="w")

print(f"OK: saved {len(df)} rows to {output_path}")