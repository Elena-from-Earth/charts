import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.config import BASE_URL, REQUEST_SLEEP_SEC


def get_json(url: str, params: dict) -> dict:
    time.sleep(REQUEST_SLEEP_SEC)

    request_url = f"{url}?{urlencode(params)}"
    request = Request(
        request_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "charts-downloader/1.0",
        },
    )

    try:
        with urlopen(request, timeout=20) as response:
            raw_data = response.read().decode("utf-8")
    except HTTPError as error:
        if error.code == 403:
            raise RuntimeError("IP blocked or access forbidden by Bitget") from error

        if error.code == 429:
            raise RuntimeError(
                "Bitget rate limit exceeded. IP may be temporarily restricted"
            ) from error

        raise RuntimeError(f"Bitget HTTP error {error.code}: {error.reason}") from error
    except URLError as error:
        raise RuntimeError(f"Network error while calling Bitget: {error.reason}") from error

    data = json.loads(raw_data)

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
