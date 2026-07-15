import csv
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import FUNDING_OUTPUT_DIR, REQUEST_SLEEP_SEC
from src.funding_client import fetch_funding_history


CSV_COLUMNS = [
    "time",
    "funding_rate",
    "datetime_utc",
]


def funding_datetime_utc(timestamp_seconds: int) -> datetime:
    return datetime.fromtimestamp(timestamp_seconds, timezone.utc)


def funding_rows_to_csv_rows(rows: list[dict]) -> list[dict]:
    rows_by_time = {}

    for row in rows:
        timestamp_seconds = int(row["fundingTime"]) // 1000
        rows_by_time[timestamp_seconds] = {
            "time": timestamp_seconds,
            "funding_rate": float(row["fundingRate"]),
            "datetime_utc": str(funding_datetime_utc(timestamp_seconds)),
        }

    return [
        rows_by_time[timestamp_seconds]
        for timestamp_seconds in sorted(rows_by_time)
    ]


def download_funding(
    symbol: str,
    max_pages: int = 100,
) -> tuple[Path, int]:
    symbol = symbol.upper()
    all_rows = []

    for page_no in range(1, max_pages + 1):
        rows = fetch_funding_history(
            symbol=symbol,
            page_no=page_no,
            page_size=100,
        )

        if not rows:
            break

        all_rows.extend(rows)
        time.sleep(REQUEST_SLEEP_SEC)

        if len(rows) < 100:
            break

    if not all_rows:
        raise RuntimeError("No funding data received")

    csv_rows = funding_rows_to_csv_rows(all_rows)

    output_dir = Path(FUNDING_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    first_time = funding_datetime_utc(csv_rows[0]["time"]).strftime(
        "%Y-%m-%d(%H-%M-%S)"
    )
    last_time = funding_datetime_utc(csv_rows[-1]["time"]).strftime(
        "%Y-%m-%d(%H-%M-%S)"
    )

    filename = (
        f"Funding_{symbol}_{first_time}_{last_time}.csv"
    )

    output_path = output_dir / filename
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(csv_rows)

    return output_path, len(csv_rows)


if __name__ == "__main__":
    symbol = input("Enter symbol: ").strip().upper()
    if not symbol:
        raise RuntimeError("Symbol is required")

    path, rows = download_funding(symbol)
    print(f"OK: saved {rows} rows to {path}")
