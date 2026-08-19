@echo off
chcp 65001 >nul 2>&1
title AQF-T File Lock
echo.
echo   ============================================================
echo     [*] AQF-T Production File Lock
echo   ============================================================
echo.

set "DIR=D:\AQF-T\AQF-T_Production"

:: Core production files — read-only
echo   Locking production core...
attrib +r "%DIR%\launch.bat"
attrib +r "%DIR%\dashboard.py"
attrib +r "%DIR%\run_daily.py"
attrib +r "%DIR%\run_daily.bat"
attrib +r "%DIR%\main.py"
attrib +r "%DIR%\paper_runner.py"
attrib +r "%DIR%\pipeline.py"
attrib +r "%DIR%\decision_core.py"
attrib +r "%DIR%\check.py"
attrib +r "%DIR%\setup_scheduler.bat"
attrib +r "%DIR%\data\market_data_adapter.py"

echo.
echo   [OK] 12 production files locked (read-only)
echo.
echo   Unlock: run unlock.bat
echo   ============================================================
pause
exit /b 0
