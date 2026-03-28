import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY BULLISH ENGULFING\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\engulfing_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_bullish_engulfing_{today}.csv"

results = []

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

        # ==========================
        # BULLISH ENGULFING LOGIC
        # ==========================
        if (
            prev["close"] < prev["open"] and   # previous bearish
            curr["close"] > curr["open"] and   # current bullish
            curr["open"] < prev["close"] and
            curr["close"] > prev["open"]
        ):
            print(f"{file.stem}")

            results.append({
                "SYMBOL": file.stem,
                "Pattern": "Bullish Engulfing"
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