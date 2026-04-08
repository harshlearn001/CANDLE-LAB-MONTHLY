#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | NIFTY MONTHLY EXPIRY CSV

Builds one monthly expiry date per month from NIFTY futures master data.
"""

import pandas as pd
from pathlib import Path

print("BUILDING NIFTY MONTHLY EXPIRY CSV\n")

# ============================================
# PATH
# ============================================
DATA_FILE = Path(r"H:\MarketForge\data\master\Futures_master\FUTIDX\NIFTY.csv")
OUT_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\nse_expiries_final.csv")

# ============================================
# LOAD DATA
# ============================================
df = pd.read_csv(DATA_FILE)

df.columns = df.columns.str.strip().str.upper()

# Convert EXP_DATE
df["EXP_DATE"] = pd.to_datetime(df["EXP_DATE"], format="%Y%m%d", errors="coerce")

df = df.dropna(subset=["EXP_DATE"])

# ============================================
# KEEP ONLY VALID NIFTY FUTURES EXPIRIES
# ============================================
df["MONTH"] = df["EXP_DATE"].dt.to_period("M")
if "SYMBOL" in df.columns:
    df = df[df["SYMBOL"].astype(str).str.strip().str.upper() == "NIFTY"]

expiry_df = (
    df.groupby("MONTH", as_index=False)["EXP_DATE"]
    .max()
    .rename(columns={"EXP_DATE": "EXPIRY_DATE"})
    .sort_values("EXPIRY_DATE")
)

# ============================================
# FINAL DATAFRAME
# ============================================
expiry_df["EXPIRY_DATE"] = expiry_df["EXPIRY_DATE"].dt.strftime("%Y-%m-%d")
expiry_df = expiry_df[["EXPIRY_DATE"]]

# ============================================
# SAVE
# ============================================
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
expiry_df.to_csv(OUT_FILE, index=False)

print("\nNIFTY MONTHLY EXPIRY CSV READY ->", OUT_FILE)

print("\nSAMPLE:")
print(expiry_df.head(10))

print("\nLAST:")
print(expiry_df.tail(10))
