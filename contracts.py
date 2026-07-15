import json
from pathlib import Path

from src.bitget_client import get_json
from src.config import BASE_URL, CATEGORY, CONTRACTS_OUTPUT_DIR


def fetch_contract(symbol: str) -> dict:
    symbol = symbol.strip().upper()

    if not symbol:
        raise ValueError("Symbol is required")

    if "/" in symbol or "\\" in symbol:
        raise ValueError("Symbol must not contain path separators")

    url = f"{BASE_URL}/api/v2/mix/market/contracts"
    params = {
        "productType": CATEGORY,
        "symbol": symbol,
    }

    return get_json(url, params)


def save_contract(symbol: str, data: dict) -> Path:
    output_dir = Path(CONTRACTS_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{symbol}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

    return output_path


def main() -> None:
    symbol = input("Enter symbol: ").strip().upper()
    data = fetch_contract(symbol)
    output_path = save_contract(symbol, data)

    print(f"OK: saved contract data to {output_path}")


if __name__ == "__main__":
    main()
