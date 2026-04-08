import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY SHOOTING STAR SCANNER\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\shooting_star_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_shooting_star_{today}.csv"

RESULT_COLUMNS = ["SYMBOL", "Pattern"]
results = []

# ==============================
# SCAN
# ==============================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        if len(df) < 1:
            continue

        #  standardize columns
        df.columns = [c.lower() for c in df.columns]

        candle = df.iloc[-1]

        open_ = candle["open"]
        close = candle["close"]
        high = candle["high"]
        low = candle["low"]

        body = abs(close - open_)
        full_range = high - low

        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low

        # ==========================
        # SHOOTING STAR CONDITIONS
        # ==========================
        if (
            full_range > 0 and
            body <= (0.3 * full_range) and
            upper_wick >= (0.6 * full_range) and
            lower_wick <= (0.1 * full_range)
        ):
            print(f"{file.stem}")

            results.append({
                "SYMBOL": file.stem,
                "Pattern": "Shooting Star"
            })

    except Exception as e:
        print(f"ERROR {file.stem}: {e}")

# ==============================
# SAVE
# ==============================
df_out = pd.DataFrame(results, columns=RESULT_COLUMNS)
df_out.to_csv(OUT_FILE, index=False)

print(f"\nTotal: {len(results)}")
print(f"Saved -> {OUT_FILE}")
