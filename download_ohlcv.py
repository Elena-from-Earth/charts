from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.bitget_client import fetch_history_candles
from src.config import CATEGORY, INTERVAL, LIMIT_PER_REQUEST, OUTPUT_DIR


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

def download_ohlcv(
    symbol: str,
    interval: str,
    first_bar: datetime,
    last_bar: datetime,
) -> tuple[Path, int]:
    symbol = symbol.upper()

    start_ms = int(first_bar.replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_ms = int(last_bar.replace(tzinfo=timezone.utc).timestamp() * 1000)

    step_ms = INTERVAL_MS[interval]
    cursor_ms = start_ms
    all_candles = []

    while cursor_ms <= end_ms:
        chunk_last_ms = min(
            cursor_ms + (LIMIT_PER_REQUEST - 1) * step_ms,
            end_ms,
        )

        candles = fetch_history_candles(
            category=CATEGORY,
            symbol=symbol,
            interval=interval,
            start_time_ms=cursor_ms - step_ms,
            end_time_ms=chunk_last_ms + step_ms,
            limit=LIMIT_PER_REQUEST,
        )

        all_candles.extend(
            candle
            for candle in candles
            if cursor_ms <= int(candle[0]) <= chunk_last_ms
        )

        cursor_ms = chunk_last_ms + step_ms

    df = candles_to_dataframe(all_candles)

    df = (
        df.drop_duplicates(subset=["time"])
        .sort_values("time")
        .reset_index(drop=True)
    )

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    first_name = df["datetime_utc"].iloc[0].strftime("%Y-%m-%d(%H-%M-%S)")
    last_name = df["datetime_utc"].iloc[-1].strftime("%Y-%m-%d(%H-%M-%S)")

    filename = f"Chart-0_{symbol}_{interval}_{first_name}_{last_name}.csv"
    output_path = Path(OUTPUT_DIR) / filename

    df.to_csv(output_path, index=False, mode="w")

    return output_path, len(df)


if __name__ == "__main__":
    download_ohlcv(
        symbol="BTCUSDT",
        interval="1m",
        first_bar=datetime(2026, 6, 1, 0, 0),
        last_bar=datetime(2026, 6, 11, 23, 59),
    )