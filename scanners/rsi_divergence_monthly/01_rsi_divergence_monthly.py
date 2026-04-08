import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY RSI DIVERGENCE SCANNER\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\rsi_divergence_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

OUT_BULL = OUT_DIR / f"monthly_bullish_divergence_{today}.csv"
OUT_BEAR = OUT_DIR / f"monthly_bearish_divergence_{today}.csv"

BULL_COLUMNS = ["SYMBOL", "Type"]
BEAR_COLUMNS = ["SYMBOL", "Type"]
bull_results = []
bear_results = []

# ==============================
# RSI FUNCTION
# ==============================
def calculate_rsi(df, period=14):

    delta = df["close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df


# ==============================
# SCAN
# ==============================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        if len(df) < 40:
            continue

        #  standardize columns
        df.columns = [c.lower() for c in df.columns]

        if not {"high", "low", "close"}.issubset(df.columns):
            continue

        df = calculate_rsi(df)

        df = df.dropna(subset=["rsi"])

        if len(df) < 10:
            continue

        # ==========================
        # SIMPLE SWING LOGIC
        # ==========================
        recent = df.tail(6)

        # Price swings
        price_low1 = recent.iloc[1]["low"]
        price_low2 = recent.iloc[4]["low"]

        price_high1 = recent.iloc[1]["high"]
        price_high2 = recent.iloc[4]["high"]

        # RSI swings
        rsi_low1 = recent.iloc[1]["rsi"]
        rsi_low2 = recent.iloc[4]["rsi"]

        rsi_high1 = recent.iloc[1]["rsi"]
        rsi_high2 = recent.iloc[4]["rsi"]

        # ==========================
        # BULLISH DIVERGENCE
        # ==========================
        if (
            price_low2 < price_low1 and
            rsi_low2 > rsi_low1
        ):
            print(f"Bullish -> {file.stem}")

            bull_results.append({
                "SYMBOL": file.stem,
                "Type": "Bullish Divergence"
            })

        # ==========================
        # BEARISH DIVERGENCE
        # ==========================
        if (
            price_high2 > price_high1 and
            rsi_high2 < rsi_high1
        ):
            print(f"Bearish -> {file.stem}")

            bear_results.append({
                "SYMBOL": file.stem,
                "Type": "Bearish Divergence"
            })

    except Exception as e:
        print(f"ERROR {file.stem}: {e}")

# ==============================
# SAVE
# ==============================
pd.DataFrame(bull_results, columns=BULL_COLUMNS).to_csv(OUT_BULL, index=False)
pd.DataFrame(bear_results, columns=BEAR_COLUMNS).to_csv(OUT_BEAR, index=False)

print("\nSCAN COMPLETE")
print(f"Bullish: {len(bull_results)}")
print(f"Bearish: {len(bear_results)}")

print("\nSaved:")
print(OUT_BULL)
print(OUT_BEAR)
