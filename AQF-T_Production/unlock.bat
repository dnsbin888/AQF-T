@echo off
chcp 65001 >nul 2>&1
title AQF-T File Unlock
echo.
echo   ============================================================
echo     [*] AQF-T Production File Unlock
echo   ============================================================
echo.

set "DIR=D:\AQF-T\AQF-T_Production"

echo   Unlocking production files...
attrib -r "%DIR%\launch.bat"
attrib -r "%DIR%\dashboard.py"
attrib -r "%DIR%\run_daily.py"
attrib -r "%DIR%\run_daily.bat"
attrib -r "%DIR%\main.py"
attrib -r "%DIR%\paper_runner.py"
attrib -r "%DIR%\pipeline.py"
attrib -r "%DIR%\decision_core.py"
attrib -r "%DIR%\check.py"
attrib -r "%DIR%\setup_scheduler.bat"
attrib -r "%DIR%\data\market_data_adapter.py"

echo.
echo   [OK] 12 files unlocked (writable)
echo.
echo   Lock: run lock.bat
echo   ============================================================
pause
exit /b 0
