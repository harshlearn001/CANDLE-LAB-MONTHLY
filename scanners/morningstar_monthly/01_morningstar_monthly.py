import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY MORNING STAR SCANNER\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\morning_star_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_morning_star_{today}.csv"

RESULT_COLUMNS = ["SYMBOL", "Pattern"]
results = []

# ==============================
# SCAN
# ==============================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        if len(df) < 3:
            continue

        #  standardize columns
        df.columns = [c.lower() for c in df.columns]

        c1 = df.iloc[-3]
        c2 = df.iloc[-2]
        c3 = df.iloc[-1]

        # ==========================
        # CONDITIONS
        # ==========================

        # Candle 1 bearish
        cond1 = c1["close"] < c1["open"]

        # Candle 2 small body
        body2 = abs(c2["close"] - c2["open"])
        range2 = c2["high"] - c2["low"]
        cond2 = (range2 > 0) and (body2 <= (0.3 * range2))

        # Candle 3 bullish
        cond3 = c3["close"] > c3["open"]

        # Close above midpoint of candle 1
        midpoint = (c1["open"] + c1["close"]) / 2
        cond4 = c3["close"] > midpoint

        if cond1 and cond2 and cond3 and cond4:
            print(f"{file.stem}")

            results.append({
                "SYMBOL": file.stem,
                "Pattern": "Morning Star"
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
