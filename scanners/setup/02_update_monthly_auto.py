import pandas as pd
from pathlib import Path

print("MONTHLY QUICK UPDATE (EXPIRY-BASED)\n")

# ============================================
# PATHS
# ============================================
FNO_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\fno_symbols.csv")
EXPIRY_FILE = Path(r"H:\CANDLE-LAB-MONTHLY\config\nse_expiries_final.csv")

EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
INDICES_DIR = Path(r"H:\MarketForge\data\master\Indices_master")

OUT_DIR = Path(r"H:\CANDLE-LAB-MONTHLY\data\monthly")

# ============================================
# LOAD F&O SYMBOLS
# ============================================
fno_df = pd.read_csv(FNO_FILE)
FNO_SYMBOLS = set(fno_df["SYMBOL"].astype(str).str.upper().str.strip())

# ============================================
# LOAD MONTHLY EXPIRIES
# ============================================
expiry_df = pd.read_csv(EXPIRY_FILE)
expiry_df.columns = expiry_df.columns.str.strip().str.upper()
expiry_df["EXPIRY_DATE"] = pd.to_datetime(expiry_df["EXPIRY_DATE"], errors="coerce")
expiry_df = expiry_df.dropna(subset=["EXPIRY_DATE"]).sort_values("EXPIRY_DATE")

EXPIRY_DATES = list(expiry_df["EXPIRY_DATE"].drop_duplicates())
EXPIRY_INDEX = pd.DatetimeIndex(EXPIRY_DATES)


# ============================================
# FUNCTION: MAP TRADE DATE TO EXPIRY
# ============================================
def assign_expiry_bucket(dates):
    positions = EXPIRY_INDEX.searchsorted(pd.DatetimeIndex(dates), side="left")

    mapped = pd.Series(pd.NaT, index=dates.index, dtype="datetime64[ns]")
    valid = positions < len(EXPIRY_INDEX)

    if valid.any():
        mapped.loc[valid] = EXPIRY_INDEX.take(positions[valid]).to_numpy()

    return mapped


# ============================================
# FUNCTION: UPDATE ONLY RECENT EXPIRY MONTHS
# ============================================
def update_last_month(file, symbol, tag):
    try:
        out_file = OUT_DIR / f"{symbol}.csv"

        if not out_file.exists():
            print(f"Skipped {symbol} (no historical file)")
            return

        old = pd.read_csv(out_file)
        old.columns = old.columns.str.strip().str.upper()
        old["DATE"] = pd.to_datetime(old["DATE"], errors="coerce")
        old = old.dropna(subset=["DATE"]).sort_values("DATE")

        if old.empty:
            print(f"Skipped {symbol} (empty historical file)")
            return

        last_saved_expiry = old["DATE"].max()

        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.upper()

        if "DATE" in df.columns:
            date_col = "DATE"
        elif "TRADE_DATE" in df.columns:
            date_col = "TRADE_DATE"
        else:
            print(f"Skipped {symbol} (no DATE column)")
            return

        required = {"OPEN", "HIGH", "LOW", "CLOSE"}
        if not required.issubset(df.columns):
            print(f"Skipped {symbol} (missing OHLC columns)")
            return

        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col]).sort_values(date_col)

        if "VOLUME" not in df.columns:
            df["VOLUME"] = 0

        recent_start = last_saved_expiry - pd.DateOffset(days=45)
        df = df[df[date_col] >= recent_start]

        if df.empty:
            print(f"No data -> {symbol}")
            return

        df["EXPIRY_DATE"] = assign_expiry_bucket(df[date_col])
        df = df.dropna(subset=["EXPIRY_DATE"])
        df = df[df["EXPIRY_DATE"] >= last_saved_expiry]

        if df.empty:
            print(f"No new expiry bucket -> {symbol}")
            return

        monthly_rows = []

        for expiry_date, group in df.groupby("EXPIRY_DATE"):
            group = group.sort_values(date_col)

            monthly_rows.append(
                {
                    "DATE": expiry_date,
                    "OPEN": group["OPEN"].iloc[0],
                    "HIGH": group["HIGH"].max(),
                    "LOW": group["LOW"].min(),
                    "CLOSE": group["CLOSE"].iloc[-1],
                    "VOLUME": group["VOLUME"].sum(),
                }
            )

        monthly = pd.DataFrame(monthly_rows)

        if monthly.empty:
            print(f"Empty monthly -> {symbol}")
            return

        monthly["DATE"] = pd.to_datetime(monthly["DATE"])
        monthly["SYMBOL"] = symbol
        monthly["TYPE"] = tag
        monthly = monthly[
            ["DATE", "SYMBOL", "TYPE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
        ].sort_values("DATE")

        old = old[old["DATE"] < monthly["DATE"].min()]

        final = pd.concat([old, monthly], ignore_index=True)
        final.sort_values("DATE", inplace=True)

        final.to_csv(out_file, index=False)

        print(f"Updated {symbol}")

    except Exception as e:
        print(f"ERROR: {file} | {e}")


# ============================================
# PROCESS EQUITY
# ============================================
print("Processing equity update\n")

for file in EQUITY_DIR.glob("*.csv"):
    symbol = file.stem.upper()

    if symbol not in FNO_SYMBOLS:
        continue

    update_last_month(file, symbol, "EQUITY")

# ============================================
# PROCESS INDICES
# ============================================
print("\nProcessing indices update\n")

for file in INDICES_DIR.glob("*.csv"):
    symbol = file.stem.upper()
    update_last_month(file, symbol, "INDEX")

# ============================================
# DONE
# ============================================
print("\nLAST MONTH UPDATE COMPLETE (EXPIRY-BASED)")
