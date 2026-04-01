#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | FINAL EXPIRY (ADAPTIVE + FUTURE PROOF)

✔ Uses futures data (MarketForge)
✔ Automatically detects expiry weekday (Tue/Thu)
✔ Handles NSE rule changes
✔ No hardcoding
✔ Institutional-grade accuracy
"""

import pandas as pd
from pathlib import Path

print("📊 BUILDING FINAL ADAPTIVE EXPIRY SYSTEM\n")

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
# GROUP BY MONTH
# ============================================
df["MONTH"] = df["EXP_DATE"].dt.to_period("M")

monthly_expiry = []

# ============================================
# CORE LOGIC (ADAPTIVE)
# ============================================
for period, group in df.groupby("MONTH"):

    dates = sorted(group["EXP_DATE"].unique())

    if len(dates) == 0:
        continue

    # ----------------------------------------
    # 🔥 STEP 1: Detect dominant weekday
    # ----------------------------------------
    weekday_series = pd.Series([d.weekday() for d in dates])
    dominant_weekday = weekday_series.value_counts().idxmax()

    # ----------------------------------------
    # 🔥 STEP 2: Filter only dominant weekday
    # ----------------------------------------
    valid_dates = [d for d in dates if d.weekday() == dominant_weekday]

    if not valid_dates:
        continue

    # ----------------------------------------
    # 🔥 STEP 3: Take latest (true expiry)
    # ----------------------------------------
    expiry = max(valid_dates)

    monthly_expiry.append(expiry)

# ============================================
# FINAL DATAFRAME
# ============================================
expiry_df = pd.DataFrame({
    "EXPIRY_DATE": sorted(set(monthly_expiry))
})

# ============================================
# SAVE
# ============================================
expiry_df.to_csv(OUT_FILE, index=False)

print("\n✅ FINAL ADAPTIVE EXPIRY READY →", OUT_FILE)

print("\n📌 SAMPLE:")
print(expiry_df.head(10))

print("\n📌 LAST:")
print(expiry_df.tail(10))