import pandas as pd
from pathlib import Path
from datetime import datetime

print("🔥 MONTHLY BEARISH ENGULFING (UPGRADED)\n")

# ==============================
# PATHS
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\engulfing_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_bearish_engulfing_{today}.csv"

results = []

# ==============================
# SCAN
# ==============================
for file in DATA_DIR.glob("*.csv"):
    try:
        df = pd.read_csv(file)

        if len(df) < 3:
            continue

        df.columns = [c.lower() for c in df.columns]

        # last 2 candles
        df = df.tail(2)

        prev = df.iloc[0]
        curr = df.iloc[1]

        # ==========================
        # BODY SIZE FILTER
        # ==========================
        prev_body = abs(prev["close"] - prev["open"])
        curr_body = abs(curr["close"] - curr["open"])

        if prev_body == 0 or curr_body == 0:
            continue

        # ==========================
        # BEARISH ENGULFING
        # ==========================
        if (
            prev["close"] > prev["open"] and   # prev bullish
            curr["close"] < curr["open"] and   # curr bearish
            curr["open"] >= prev["close"] and
            curr["close"] <= prev["open"] and
            curr_body > prev_body * 0.8   # strong engulfing
        ):
            print(f"{file.stem}")

            results.append({
                "SYMBOL": file.stem,
                "Pattern": "Bearish Engulfing",
                "Prev_Close": prev["close"],
                "Curr_Close": curr["close"],
                "Body_Strength": round(curr_body / prev_body, 2)
            })

    except Exception as e:
        print(f"❌ ERROR {file.stem}: {e}")

# ==============================
# SAVE
# ==============================
df_out = pd.DataFrame(results)

if not df_out.empty:
    df_out.to_csv(OUT_FILE, index=False)

    print(f"\n🔥 TOTAL BEARISH ENGULFING: {len(results)}")
    print(f"Saved → {OUT_FILE}")

else:
    print("\n⚠ No bearish engulfing found")