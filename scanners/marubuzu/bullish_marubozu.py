import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY BULLISH MARUBOZU SCANNER\n")

# ==============================
# PATHS
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\marubozu_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_bullish_marubozu_{today}.csv"

results = []

# ==============================
# PARAMETERS
# ==============================
THRESHOLD = 0.02  # 2% wick tolerance

# ==============================
# SCAN
# ==============================
for file in DATA_DIR.glob("*.csv"):

    symbol = file.stem.upper()

    try:
        df = pd.read_csv(file)

        if len(df) < 1:
            continue

        df.columns = df.columns.str.strip().str.upper()

        last = df.iloc[-1]

        o, h, l, c = last["OPEN"], last["HIGH"], last["LOW"], last["CLOSE"]

        # Bullish condition
        if (
            c > o and
            abs(o - l) / (h - l + 1e-9) < THRESHOLD and
            abs(h - c) / (h - l + 1e-9) < THRESHOLD
        ):
            results.append({
                "SYMBOL": symbol,
                "DATE": last["DATE"],
                "PATTERN": "BULLISH_MARUBOZU"
            })

            print(f"🟢 {symbol}")

    except Exception as e:
        print(f"❌ {symbol} | {e}")

# ==============================
# SAVE
# ==============================
if results:
    pd.DataFrame(results).to_csv(OUT_FILE, index=False)

print("\n🔥 BULLISH MARUBOZU SCAN COMPLETE")
print(f"Total: {len(results)}")
print(f"Saved → {OUT_FILE}")