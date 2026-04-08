import pandas as pd
from pathlib import Path
from datetime import datetime
import numpy as np

print(" MONTHLY ADX SCANNER (FIXED)\n")

# ==============================
# PATHS
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\adx_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_adx_{today}.csv"

RESULT_COLUMNS = ["SYMBOL", "ADX", "+DI", "-DI", "Signal"]
results = []

# ==============================
# ADX FUNCTION (FIXED)
# ==============================
def calculate_adx(df, period=14):

    df = df.copy()

    df["h-l"] = df["high"] - df["low"]
    df["h-pc"] = abs(df["high"] - df["close"].shift(1))
    df["l-pc"] = abs(df["low"] - df["close"].shift(1))

    df["tr"] = df[["h-l", "h-pc", "l-pc"]].max(axis=1)

    df["+dm"] = np.where(
        (df["high"] - df["high"].shift(1)) > (df["low"].shift(1) - df["low"]),
        np.maximum(df["high"] - df["high"].shift(1), 0),
        0
    )

    df["-dm"] = np.where(
        (df["low"].shift(1) - df["low"]) > (df["high"] - df["high"].shift(1)),
        np.maximum(df["low"].shift(1) - df["low"], 0),
        0
    )

    tr_smooth = df["tr"].rolling(period).mean()
    plus_dm = df["+dm"].rolling(period).mean()
    minus_dm = df["-dm"].rolling(period).mean()

    df["+di"] = 100 * (plus_dm / tr_smooth)
    df["-di"] = 100 * (minus_dm / tr_smooth)

    dx = (abs(df["+di"] - df["-di"]) / (df["+di"] + df["-di"])) * 100
    df["adx"] = dx.rolling(period).mean()

    return df

# ==============================
# SCAN FILES
# ==============================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        # Minimum candles check (ADX needs history)
        if len(df) < 30:
            continue

        # Convert columns to lowercase
        df.columns = [c.lower() for c in df.columns]

        # Ensure required columns exist
        required_cols = {"open", "high", "low", "close"}
        if not required_cols.issubset(df.columns):
            print(f"WARN Skipped {file.stem} (missing OHLC)")
            continue

        # Calculate ADX
        df = calculate_adx(df)

        # Safety check
        if "adx" not in df.columns:
            print(f"WARN ADX missing for {file.stem}")
            continue

        last = df.iloc[-1]

        # Skip if NaN
        if pd.isna(last["adx"]):
            continue

        adx = last["adx"]
        plus_di = last["+di"]
        minus_di = last["-di"]

        # ==============================
        # SIGNAL LOGIC
        # ==============================
        if adx > 25:

            if plus_di > minus_di:
                signal = "STRONG UPTREND"
            else:
                signal = "STRONG DOWNTREND"

            results.append({
                "SYMBOL": file.stem,
                "ADX": round(adx, 2),
                "+DI": round(plus_di, 2),
                "-DI": round(minus_di, 2),
                "Signal": signal
            })

            print(f"{file.stem} -> {signal} (ADX={round(adx,2)})")

    except Exception as e:
        print(f"ERROR ERROR {file.stem}: {e}")

# ==============================
# SAVE OUTPUT
# ==============================
df_out = pd.DataFrame(results, columns=RESULT_COLUMNS)

if not df_out.empty:
    df_out = df_out.sort_values("ADX", ascending=False)

df_out.to_csv(OUT_FILE, index=False)

if not df_out.empty:
    print(f"\n TOTAL STRONG TREND STOCKS: {len(results)}")
    print(f"Saved -> {OUT_FILE}")

else:
    print("\nWARN No strong ADX trends found")
    print(f"Saved -> {OUT_FILE}")
