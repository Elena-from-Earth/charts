import math
import threading
import tkinter as tk
from datetime import datetime, timedelta, timezone
from tkinter import ttk

from download_ohlcv import download_ohlcv

from src.config import LIMIT_PER_REQUEST, REQUEST_SLEEP_SEC


DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

TIMEFRAME_SECONDS = {
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1H": 3600,
    "4H": 14400,
    "6H": 21600,
    "12H": 43200,
    "1D": 86400,
}


def update_estimate(*args) -> None:
    try:
        first_bar = datetime.strptime(first_bar_var.get(), DATE_FORMAT)
        last_bar = datetime.strptime(last_bar_var.get(), DATE_FORMAT)
        timeframe = timeframe_var.get()

        if last_bar < first_bar:
            raise ValueError

        timeframe_seconds = TIMEFRAME_SECONDS[timeframe]
        range_seconds = (last_bar - first_bar).total_seconds()

        bars = int(range_seconds // timeframe_seconds) + 1
        requests_count = math.ceil(bars / LIMIT_PER_REQUEST)

        requests_per_second = 1 / REQUEST_SLEEP_SEC
        estimated_seconds = requests_count * REQUEST_SLEEP_SEC

        if estimated_seconds < 60:
            estimated_time = f"{estimated_seconds:.1f} seconds"
        elif estimated_seconds < 3600:
            estimated_time = f"{estimated_seconds / 60:.1f} minutes"
        elif estimated_seconds < 86400:
            estimated_time = f"{estimated_seconds / 3600:.1f} hours"
        else:
            estimated_time = f"{estimated_seconds / 86400:.1f} days"

        estimate_var.set(
            f"Bars: {bars:,}\n"
            f"Requests: {requests_count:,}\n"
            f"Speed: {requests_per_second:.2f} req/s\n"
            f"Estimated time: {estimated_time}"
        )

    except (ValueError, KeyError):
        estimate_var.set("Enter valid dates")


def submit() -> None:
    try:
        symbol = symbol_var.get().strip().upper()
        timeframe = timeframe_var.get()

        first_bar = datetime.strptime(
            first_bar_var.get(),
            DATE_FORMAT,
        )

        last_bar = datetime.strptime(
            last_bar_var.get(),
            DATE_FORMAT,
        )

        if last_bar < first_bar:
            raise ValueError

    except ValueError:
        status_var.set("Error: invalid dates")
        return

    status_var.set("Downloading...")

    def run_download() -> None:
        try:
            output_path, rows = download_ohlcv(
                symbol=symbol,
                interval=timeframe,
                first_bar=first_bar,
                last_bar=last_bar,
            )

            root.after(
                0,
                lambda: status_var.set(
                    f"Saved {rows:,} bars: {output_path.name}"
                ),
            )

        except Exception as error:
            root.after(
                0,
                lambda: status_var.set(f"Error: {error}"),
            )

    threading.Thread(
        target=run_download,
        daemon=True,
    ).start()


root = tk.Tk()
root.title("Bitget OHLC Downloader")
root.resizable(False, False)

symbol_var = tk.StringVar(value="BTCUSDT")
timeframe_var = tk.StringVar(value="1m")

default_last_bar = datetime.now(timezone.utc).replace(
    second=0,
    microsecond=0,
)

default_first_bar = default_last_bar - timedelta(minutes=999)

first_bar_var = tk.StringVar(
    value=default_first_bar.strftime(DATE_FORMAT)
)

last_bar_var = tk.StringVar(
    value=default_last_bar.strftime(DATE_FORMAT)
)

estimate_var = tk.StringVar()
status_var = tk.StringVar()

ttk.Label(root, text="Trading pair").grid(
    row=0, column=0, padx=10, pady=8, sticky="w"
)
ttk.Entry(root, textvariable=symbol_var, width=25).grid(
    row=0, column=1
)

ttk.Label(root, text="Timeframe").grid(
    row=1, column=0, padx=10, pady=8, sticky="w"
)
ttk.Combobox(
    root,
    textvariable=timeframe_var,
    values=list(TIMEFRAME_SECONDS.keys()),
    state="readonly",
    width=22,
).grid(row=1, column=1)

ttk.Label(root, text="First bar").grid(
    row=2, column=0, padx=10, pady=8, sticky="w"
)
ttk.Entry(root, textvariable=first_bar_var, width=25).grid(
    row=2, column=1
)

ttk.Label(root, text="Last bar").grid(
    row=3, column=0, padx=10, pady=8, sticky="w"
)
ttk.Entry(root, textvariable=last_bar_var, width=25).grid(
    row=3, column=1
)

ttk.Label(root, textvariable=estimate_var, justify="left").grid(
    row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w"
)

ttk.Button(root, text="Download", command=submit).grid(
    row=5, column=0, columnspan=2, pady=12
)

ttk.Label(root, textvariable=status_var).grid(
    row=6, column=0, columnspan=2, padx=10, pady=8
)

for variable in [
    timeframe_var,
    first_bar_var,
    last_bar_var,
]:
    variable.trace_add("write", update_estimate)

update_estimate()
root.mainloop()