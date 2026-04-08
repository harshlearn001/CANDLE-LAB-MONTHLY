import pandas as pd
from pandas.errors import EmptyDataError
from pathlib import Path
from datetime import datetime

print("MASTER SIGNAL ENGINE (MONTHLY)\n")

BASE = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals")
today = datetime.now().strftime("%Y-%m-%d")


def load_latest(folder_name, pattern):
    folder = BASE / folder_name
    files = sorted(folder.glob(pattern))

    if not files:
        print(f"Missing signal file: {folder_name}/{pattern}")
        return pd.DataFrame()

    latest_file = max(files, key=lambda path: path.stat().st_mtime)

    try:
        df = pd.read_csv(latest_file)
        print(f"Loaded {latest_file.name}")
        return df
    except EmptyDataError:
        print(f"Empty signal file: {latest_file.name}")
        return pd.DataFrame()


def fix_col(df):
    if not df.empty and "SYMBOL" in df.columns:
        df = df.rename(columns={"SYMBOL": "Symbol"})
    return df


adx = fix_col(load_latest("adx_monthly", "monthly_adx_*.csv"))
rsi = fix_col(load_latest("rsi_monthly", "monthly_rsi_*.csv"))

bull_eng = fix_col(load_latest("engulfing_monthly", "monthly_bullish_engulfing_*.csv"))
bear_eng = fix_col(load_latest("engulfing_monthly", "monthly_bearish_engulfing_*.csv"))

hammer = fix_col(load_latest("hammer_confirmed_monthly", "monthly_hammer_confirmed_*.csv"))
hanging = fix_col(load_latest("hangingman_monthly", "monthly_hangingman_confirmed_*.csv"))

shooting = fix_col(load_latest("shooting_star_monthly", "monthly_shooting_star_*.csv"))
gravestone = fix_col(load_latest("gravestone_monthly", "monthly_gravestone_*.csv"))

nr7 = fix_col(load_latest("nr7_monthly", "monthly_nr7_*.csv"))
inside = fix_col(load_latest("insidebar_monthly", "monthly_insidebar_*.csv"))

div_bull = fix_col(load_latest("rsi_divergence_monthly", "monthly_bullish_divergence_*.csv"))
div_bear = fix_col(load_latest("rsi_divergence_monthly", "monthly_bearish_divergence_*.csv"))

morning = fix_col(load_latest("morning_star_monthly", "monthly_morning_star_*.csv"))
piercing = fix_col(load_latest("piercing_pattern_monthly", "monthly_piercing_pattern_*.csv"))

dfs = [
    adx,
    rsi,
    bull_eng,
    bear_eng,
    hammer,
    hanging,
    shooting,
    gravestone,
    nr7,
    inside,
    div_bull,
    div_bear,
    morning,
    piercing,
]

symbols = set()

for df in dfs:
    if not df.empty and "Symbol" in df.columns:
        symbols.update(df["Symbol"].astype(str).tolist())

print("Total symbols:", len(symbols))

results = []

for sym in symbols:
    score = 0
    reasons = []

    if not adx.empty:
        row = adx[adx["Symbol"] == sym]
        if not row.empty:
            sig = str(row.iloc[0]["Signal"])
            if "UPTREND" in sig:
                score += 3
                reasons.append("ADX_UP")
            elif "DOWNTREND" in sig:
                score -= 3
                reasons.append("ADX_DOWN")

    if not rsi.empty:
        row = rsi[rsi["Symbol"] == sym]
        if not row.empty:
            sig = row.iloc[0]["Signal"]
            if sig == "OVERSOLD":
                score += 2
                reasons.append("RSI_OS")
            elif sig == "OVERBOUGHT":
                score -= 2
                reasons.append("RSI_OB")

    if not div_bull.empty and sym in div_bull["Symbol"].values:
        score += 3
        reasons.append("BULL_DIV")

    if not div_bear.empty and sym in div_bear["Symbol"].values:
        score -= 3
        reasons.append("BEAR_DIV")

    if not bull_eng.empty and sym in bull_eng["Symbol"].values:
        score += 3
        reasons.append("BULL_ENG")

    if not bear_eng.empty and sym in bear_eng["Symbol"].values:
        score -= 3
        reasons.append("BEAR_ENG")

    if not hammer.empty and sym in hammer["Symbol"].values:
        score += 3
        reasons.append("HAMMER")

    if not hanging.empty and sym in hanging["Symbol"].values:
        score -= 3
        reasons.append("HANGING")

    if not morning.empty and sym in morning["Symbol"].values:
        score += 3
        reasons.append("MORNING")

    if not piercing.empty and sym in piercing["Symbol"].values:
        score += 3
        reasons.append("PIERCING")

    if not shooting.empty and sym in shooting["Symbol"].values:
        score -= 2
        reasons.append("SHOOTING")

    if not gravestone.empty and sym in gravestone["Symbol"].values:
        score -= 2
        reasons.append("GRAVESTONE")

    if not nr7.empty and sym in nr7["Symbol"].values:
        score += 2
        reasons.append("NR7")

    if not inside.empty and sym in inside["Symbol"].values:
        score += 1
        reasons.append("INSIDE")

    if score >= 4:
        signal = "BUY"
    elif score <= -4:
        signal = "SELL"
    else:
        continue

    results.append(
        {
            "Symbol": sym,
            "Score": score,
            "Signal": signal,
            "Reasons": ",".join(reasons),
        }
    )

out = pd.DataFrame(results)

OUT_DIR = BASE / "master"
OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / f"final_monthly_trades_{today}.csv"

if not out.empty:
    out = out.sort_values(["Score", "Symbol"], ascending=[False, True])
    out.to_csv(OUT_FILE, index=False)

    print("\nFINAL MONTHLY TRADES")
    print(out.head(10))
    print("Saved ->", OUT_FILE)
else:
    print("\nNo strong signals")
