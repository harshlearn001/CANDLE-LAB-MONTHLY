@echo off

echo ======================================
echo 🚀 RUNNING MONTHLY SCANNERS
echo ======================================

REM ======================================
REM STEP 1: BUILD / UPDATE DATA
REM ======================================
echo.
echo 📦 Building Monthly Data...
python scanners/setup/02_update_monthly_auto.py

REM ======================================
REM STEP 2: CORE SIGNALS
REM ======================================
echo.
echo 📊 Running ADX...
python scanners/adx_monthly/01_adx_monthly.py

echo.
echo 📊 Running RSI...
python scanners/rsi_monthly/01_rsi_monthly.py

echo.
echo 📊 Running RSI Divergence...
python scanners/rsi_divergence_monthly/01_rsi_divergence_monthly.py

REM ======================================
REM STEP 3: PRICE ACTION PATTERNS
REM ======================================
echo.
echo 📈 Running Bullish Engulfing...
python scanners/engulfing_monthly/01_bullish_engulfing_monthly.py

echo.
echo 📉 Running Bearish Engulfing...
python scanners/engulfing_monthly/01_bearish_engulfing_monthly.py

echo.
echo 📈 Running Piercing Pattern...
python scanners/piercing_pattern_monthly/01_piercing_pattern_monthly.py

echo.
echo 📊 Running NR7...
python scanners/nr7_monthly/01_nr7_monthly.py

echo.
echo 📊 Running Inside Bar...
python scanners/insidebar_monthly/01_insidebar_monthly.py

REM ======================================
REM STEP 4: MASTER ENGINE
REM ======================================
echo.
echo 🧠 Running Master Signal Engine...
python scanners/master/01_master_signal_engine_monthly.py

REM ======================================
REM DONE
REM ======================================
echo.
echo ======================================
echo ✅ ALL SCANNERS COMPLETED SUCCESSFULLY
echo ======================================

pause
