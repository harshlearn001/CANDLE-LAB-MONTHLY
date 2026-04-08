#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | MONTHLY BULLISH ENGULFING
"""

from pathlib import Path
from datetime import datetime
import pandas as pd

print("MONTHLY BULLISH ENGULFING SCANNER\n")

# =================================================
# PATHS
# =================================================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")
FNO_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\engulfing_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_bullish_engulfing_{today}.csv"

MIN_BODY_RATIO = 0.40

symbols = set(
    pd.read_csv(FNO_FILE)["SYMBOL"]
    .astype(str)
    .str.strip()
    .str.upper()
)

RESULT_COLUMNS = ["SYMBOL", "DATE", "PATTERN"]
results = []

print(f"F&O symbols loaded: {len(symbols)}")

for symbol in sorted(symbols):
    file = DATA_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)

        if len(df) < 2:
            continue

        df.columns = df.columns.str.strip().str.upper()

        required = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}
        if not required.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 2:
            continue

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        def body_ratio(candle):
            candle_range = candle["HIGH"] - candle["LOW"]
            if candle_range <= 0:
                return 0
            return abs(candle["CLOSE"] - candle["OPEN"]) / candle_range

        if body_ratio(prev) < MIN_BODY_RATIO or body_ratio(curr) < MIN_BODY_RATIO:
            continue

        if (
            prev["CLOSE"] < prev["OPEN"]
            and curr["CLOSE"] > curr["OPEN"]
            and curr["OPEN"] < prev["CLOSE"]
            and curr["CLOSE"] > prev["OPEN"]
        ):
            results.append(
                {
                    "SYMBOL": symbol,
                    "DATE": curr["DATE"].date(),
                    "PATTERN": "BULLISH_ENGULFING_MONTHLY",
                }
            )
            print(symbol)

    except Exception as e:
        print(f"ERROR {symbol} | {e}")

pd.DataFrame(results, columns=RESULT_COLUMNS).to_csv(OUT_FILE, index=False)

print("\nMONTHLY BULLISH ENGULFING SCAN COMPLETED")
print(f"Stocks found: {len(results)}")
print(f"Saved -> {OUT_FILE}")
