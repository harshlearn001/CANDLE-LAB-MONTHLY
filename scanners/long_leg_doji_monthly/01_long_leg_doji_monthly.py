import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY LONG-LEGGED DOJI SCANNER\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\longleg_doji_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_longleg_doji_{today}.csv"

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

        # 🔥 standardize columns
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
        # LONG-LEGGED DOJI CONDITIONS
        # ==========================
        if (
            full_range > 0 and
            body <= (0.1 * full_range) and
            upper_wick >= (0.4 * full_range) and
            lower_wick >= (0.4 * full_range)
        ):
            print(f"{file.stem}")

            results.append({
                "SYMBOL": file.stem,
                "Pattern": "Long-Legged Doji"
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