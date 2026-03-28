#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB-MONTHLY | NR7 SCANNER

✔ Monthly candles
✔ NR7 (lowest range of last 7 months)
✔ Trend filter (MA20 monthly)
✔ Clean + fast
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

print("\nMONTHLY NR7 SCANNER STARTED\n")

# =====================================================
# PATHS
# =====================================================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\nr7_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today_str = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_nr7_{today_str}.csv"

results = []

# =====================================================
# PROCESS
# =====================================================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        if df.empty or len(df) < 30:
            continue

        # ==============================
        # STANDARDIZE
        # ==============================
        df.columns = df.columns.str.lower()

        required = {"open", "high", "low", "close"}
        if not required.issubset(df.columns):
            continue

        # ==============================
        # CALCULATIONS
        # ==============================
        df["range"] = df["high"] - df["low"]
        df["ma20"] = df["close"].rolling(20).mean()

        df = df.dropna(subset=["ma20"])

        if len(df) < 7:
            continue

        last7 = df.tail(7)

        today = last7.iloc[-1]
        prev6 = last7.iloc[:-1]

        # ==============================
        # NR7 CONDITION
        # ==============================
        nr7 = today["range"] < prev6["range"].min()

        # ==============================
        # TREND FILTER (MONTHLY)
        # ==============================
        trend_up = today["close"] > today["ma20"]
        trend_down = today["close"] < today["ma20"]

        # ==============================
        # FINAL SIGNAL
        # ==============================
        if nr7:

            direction = "NEUTRAL"

            if trend_up:
                direction = "BREAKOUT_UP"
            elif trend_down:
                direction = "BREAKOUT_DOWN"

            print(f"NR7 → {file.stem} ({direction})")

            results.append({
                "Symbol": file.stem,
                "Close": round(today["close"], 2),
                "Range": round(today["range"], 2),
                "MA20": round(today["ma20"], 2),
                "Direction": direction
            })

    except Exception as e:
        print(f"ERROR → {file.stem} | {e}")

# =====================================================
# SAVE OUTPUT
# =====================================================
out = pd.DataFrame(results)

if not out.empty:
    out = out.sort_values("Range")  # tightest first
    out.to_csv(OUT_FILE, index=False)

    print("\nMONTHLY NR7 SCAN COMPLETED")
    print("Stocks found:", len(out))
    print("Saved →", OUT_FILE)

else:
    print("\nNo NR7 signals found")