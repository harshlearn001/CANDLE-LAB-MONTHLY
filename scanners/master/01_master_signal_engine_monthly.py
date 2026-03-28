import pandas as pd
from pathlib import Path
from datetime import datetime

print("MASTER SIGNAL ENGINE (MONTHLY)\n")

BASE = Path(r"H:\CANDLE-LAB-MONTHLY\analysis\equity\signals")

today = datetime.now().strftime("%Y-%m-%d")

# ==============================
# SAFE LOAD FUNCTION
# ==============================
def load(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

# ==============================
# LOAD ALL SIGNAL FILES
# ==============================
adx = load(BASE / "adx_monthly" / f"monthly_adx_{today}.csv")
rsi = load(BASE / "rsi_monthly" / f"monthly_rsi_{today}.csv")

bull_eng = load(BASE / "engulfing_monthly" / f"monthly_bullish_engulfing_{today}.csv")
bear_eng = load(BASE / "engulfing_monthly" / f"monthly_bearish_engulfing_{today}.csv")

hammer = load(BASE / "hammer_monthly" / f"monthly_hammer_confirmed_{today}.csv")
hanging = load(BASE / "hangingman_monthly" / f"monthly_hangingman_confirmed_{today}.csv")

shooting = load(BASE / "shooting_star_monthly" / f"monthly_shooting_star_{today}.csv")
gravestone = load(BASE / "gravestone_monthly" / f"monthly_gravestone_{today}.csv")

nr7 = load(BASE / "nr7_monthly" / f"monthly_nr7_{today}.csv")
inside = load(BASE / "insidebar_monthly" / f"monthly_insidebar_{today}.csv")

div_bull = load(BASE / "rsi_divergence_monthly" / f"monthly_bullish_divergence_{today}.csv")
div_bear = load(BASE / "rsi_divergence_monthly" / f"monthly_bearish_divergence_{today}.csv")

morning = load(BASE / "morning_star_monthly" / f"monthly_morning_star_{today}.csv")
piercing = load(BASE / "piercing_pattern_monthly" / f"monthly_piercing_pattern_{today}.csv")

# ==============================
# COL FIX (VERY IMPORTANT)
# ==============================
def fix_col(df):
    if not df.empty:
        if "SYMBOL" in df.columns:
            df.rename(columns={"SYMBOL": "Symbol"}, inplace=True)
    return df

dfs = [adx, rsi, bull_eng, bear_eng, hammer, hanging,
       shooting, gravestone, nr7, inside,
       div_bull, div_bear, morning, piercing]

dfs = [fix_col(d) for d in dfs]

# ==============================
# ALL SYMBOLS
# ==============================
symbols = set()

for df in dfs:
    if not df.empty and "Symbol" in df.columns:
        symbols.update(df["Symbol"].tolist())

print("Total symbols:", len(symbols))

# ==============================
# SCORING ENGINE
# ==============================
results = []

for sym in symbols:

    score = 0
    reasons = []

    # --------------------------
    # ADX
    # --------------------------
    if not adx.empty:
        row = adx[adx["Symbol"] == sym]
        if not row.empty:
            sig = row.iloc[0]["Signal"]
            if "UPTREND" in sig:
                score += 3
                reasons.append("ADX_UP")
            elif "DOWNTREND" in sig:
                score -= 3
                reasons.append("ADX_DOWN")

    # --------------------------
    # RSI
    # --------------------------
    if not rsi.empty:
        row = rsi[rsi["Symbol"] == sym]
        if not row.empty:
            if row.iloc[0]["Signal"] == "OVERSOLD":
                score += 2
                reasons.append("RSI_OS")
            elif row.iloc[0]["Signal"] == "OVERBOUGHT":
                score -= 2
                reasons.append("RSI_OB")

    # --------------------------
    # DIVERGENCE
    # --------------------------
    if not div_bull.empty and sym in div_bull["Symbol"].values:
        score += 3
        reasons.append("BULL_DIV")

    if not div_bear.empty and sym in div_bear["Symbol"].values:
        score -= 3
        reasons.append("BEAR_DIV")

    # --------------------------
    # STRONG PATTERNS
    # --------------------------
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

    # --------------------------
    # WEAK PATTERNS
    # --------------------------
    if not shooting.empty and sym in shooting["Symbol"].values:
        score -= 2
        reasons.append("SHOOTING")

    if not gravestone.empty and sym in gravestone["Symbol"].values:
        score -= 2
        reasons.append("GRAVESTONE")

    # --------------------------
    # BREAKOUT / COMPRESSION
    # --------------------------
    if not nr7.empty and sym in nr7["Symbol"].values:
        score += 2
        reasons.append("NR7")

    if not inside.empty and sym in inside["Symbol"].values:
        score += 1
        reasons.append("INSIDE")

    # ==========================
    # FINAL DECISION
    # ==========================
    if score >= 4:
        signal = "BUY"
    elif score <= -4:
        signal = "SELL"
    else:
        continue

    results.append({
        "Symbol": sym,
        "Score": score,
        "Signal": signal,
        "Reasons": ",".join(reasons)
    })

# ==============================
# SAVE OUTPUT
# ==============================
out = pd.DataFrame(results)

OUT_DIR = BASE / "master"
OUT_DIR.mkdir(exist_ok=True)

OUT_FILE = OUT_DIR / f"final_monthly_trades_{today}.csv"

if not out.empty:
    out = out.sort_values("Score", ascending=False)
    out.to_csv(OUT_FILE, index=False)

    print("\nFINAL MONTHLY TRADES")
    print(out.head(10))
    print("Saved →", OUT_FILE)

else:
    print("\nNo strong signals")