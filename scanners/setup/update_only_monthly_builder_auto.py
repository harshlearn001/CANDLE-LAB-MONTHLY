import pandas as pd
from pathlib import Path

print("⚡ MONTHLY QUICK UPDATE (HOLIDAY SMART)\n")

# ============================================
# PATHS
# ============================================
FNO_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\fno_symbols.csv")

EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
INDICES_DIR = Path(r"H:\MarketForge\data\master\Indices_master")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

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

# ============================================
# FUNCTION: GET LAST TRADING DAY
# ============================================
def get_last_trading_day(group):
    valid = group[~group.index.isin(HOLIDAYS)]
    if valid.empty:
        return None
    return valid.iloc[-1]

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

        # LOAD DAILY
        df = pd.read_csv(file)

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
        # LAST ~2 MONTHS DATA
        # ============================================
        df = df[df.index >= last_month - pd.DateOffset(days=40)]

        if df.empty:
            print(f"⚠ No data → {symbol}")
            return

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
                "DATE": last_row.name,               # 🔥 correct trading date
                "OPEN": g["OPEN"].iloc[0],
                "HIGH": g["HIGH"].max(),
                "LOW": g["LOW"].min(),
                "CLOSE": last_row["CLOSE"],
                "VOLUME": g["VOLUME"].sum() if "VOLUME" in g.columns else 0
            })

        monthly = pd.DataFrame(monthly_rows)

        if monthly.empty:
            print(f"⚠ Empty monthly → {symbol}")
            return

        # ============================================
        # FORMAT
        # ============================================
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
# PROCESS EQUITY
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
print("\n🔥 LAST MONTH UPDATE COMPLETE (HOLIDAY SMART)")