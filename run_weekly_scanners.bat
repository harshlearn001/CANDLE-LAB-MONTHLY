@echo off

echo ======================================
echo RUNNING MONTHLY SCANNERS
echo ======================================

echo.
echo Building Monthly Data...
python scanners/setup/02_update_monthly_auto.py

echo.
echo Running ADX...
python scanners/adx_monthly/01_adx_monthly.py

echo.
echo Running RSI...
python scanners/rsi_monthly/01_rsi_monthly.py

echo.
echo Running RSI Divergence...
python scanners/rsi_divergence_monthly/01_rsi_divergence_monthly.py

echo.
echo Running Bullish Engulfing...
python scanners/engulfing_monthly/01_bullish_engulfing_monthly.py

echo.
echo Running Bearish Engulfing...
python scanners/engulfing_monthly/01_bearish_engulfing_monthly.py

echo.
echo Running Hammer Confirmed...
python scanners/hammer_monthly/01_hammer_confirmed_monthly.py

echo.
echo Running Hanging Man Confirmed...
python scanners/hangingman_monthly/01_hangingman_confirmed_monthly.py

echo.
echo Running Shooting Star...
python scanners/shooting_star_monthly/01_shooting_star_monthly.py

echo.
echo Running Gravestone...
python scanners/gravestone_monthly/01_gravestone_monthly.py

echo.
echo Running Morning Star...
python scanners/morningstar_monthly/01_morningstar_monthly.py

echo.
echo Running Piercing Pattern...
python scanners/piercing_pattern_monthly/01_piercing_pattern_monthly.py

echo.
echo Running NR7...
python scanners/nr7_monthly/01_nr7_monthly.py

echo.
echo Running Inside Bar...
python scanners/Insidebar_monthly/01_Insidebar_monthly.py

echo.
echo Running Master Signal Engine...
python scanners/master/01_master_signal_engine_monthly.py

echo.
echo ======================================
echo ALL SCANNERS COMPLETED
echo ======================================

pause
