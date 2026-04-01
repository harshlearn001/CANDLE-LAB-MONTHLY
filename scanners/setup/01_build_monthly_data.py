#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | MONTHLY CANDLES (F&O ONLY)

✔ Uses FNO symbols list
✔ Builds calendar monthly candles (NOT expiry-based)
✔ Clean OHLC aggregation
✔ Production ready
"""

import pandas as pd
from pathlib import Path

print("📊 BUILDING MONTHLY CANDLES (F&O ONLY)\n")

# ============================================
# PATHS
# ============================================
FNO_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\fno_symbols.csv")

DATA_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# LOAD F&O SYMBOLS
# ============================================
fno_df = pd.read_csv(FNO_FILE)

FNO_SYMBOLS = set(
    fno_df["SYMBOL"]
    .astype(str)
    .str.strip()
    .str.upper()
)

print(f"✔ Loaded F&O symbols: {len(FNO_SYMBOLS)}\n")

# ============================================
# FUNCTION: BUILD MONTHLY
# ============================================
def build_monthly(file, symbol):

    try:
        df = pd.read_csv(file)

        df.columns = df.columns.str.strip().str.upper()

        # Detect date column
        if "DATE" in df.columns:
            date_col = "DATE"
        elif "TRADE_DATE" in df.columns:
            date_col = "TRADE_DATE"
        else:
            return None

        # Convert date
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])

        df = df.sort_values(date_col)
        df.set_index(date_col, inplace=True)

        # Ensure OHLC
        required = {"OPEN", "HIGH", "LOW", "CLOSE"}
        if not required.issubset(df.columns):
            return None

        if "VOLUME" not in df.columns:
            df["VOLUME"] = 0

        # ====================================
        # GROUP BY MONTH (CALENDAR)
        # ====================================
        df["MONTH"] = df.index.to_period("M")

        monthly = []

        for _, g in df.groupby("MONTH"):

            g = g.sort_index()

            monthly.append({
                "DATE": g.index[-1],              # last trading day
                "SYMBOL": symbol,
                "OPEN": g["OPEN"].iloc[0],
                "HIGH": g["HIGH"].max(),
                "LOW": g["LOW"].min(),
                "CLOSE": g["CLOSE"].iloc[-1],
                "VOLUME": g["VOLUME"].sum()
            })

        if not monthly:
            return None

        return pd.DataFrame(monthly)

    except Exception as e:
        print(f"❌ ERROR: {symbol} | {e}")
        return None

# ============================================
# PROCESS F&O STOCKS
# ============================================
print("🔹 Processing F&O stocks...\n")

for symbol in sorted(FNO_SYMBOLS):

    file = DATA_DIR / f"{symbol}.csv"

    if not file.exists():
        print(f"⚠ Missing: {symbol}")
        continue

    result = build_monthly(file, symbol)

    if result is None:
        continue

    out_file = OUT_DIR / f"{symbol}.csv"
    result.to_csv(out_file, index=False)

    print(f"✔ {symbol} done")

# ============================================
# DONE
# ============================================
print("\n🔥 F&O MONTHLY CANDLES READY")
print("Saved in →", OUT_DIR)