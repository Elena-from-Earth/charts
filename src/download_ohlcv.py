import csv
from datetime import datetime, timezone
from pathlib import Path

from src.bitget_client import fetch_history_candles
from src.config import CATEGORY, LIMIT_PER_REQUEST, OUTPUT_DIR


INTERVAL_MS = {
    "1m": 60_000,
    "3m": 180_000,
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1H": 3_600_000,
    "4H": 14_400_000,
    "6H": 21_600_000,
    "12H": 43_200_000,
    "1D": 86_400_000,
}


def now_closed_candle_ms(interval: str) -> int:
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    step = INTERVAL_MS[interval]
    return (now_ms // step) * step - step


CSV_COLUMNS = [
    "time",
    "open",
    "high",
    "low",
    "close",
    "Volume",
    "volume_base",
    "datetime_utc",
]


def candle_datetime_utc(timestamp_seconds: int) -> datetime:
    return datetime.fromtimestamp(timestamp_seconds, timezone.utc)


def candles_to_rows(candles: list) -> list[dict]:
    rows_by_time = {}

    for candle in candles:
        timestamp_seconds = int(candle[0]) // 1000
        rows_by_time[timestamp_seconds] = {
            "time": timestamp_seconds,
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "Volume": float(candle[6]),
            "volume_base": float(candle[5]),
            "datetime_utc": str(candle_datetime_utc(timestamp_seconds)),
        }

    return [
        rows_by_time[timestamp_seconds]
        for timestamp_seconds in sorted(rows_by_time)
    ]

symbol = "BTCUSDT"

def download_ohlcv(
    symbol: str,
    interval: str,
    first_bar: datetime,
    last_bar: datetime,
    progress_callback=None,
) -> tuple[Path, int]:
    symbol = symbol.upper()

    start_ms = int(first_bar.replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_ms = int(last_bar.replace(tzinfo=timezone.utc).timestamp() * 1000)

    step_ms = INTERVAL_MS[interval]
    total_bars = ((end_ms - start_ms) // step_ms) + 1
    total_requests = (
        total_bars + LIMIT_PER_REQUEST - 1
    ) // LIMIT_PER_REQUEST

    cursor_ms = start_ms
    completed_requests = 0
    all_candles = []

    if progress_callback:
        progress_callback(10)

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
        completed_requests += 1

        if progress_callback:
            progress = 10 + int(
                90 * completed_requests / total_requests
            )
            progress_callback(min(progress, 100))

    rows = candles_to_rows(all_candles)

    if not rows:
        raise RuntimeError("No OHLCV data received")

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    first_time = candle_datetime_utc(rows[0]["time"])
    last_time = candle_datetime_utc(rows[-1]["time"])

    first_name = first_time.strftime(
        "%Y-%m-%d(%H-%M-%S)"
    )
    last_name = last_time.strftime(
        "%Y-%m-%d(%H-%M-%S)"
    )

    bars_k = round(len(rows) / 1000)

    filename = (
        f"{symbol}_{interval}_"
        f"{first_name}_{last_name}_{bars_k}k.csv"
    )
    output_path = Path(OUTPUT_DIR) / filename

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    if progress_callback:
        progress_callback(100)

    return output_path, len(rows)


if __name__ == "__main__":
    download_ohlcv(
        symbol="BTCUSDT",
        interval="1m",
        first_bar=datetime(2026, 6, 1, 0, 0),
        last_bar=datetime(2026, 6, 11, 23, 59),
    )
