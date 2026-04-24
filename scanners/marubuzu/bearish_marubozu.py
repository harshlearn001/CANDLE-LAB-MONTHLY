import pandas as pd
from pathlib import Path
from datetime import datetime

print("🔴 MONTHLY BEARISH MARUBOZU 🔥\n")

# ==============================
# PATHS
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\marubozu_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_bearish_marubozu_{today}.csv"

# ==============================
# PARAMETERS (ALIGNED SYSTEM)
# ==============================
MIN_BODY_RATIO = 0.65     # monthly slightly relaxed
WICK_TOLERANCE = 0.01     # 1% tolerance (monthly candles bigger)

results = []

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

        o = last["OPEN"]
        h = last["HIGH"]
        l = last["LOW"]
        c = last["CLOSE"]

        rng = h - l
        if rng <= 0:
            continue

        body = abs(c - o)
        body_ratio = body / rng

        # body strength filter
        if body_ratio < MIN_BODY_RATIO:
            continue

        # wick calculation
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l

        tol = c * WICK_TOLERANCE

        # bearish marubozu
        if (
            c < o and
            upper_wick <= tol and
            lower_wick <= tol
        ):
            results.append({
                "SYMBOL": symbol,
                "DATE": last.get("DATE", ""),
                "PATTERN": "BEARISH_MARUBOZU",
                "BODY_RATIO": round(body_ratio, 2)
            })

            print(f"🔴 {symbol}")

    except Exception as e:
        print(f"❌ {symbol} | {e}")

# ==============================
# SAVE
# ==============================
if results:
    pd.DataFrame(results).to_csv(OUT_FILE, index=False)

print("\n🔥 BEARISH MARUBOZU SCAN COMPLETE")
print(f"Total: {len(results)}")
print(f"Saved → {OUT_FILE}")