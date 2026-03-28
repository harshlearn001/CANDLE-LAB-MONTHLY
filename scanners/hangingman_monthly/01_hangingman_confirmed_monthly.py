import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY HANGING MAN WITH CONFIRMATION\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\hangingman_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_hangingman_confirmed_{today}.csv"

results = []

# ==============================
# SCAN
# ==============================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        if len(df) < 4:
            continue

        # 🔥 standardize columns
        df.columns = [c.lower() for c in df.columns]

        # Context + pattern + confirmation
        prev = df.iloc[-3]
        hm = df.iloc[-2]
        confirm = df.iloc[-1]

        open_ = hm["open"]
        close = hm["close"]
        high = hm["high"]
        low = hm["low"]

        body = abs(close - open_)
        full_range = high - low

        lower_wick = min(open_, close) - low
        upper_wick = high - max(open_, close)

        # ==========================
        # HANGING MAN SHAPE
        # ==========================
        is_shape = (
            full_range > 0 and
            body <= (0.3 * full_range) and
            lower_wick >= (0.6 * full_range) and
            upper_wick <= (0.1 * full_range)
        )

        # ==========================
        # CONTEXT (UPTREND)
        # ==========================
        is_uptrend = prev["close"] > prev["open"]

        # ==========================
        # CONFIRMATION (BREAKDOWN)
        # ==========================
        is_confirmed = confirm["close"] < low

        if is_shape and is_uptrend and is_confirmed:
            print(f"{file.stem}")

            results.append({
                "SYMBOL": file.stem,
                "Pattern": "Hanging Man Confirmed"
            })

    except Exception as e:
        print(f"ERROR {file.stem}: {e}")

# ==============================
# SAVE
# ==============================
df_out = pd.DataFrame(results)
df_out.to_csv(OUT_FILE, index=False)

print(f"\nTotal: {len(results)}")
print(f"Saved → {OUT_FILE}")