import requests

from src.config import BASE_URL


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

    response = requests.get(url, params=params, timeout=20)

    if response.status_code == 403:
        raise RuntimeError("IP blocked or access forbidden by Bitget")

    if response.status_code == 429:
        raise RuntimeError("Bitget rate limit exceeded")

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "00000":
        raise RuntimeError(f"Bitget API error: {data}")

    return data.get("data", [])