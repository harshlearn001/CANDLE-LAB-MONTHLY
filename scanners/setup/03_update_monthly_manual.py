import pandas as pd
from pathlib import Path

print("⚡ MONTHLY QUICK UPDATE (LAST MONTH ONLY)\n")

# ============================================
# MODE SETTINGS
# ============================================
USE_MANUAL_MONTH = True     # 👈 Control month range
USE_RUN_DATE = True         # 👈 Save today's date instead of month end
USE_LAST_TRADING_DAY = False  # 👈 Best option for accuracy

# ============================================
# MANUAL MONTH INPUT
# ============================================
MONTH_START = "2026-03-01"
MONTH_END   = "2026-03-30"   # last trading day

MONTH_START = pd.to_datetime(MONTH_START)
MONTH_END   = pd.to_datetime(MONTH_END)

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

        if not out_file.exists():
            print(f"⚠ Skipped {symbol} (no historical file)")
            return

        old = pd.read_csv(out_file)
        old["DATE"] = pd.to_datetime(old["DATE"])

        last_month = old["DATE"].max()

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
        # DATE FILTER
        # ============================================
        if USE_MANUAL_MONTH:
            df = df[(df.index >= MONTH_START) & (df.index <= MONTH_END)]
        else:
            df = df[df.index >= last_month - pd.DateOffset(days=35)]

        if df.empty:
            print(f"⚠ No data for {symbol}")
            return

        # ============================================
        # DECIDE FINAL DATE
        # ============================================
        if USE_LAST_TRADING_DAY:
            FINAL_DATE = df.index.max()
        elif USE_RUN_DATE:
            FINAL_DATE = pd.Timestamp.today().normalize()
        else:
            FINAL_DATE = MONTH_END

        # ============================================
        # BUILD MONTHLY
        # ============================================
        monthly = pd.DataFrame()

        if USE_MANUAL_MONTH:
            monthly.loc[0, "DATE"] = FINAL_DATE
            monthly.loc[0, "OPEN"] = df["OPEN"].iloc[0]
            monthly.loc[0, "HIGH"] = df["HIGH"].max()
            monthly.loc[0, "LOW"] = df["LOW"].min()
            monthly.loc[0, "CLOSE"] = df["CLOSE"].iloc[-1]

            if "VOLUME" in df.columns:
                monthly.loc[0, "VOLUME"] = df["VOLUME"].sum()
            else:
                monthly.loc[0, "VOLUME"] = 0

        else:
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

        # ============================================
        # FINAL FORMAT
        # ============================================
        monthly["DATE"] = pd.to_datetime(monthly["DATE"])
        monthly["SYMBOL"] = symbol
        monthly["TYPE"] = tag

        monthly = monthly[
            ["DATE", "SYMBOL", "TYPE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
        ]

        # ============================================
        # REMOVE OLD MONTH
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