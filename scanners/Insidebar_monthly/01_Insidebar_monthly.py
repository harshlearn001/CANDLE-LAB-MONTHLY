import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY INSIDE BAR SCANNER\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\insidebar_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_insidebar_{today}.csv"

RESULT_COLUMNS = ["SYMBOL", "Pattern", "Prev_High", "Prev_Low"]
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

        #  standardize columns
        df.columns = [c.lower() for c in df.columns]

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        # ==========================
        # INSIDE BAR CONDITION
        # ==========================
        if (
            curr["high"] < prev["high"] and
            curr["low"] > prev["low"]
        ):
            print(f"{file.stem}")

            results.append({
                "SYMBOL": file.stem,
                "Pattern": "Inside Bar",
                "Prev_High": prev["high"],
                "Prev_Low": prev["low"]
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
