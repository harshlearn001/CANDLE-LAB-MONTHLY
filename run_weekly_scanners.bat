@echo off

echo ======================================
echo   CANDLE-LAB MONTHLY PIPELINE
echo ======================================

call conda activate TradeSense

REM ======================================
REM BUILD MONTHLY DATA
REM ======================================
echo.
echo [BUILD MONTHLY DATA]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\setup
#python built_monthly_historical_data.py
python update_only_monthly_builder.py

REM ======================================
REM TREND + MOMENTUM
REM ======================================
echo.
echo [MONTHLY ADX]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\adx_monthly
python 01_adx_monthly.py

echo.
echo [MONTHLY RSI]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\rsi_monthly
python 01_rsi_monthly.py

echo.
echo [MONTHLY RSI DIVERGENCE]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\rsi_divergence_monthly
python 01_rsi_divergence_monthly.py

REM ======================================
REM REVERSAL PATTERNS
REM ======================================
echo.
echo [MONTHLY ENGULFING]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\engulfing_monthly
python 01_bullish_engulfing_monthly.py
python 02_bearish_engulfing_monthly.py

echo.
echo [MONTHLY HAMMER]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\hammer_monthly
python 01_hammer_confirmed_monthly.py

echo.
echo [MONTHLY HANGING MAN]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\hangingman_monthly
python 01_hangingman_confirmed_monthly.py

echo.
echo [MONTHLY SHOOTING STAR]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\shooting_star_monthly
python 01_shooting_star_monthly.py

echo.
echo [MONTHLY GRAVESTONE]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\gravestone_monthly
python 01_gravestone_monthly.py

echo.
echo [MONTHLY MORNING STAR]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\morning_star_monthly
python 01_morning_star_monthly.py

echo.
echo [MONTHLY PIERCING PATTERN]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\piercing_pattern_monthly
python 01_piercing_pattern_monthly.py

echo.
echo [MONTHLY HARAMI]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\harami_monthly
python 01_harami_monthly.py

REM ======================================
REM BREAKOUT / VOLATILITY
REM ======================================
echo.
echo [MONTHLY INSIDE BAR]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\insidebar_monthly
python 01_insidebar_monthly.py

echo.
echo [MONTHLY LONG LEGGED DOJI]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\longleg_doji_monthly
python 01_longleg_doji_monthly.py

echo.
echo [MONTHLY SMALL DOJI]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\doji_monthly
python 01_small_doji_monthly.py

echo.
echo [MONTHLY NR7]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\nr7_monthly
python 01_nr7_monthly.py

REM ======================================
REM MASTER ENGINE
REM ======================================
echo.
echo [MASTER ENGINE]
cd /d H:\CANDLE-LAB-MONTHLY\scanners\master
python 01_master_signal_engine_monthly.py

REM ======================================
REM DONE
REM ======================================
echo.
echo ======================================
echo   MONTHLY PIPELINE COMPLETED
echo ======================================

pause