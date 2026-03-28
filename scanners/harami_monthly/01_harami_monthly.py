import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY HARAMI SCANNER\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\harami_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

OUT_BULL = OUT_DIR / f"monthly_bullish_harami_{today}.csv"
OUT_BEAR = OUT_DIR / f"monthly_bearish_harami_{today}.csv"

bull_results = []
bear_results = []

# ==============================
# SCAN
# ==============================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        if len(df) < 2:
            continue

        # 🔥 standardize columns
        df.columns = [c.lower() for c in df.columns]

        df = df.tail(2)

        prev = df.iloc[0]
        curr = df.iloc[1]

        prev_open = prev["open"]
        prev_close = prev["close"]

        curr_open = curr["open"]
        curr_close = curr["close"]

        prev_high_body = max(prev_open, prev_close)
        prev_low_body = min(prev_open, prev_close)

        curr_high_body = max(curr_open, curr_close)
        curr_low_body = min(curr_open, curr_close)

        # ==========================
        # BULLISH HARAMI
        # ==========================
        if (
            prev_close < prev_open and
            curr_high_body <= prev_high_body and
            curr_low_body >= prev_low_body
        ):
            print(f"Bullish Harami → {file.stem}")

            bull_results.append({
                "SYMBOL": file.stem,
                "Pattern": "Bullish Harami"
            })

        # ==========================
        # BEARISH HARAMI
        # ==========================
        if (
            prev_close > prev_open and
            curr_high_body <= prev_high_body and
            curr_low_body >= prev_low_body
        ):
            print(f"Bearish Harami → {file.stem}")

            bear_results.append({
                "SYMBOL": file.stem,
                "Pattern": "Bearish Harami"
            })

    except Exception as e:
        print(f"ERROR {file.stem}: {e}")

# ==============================
# SAVE
# ==============================
pd.DataFrame(bull_results).to_csv(OUT_BULL, index=False)
pd.DataFrame(bear_results).to_csv(OUT_BEAR, index=False)

print("\nSCAN COMPLETE")
print(f"Bullish: {len(bull_results)}")
print(f"Bearish: {len(bear_results)}")

print("\nSaved:")
print(OUT_BULL)
print(OUT_BEAR)