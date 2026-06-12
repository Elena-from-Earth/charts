import tkinter as tk
from tkinter import ttk
from datetime import datetime


DATE_FORMAT = "%d-%m-%Y %H:%M:%S"


def submit() -> None:
    symbol = symbol_var.get().strip().upper()
    interval_value = interval_var.get().strip()
    interval_unit = unit_var.get()

    try:
        datetime.strptime(first_bar_var.get(), DATE_FORMAT)
        datetime.strptime(last_bar_var.get(), DATE_FORMAT)
    except ValueError:
        status_var.set("Error: use dd-mm-yyyy hh:mm:ss")
        return

    status_var.set(
        f"{symbol} | {interval_value}{interval_unit} | parameters accepted"
    )


root = tk.Tk()
root.title("Bitget OHLC Downloader")
root.resizable(False, False)

symbol_var = tk.StringVar(value="BTCUSDT")
interval_var = tk.StringVar(value="1")
unit_var = tk.StringVar(value="m")
first_bar_var = tk.StringVar(value="01-06-2026 00:00:00")
last_bar_var = tk.StringVar(value="11-06-2026 23:59:00")
status_var = tk.StringVar()

ttk.Label(root, text="Trading pair").grid(row=0, column=0, padx=10, pady=8, sticky="w")
ttk.Entry(root, textvariable=symbol_var, width=25).grid(row=0, column=1, columnspan=2)

ttk.Label(root, text="Timeframe").grid(row=1, column=0, padx=10, pady=8, sticky="w")
ttk.Entry(root, textvariable=interval_var, width=10).grid(row=1, column=1)

ttk.Combobox(
    root,
    textvariable=unit_var,
    values=["s", "m", "h", "d"],
    state="readonly",
    width=5,
).grid(row=1, column=2)

ttk.Label(root, text="First bar").grid(row=2, column=0, padx=10, pady=8, sticky="w")
ttk.Entry(root, textvariable=first_bar_var, width=25).grid(row=2, column=1, columnspan=2)

ttk.Label(root, text="Last bar").grid(row=3, column=0, padx=10, pady=8, sticky="w")
ttk.Entry(root, textvariable=last_bar_var, width=25).grid(row=3, column=1, columnspan=2)

ttk.Button(root, text="Download", command=submit).grid(
    row=4, column=0, columnspan=3, pady=12
)

ttk.Label(root, textvariable=status_var).grid(
    row=5, column=0, columnspan=3, padx=10, pady=8
)

root.mainloop()