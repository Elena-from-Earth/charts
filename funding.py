import time
from pathlib import Path

import pandas as pd

from src.config import FUNDING_OUTPUT_DIR, REQUEST_SLEEP_SEC
from src.funding_client import fetch_funding_history


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

    df = pd.DataFrame(all_rows)

    df["fundingTime"] = df["fundingTime"].astype("int64")
    df["fundingRate"] = df["fundingRate"].astype(float)
    df["time"] = df["fundingTime"] // 1000
    df["datetime_utc"] = pd.to_datetime(
        df["time"],
        unit="s",
        utc=True,
    )

    df = (
        df.rename(
            columns={
                "fundingRate": "funding_rate",
            }
        )
        .drop(columns=["fundingTime"])
        .drop_duplicates(subset=["time"])
        .sort_values("time")
        .reset_index(drop=True)
    )

    df = df[
        [
            "time",
            "funding_rate",
            "datetime_utc",
        ]
    ]

    output_dir = Path(FUNDING_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    first_time = df["datetime_utc"].iloc[0].strftime(
        "%Y-%m-%d(%H-%M-%S)"
    )
    last_time = df["datetime_utc"].iloc[-1].strftime(
        "%Y-%m-%d(%H-%M-%S)"
    )

    filename = (
        f"Funding_{symbol}_{first_time}_{last_time}.csv"
    )

    output_path = output_dir / filename
    df.to_csv(output_path, index=False, mode="w")

    return output_path, len(df)


if __name__ == "__main__":
    symbol = input("Enter symbol: ").strip().upper()
    if not symbol:
        raise RuntimeError("Symbol is required")

    path, rows = download_funding(symbol)
    print(f"OK: saved {rows} rows to {path}")
