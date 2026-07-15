from src.download_funding import download_funding


if __name__ == "__main__":
    symbol = input("Enter symbol: ").strip().upper()
    if not symbol:
        raise RuntimeError("Symbol is required")

    path, rows = download_funding(symbol)
    print(f"OK: saved {rows} rows to {path}")
