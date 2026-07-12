# src/config.py

BASE_URL = "https://api.bitget.com"

CATEGORY = "USDT-FUTURES"
INTERVAL = "1m"
LIMIT_PER_REQUEST = 100

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
]

OUTPUT_DIR = "data/ohlcv"
FUNDING_OUTPUT_DIR = "data/funding"

REQUEST_SLEEP_SEC = 0.3
