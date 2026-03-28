import pandas as pd
from pathlib import Path

print("⚡ MONTHLY QUICK UPDATE (LAST MONTH ONLY)\n")

# ============================================
# PATHS
# ============================================
FNO_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\fno_symbols.csv")

EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
INDICES_DIR = Path(r"H:\MarketForge\data\master\Indices_master")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

# ============================================
# LOAD F&O SYMBOLS
# ============================================
fno_df = pd.read_csv(FNO_FILE)
FNO_SYMBOLS = set(fno_df["SYMBOL"].astype(str).str.upper().str.strip())

# ============================================
# FUNCTION: UPDATE ONLY LAST MONTH
# ============================================
def update_last_month(file, symbol, tag):
    try:
        out_file = OUT_DIR / f"{symbol}.csv"

        # Must exist (since history already built)
        if not out_file.exists():
            print(f"⚠ Skipped {symbol} (no historical file)")
            return

        # Load existing monthly
        old = pd.read_csv(out_file)
        old["DATE"] = pd.to_datetime(old["DATE"])

        last_month = old["DATE"].max()

        # Load daily data
        df = pd.read_csv(file)

        # Detect date column
        if "DATE" in df.columns:
            date_col = "DATE"
        elif "TRADE_DATE" in df.columns:
            date_col = "TRADE_DATE"
        else:
            print(f"⚠ Skipped {symbol} (no DATE column)")
            return

        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df.dropna(subset=[date_col], inplace=True)

        df.sort_values(date_col, inplace=True)
        df.set_index(date_col, inplace=True)

        # ============================================
        # ONLY LAST 2 MONTHS DATA
        # ============================================
        df = df[df.index >= last_month - pd.DateOffset(days=35)]

        # ============================================
        # BUILD MONTHLY
        # ============================================
        monthly = pd.DataFrame()
        monthly["OPEN"] = df["OPEN"].resample("ME").first()
        monthly["HIGH"] = df["HIGH"].resample("ME").max()
        monthly["LOW"] = df["LOW"].resample("ME").min()
        monthly["CLOSE"] = df["CLOSE"].resample("ME").last()

        if "VOLUME" in df.columns:
            monthly["VOLUME"] = df["VOLUME"].resample("ME").sum()
        else:
            monthly["VOLUME"] = 0

        monthly.dropna(inplace=True)
        monthly.reset_index(inplace=True)

        monthly.rename(columns={date_col: "DATE"}, inplace=True)

        monthly["SYMBOL"] = symbol
        monthly["TYPE"] = tag

        monthly = monthly[
            ["DATE", "SYMBOL", "TYPE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
        ]

        # ============================================
        # REMOVE LAST MONTH FROM OLD
        # ============================================
        old = old[old["DATE"] < monthly["DATE"].min()]

        # ============================================
        # MERGE
        # ============================================
        final = pd.concat([old, monthly])
        final.sort_values("DATE", inplace=True)

        final.to_csv(out_file, index=False)

        print(f"🔄 Updated {symbol}")

    except Exception as e:
        print(f"❌ ERROR: {file} | {e}")

# ============================================
# PROCESS EQUITY (F&O ONLY)
# ============================================
print("🔹 EQUITY UPDATE\n")

for file in EQUITY_DIR.glob("*.csv"):
    symbol = file.stem.upper()

    if symbol not in FNO_SYMBOLS:
        continue

    update_last_month(file, symbol, "EQUITY")

# ============================================
# PROCESS INDICES
# ============================================
print("\n🔹 INDICES UPDATE\n")

for file in INDICES_DIR.glob("*.csv"):
    symbol = file.stem.upper()

    update_last_month(file, symbol, "INDEX")

# ============================================
# DONE
# ============================================
print("\n🔥 LAST MONTH UPDATE COMPLETE")