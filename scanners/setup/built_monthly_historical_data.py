import pandas as pd
from pathlib import Path

print("📊 BUILDING MONTHLY CANDLES (HOLIDAY SMART)\n")

# ============================================
# PATHS
# ============================================
FNO_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\fno_symbols.csv")

EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
INDICES_DIR = Path(r"H:\MarketForge\data\master\Indices_master")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 🔥 HOLIDAY FILE
HOLIDAY_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\nse_holidays_2026.csv")

# ============================================
# LOAD HOLIDAYS
# ============================================
holiday_df = pd.read_csv(HOLIDAY_FILE)
holiday_df["DATE"] = pd.to_datetime(holiday_df["DATE"])
HOLIDAYS = set(holiday_df["DATE"])

# ============================================
# LOAD F&O SYMBOLS
# ============================================
fno_df = pd.read_csv(FNO_FILE)
FNO_SYMBOLS = set(fno_df["SYMBOL"].astype(str).str.upper().str.strip())

print(f"Loaded F&O symbols: {len(FNO_SYMBOLS)}\n")

# ============================================
# FUNCTION: GET LAST TRADING DAY OF MONTH
# ============================================
def get_last_trading_day(group):
    valid = group[~group.index.isin(HOLIDAYS)]
    if valid.empty:
        return None
    return valid.iloc[-1]

# ============================================
# FUNCTION: BUILD MONTHLY (SMART)
# ============================================
def build_monthly(file, symbol, tag):
    try:
        df = pd.read_csv(file)

        # DATE COLUMN DETECTION
        if "DATE" in df.columns:
            date_col = "DATE"
        elif "TRADE_DATE" in df.columns:
            date_col = "TRADE_DATE"
        else:
            print(f"⚠ Skipped {symbol} (no DATE column)")
            return

        # CHECK OHLC
        required_cols = {"OPEN", "HIGH", "LOW", "CLOSE"}
        if not required_cols.issubset(df.columns):
            print(f"⚠ Skipped {symbol} (missing OHLC)")
            return

        # CLEAN
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df.dropna(subset=[date_col], inplace=True)

        df.sort_values(date_col, inplace=True)
        df.set_index(date_col, inplace=True)

        if "VOLUME" not in df.columns:
            df["VOLUME"] = 0

        # ============================================
        # GROUP BY MONTH (SMART)
        # ============================================
        df["MONTH"] = df.index.to_period("M")

        monthly_rows = []

        for _, g in df.groupby("MONTH"):
            g = g.sort_index()

            last_row = get_last_trading_day(g)
            if last_row is None:
                continue

            monthly_rows.append({
                "DATE": last_row.name,                 # 🔥 correct trading day
                "OPEN": g["OPEN"].iloc[0],
                "HIGH": g["HIGH"].max(),
                "LOW": g["LOW"].min(),
                "CLOSE": last_row["CLOSE"],            # 🔥 correct close
                "VOLUME": g["VOLUME"].sum()
            })

        monthly = pd.DataFrame(monthly_rows)

        if monthly.empty:
            print(f"⚠ Empty monthly → {symbol}")
            return

        # ADD SYMBOL + TYPE
        monthly["SYMBOL"] = symbol
        monthly["TYPE"] = tag

        monthly = monthly[
            ["DATE", "SYMBOL", "TYPE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
        ]

        # SAVE
        out_file = OUT_DIR / f"{symbol}.csv"
        monthly.sort_values("DATE", inplace=True)
        monthly.to_csv(out_file, index=False)

        print(f"✔ {symbol} ({tag}) done")

    except Exception as e:
        print(f"❌ ERROR: {file} | {e}")

# ============================================
# PROCESS EQUITY (F&O ONLY)
# ============================================
print("🔹 Processing EQUITY (F&O only)\n")

for file in EQUITY_DIR.glob("*.csv"):
    symbol = file.stem.upper()

    if symbol not in FNO_SYMBOLS:
        continue

    build_monthly(file, symbol, "EQUITY")

# ============================================
# PROCESS INDICES
# ============================================
print("\n🔹 Processing INDICES (ALL)\n")

for file in INDICES_DIR.glob("*.csv"):
    symbol = file.stem.upper()

    build_monthly(file, symbol, "INDEX")

# ============================================
# DONE
# ============================================
print("\n🔥 ALL MONTHLY DATA READY (HOLIDAY SMART)")
print("Saved in →", OUT_DIR)