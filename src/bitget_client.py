# src/bitget_client.py

import time
import requests

from src.config import BASE_URL, REQUEST_SLEEP_SEC


def get_json(url: str, params: dict) -> dict:
    time.sleep(REQUEST_SLEEP_SEC)

    response = requests.get(url, params=params, timeout=20)

    if response.status_code == 429:
        raise RuntimeError("Rate limit: HTTP 429 Too Many Requests")

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "00000":
        raise RuntimeError(f"Bitget API error: {data}")

    return data


def fetch_history_candles(
    category: str,
    symbol: str,
    interval: str,
    start_time_ms: int,
    end_time_ms: int,
    limit: int = 1000,
) -> list:
    url = f"{BASE_URL}/api/v3/market/history-candles"

    params = {
        "category": category,
        "symbol": symbol,
        "interval": interval,
        "type": "MARKET",
        "startTime": str(start_time_ms),
        "endTime": str(end_time_ms),
        "limit": str(limit),
    }

    data = get_json(url, params)
    return data.get("data", [])