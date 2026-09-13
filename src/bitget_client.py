import json
import ssl
import threading
import time
from http.client import HTTPException, HTTPSConnection
from urllib.parse import urlparse, urlencode

from src.config import BASE_URL, REQUEST_SLEEP_SEC

try:
    import certifi
except ModuleNotFoundError:  # pragma: no cover - installation fallback
    certifi = None

retry_hook = None

_PARSED_BASE = urlparse(BASE_URL)
_HOST = _PARSED_BASE.hostname or "api.bitget.com"
_PORT = _PARSED_BASE.port or 443
_THREAD = threading.local()
_MAX_ATTEMPTS = 5
_TIMEOUT_SEC = 20


def create_ssl_context(tls12_only: bool = False) -> ssl.SSLContext:
    if certifi is not None:
        context = ssl.create_default_context(cafile=certifi.where())
    else:
        context = ssl.create_default_context()

    if tls12_only:
        context.maximum_version = ssl.TLSVersion.TLSv1_2

    return context


def _close_connection() -> None:
    connection = getattr(_THREAD, "connection", None)
    if connection is None:
        return

    try:
        connection.close()
    except Exception:
        pass

    _THREAD.connection = None


def _get_connection(tls12_only: bool = False) -> HTTPSConnection:
    connection = getattr(_THREAD, "connection", None)
    if connection is not None:
        return connection

    connection = HTTPSConnection(
        _HOST,
        _PORT,
        timeout=_TIMEOUT_SEC,
        context=create_ssl_context(tls12_only=tls12_only),
    )
    _THREAD.connection = connection
    return connection


def get_json(url: str, params: dict) -> dict:
    parsed = urlparse(url)
    target = f"{parsed.path}?{urlencode(params)}"
    last_error = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        if attempt == 1:
            time.sleep(REQUEST_SLEEP_SEC)
        else:
            if retry_hook is not None:
                retry_hook(attempt, last_error)
            time.sleep(min(2 ** (attempt - 2), 8))
            _close_connection()

        try:
            connection = _get_connection(tls12_only=attempt >= 3)
            connection.request(
                "GET",
                target,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "charts-downloader/1.0",
                    "Connection": "keep-alive",
                    "Host": _HOST,
                },
            )
            response = connection.getresponse()
            raw_data = response.read().decode("utf-8")
            status = response.status
        except (TimeoutError, OSError, HTTPException, ssl.SSLError) as error:
            last_error = error
            _close_connection()
            continue

        if status in {429, 500, 502, 503, 504}:
            last_error = RuntimeError(f"Bitget HTTP error {status}")
            _close_connection()
            continue

        if status == 403:
            raise RuntimeError("IP blocked or access forbidden by Bitget")

        if status != 200:
            raise RuntimeError(f"Bitget HTTP error {status}")

        data = json.loads(raw_data)

        if data.get("code") != "00000":
            raise RuntimeError(f"Bitget API error: {data}")

        return data

    raise RuntimeError(
        f"Network error while calling Bitget: {last_error}"
    ) from last_error


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
