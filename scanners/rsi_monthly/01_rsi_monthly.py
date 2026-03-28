import pandas as pd
from pathlib import Path
from datetime import datetime

print("MONTHLY RSI SCANNER\n")

# ==============================
# PATHS (UPDATED)
# ==============================
DATA_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals\rsi_monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"monthly_rsi_{today}.csv"

results = []

# ==============================
# RSI FUNCTION
# ==============================
def calculate_rsi(df, period=14):

    delta = df["close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df


# ==============================
# SCAN
# ==============================
files = list(DATA_DIR.glob("*.csv"))

for file in files:
    try:
        df = pd.read_csv(file)

        if len(df) < 30:
            continue

        # 🔥 standardize columns
        df.columns = [c.lower() for c in df.columns]

        if "close" not in df.columns:
            continue

        df = calculate_rsi(df)

        df = df.dropna(subset=["rsi"])

        if df.empty:
            continue

        last = df.iloc[-1]
        rsi = last["rsi"]

        # ==========================
        # CONDITIONS
        # ==========================
        if rsi < 30:
            signal = "OVERSOLD"
        elif rsi > 70:
            signal = "OVERBOUGHT"
        else:
            continue

        results.append({
            "SYMBOL": file.stem,
            "RSI": round(rsi, 2),
            "Signal": signal
        })

        print(f"{file.stem} → {signal}")

    except Exception as e:
        print(f"ERROR {file.stem}: {e}")

# ==============================
# SAVE
# ==============================
df_out = pd.DataFrame(results)
df_out.to_csv(OUT_FILE, index=False)

print(f"\nTotal: {len(results)}")
print(f"Saved → {OUT_FILE}")