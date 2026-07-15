from src.config import BASE_URL
from src.bitget_client import get_json


def fetch_funding_history(
    symbol: str,
    page_no: int = 1,
    page_size: int = 100,
) -> list:
    url = f"{BASE_URL}/api/v2/mix/market/history-fund-rate"

    params = {
        "symbol": symbol.upper(),
        "productType": "USDT-FUTURES",
        "pageNo": str(page_no),
        "pageSize": str(page_size),
    }

    data = get_json(url, params)
    return data.get("data", [])
