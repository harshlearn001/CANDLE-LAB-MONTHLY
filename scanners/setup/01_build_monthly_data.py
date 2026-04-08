#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | MONTHLY CANDLES (F&O ONLY)

Builds expiry-based monthly candles using the saved NIFTY monthly expiry dates.
"""

import pandas as pd
from pathlib import Path

print("BUILDING MONTHLY CANDLES (EXPIRY-BASED)\n")

# ============================================
# PATHS
# ============================================
FNO_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\fno_symbols.csv")
EXPIRY_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\nse_expiries_final.csv")

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

# ============================================
# LOAD MONTHLY EXPIRIES
# ============================================
expiry_df = pd.read_csv(EXPIRY_FILE)
expiry_df.columns = expiry_df.columns.str.strip().str.upper()
expiry_df["EXPIRY_DATE"] = pd.to_datetime(expiry_df["EXPIRY_DATE"], errors="coerce")
expiry_df = expiry_df.dropna(subset=["EXPIRY_DATE"]).sort_values("EXPIRY_DATE")

EXPIRY_DATES = list(expiry_df["EXPIRY_DATE"].drop_duplicates())

print(f"Loaded F&O symbols: {len(FNO_SYMBOLS)}")
print(f"Loaded monthly expiries: {len(EXPIRY_DATES)}\n")


# ============================================
# FUNCTION: MAP TRADE DATE TO EXPIRY
# ============================================
def assign_expiry_bucket(dates):
    expiry_index = pd.DatetimeIndex(EXPIRY_DATES)
    positions = expiry_index.searchsorted(pd.DatetimeIndex(dates), side="left")

    mapped = pd.Series(pd.NaT, index=dates.index, dtype="datetime64[ns]")
    valid = positions < len(expiry_index)

    if valid.any():
        mapped.loc[valid] = expiry_index.take(positions[valid]).to_numpy()

    return mapped


# ============================================
# FUNCTION: BUILD MONTHLY
# ============================================
def build_monthly(file, symbol):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.upper()

        if "DATE" in df.columns:
            date_col = "DATE"
        elif "TRADE_DATE" in df.columns:
            date_col = "TRADE_DATE"
        else:
            print(f"Skipped {symbol} (no DATE column)")
            return None

        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col]).sort_values(date_col)

        required = {"OPEN", "HIGH", "LOW", "CLOSE"}
        if not required.issubset(df.columns):
            print(f"Skipped {symbol} (missing OHLC columns)")
            return None

        if "VOLUME" not in df.columns:
            df["VOLUME"] = 0

        df["EXPIRY_DATE"] = assign_expiry_bucket(df[date_col])
        df = df.dropna(subset=["EXPIRY_DATE"])

        monthly_rows = []

        for expiry_date, group in df.groupby("EXPIRY_DATE"):
            group = group.sort_values(date_col)

            monthly_rows.append(
                {
                    "DATE": expiry_date,
                    "SYMBOL": symbol,
                    "OPEN": group["OPEN"].iloc[0],
                    "HIGH": group["HIGH"].max(),
                    "LOW": group["LOW"].min(),
                    "CLOSE": group["CLOSE"].iloc[-1],
                    "VOLUME": group["VOLUME"].sum(),
                }
            )

        if not monthly_rows:
            return None

        return pd.DataFrame(monthly_rows).sort_values("DATE")

    except Exception as e:
        print(f"ERROR: {symbol} | {e}")
        return None


# ============================================
# PROCESS F&O STOCKS
# ============================================
print("Processing F&O stocks...\n")

for symbol in sorted(FNO_SYMBOLS):
    file = DATA_DIR / f"{symbol}.csv"

    if not file.exists():
        print(f"Missing: {symbol}")
        continue

    result = build_monthly(file, symbol)

    if result is None:
        continue

    out_file = OUT_DIR / f"{symbol}.csv"
    result.to_csv(out_file, index=False)

    print(f"{symbol} done")

# ============================================
# DONE
# ============================================
print("\nF&O MONTHLY CANDLES READY")
print("Saved in ->", OUT_DIR)
