from pathlib import Path


# src/config.py

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASE_URL = "https://api.bitget.com"

CATEGORY = "USDT-FUTURES"
INTERVAL = "1m"
LIMIT_PER_REQUEST = 100

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
]

OUTPUT_DIR = PROJECT_ROOT / "data" / "ohlcv"
CONTRACTS_OUTPUT_DIR = PROJECT_ROOT / "data" / "contracts"
FUNDING_OUTPUT_DIR = PROJECT_ROOT / "data" / "funding"

REQUEST_SLEEP_SEC = 0.3
