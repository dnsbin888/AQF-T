@echo off
setlocal enabledelayedexpansion
title AQF-T One-Click Launcher v1.1 (port 8081)

:: ============================================================
::  AQF-T One-Click Launcher v1.1 - ASCII only (codepage-safe)
::  Dashboard + System Check + optional Data Refresh
::  Port 8081 (QianLong owns 8080 - launch.bat never touches it)
:: ============================================================

set "PYTHON=C:\Program Files\Python312\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"
set "AQFT_DIR=D:\AQF-T\AQF-T_Production"
set "DASHBOARD_PORT=8081"

:: -- Check Python --
"%PYTHON%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found at: %PYTHON%
    echo         Please check Python installation
    pause
    exit /b 1
)

echo.
echo   ============================================================
echo     [*] AQF-T Unified Launcher v1.1 - ASCII-safe
echo   ============================================================
echo.
echo     Mode: %~1
echo.

:: -- Step 1: Kill only AQF-T processes on port 8081 --
echo   [1/6] Stopping old processes...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":%DASHBOARD_PORT% " ^| findstr LISTENING') do (
    echo         Killing PID %%a (port %DASHBOARD_PORT%)
    taskkill /F /PID %%a >nul 2>&1
)
echo         Done.

:: -- Step 2: Skip bytecode cleanup --
::   Python auto-invalidates .pyc; skip cold recompile
echo   [2/6] Skipping bytecode cleanup (Python auto-invalidates .pyc)...
echo         Done.

:: -- Step 3: System check --
echo   [3/6] Running system check...
cd /d "%AQFT_DIR%"
"%PYTHON%" check.py >nul 2>&1
if %errorlevel% neq 0 (
    echo         [WARN] Some checks failed - see check_result.txt
    type check_result.txt 2>nul
) else (
    echo         [OK] All modules pass
)

:: -- Step 4: Refresh market data (optional) --
if /i "%~1"=="--run-daily" goto :run_daily_now
echo   [4/6] Skipping EOD pipeline (15:30 scheduler); use --run-daily to force
goto :step5

:run_daily_now
echo   [4/6] Refreshing market data (run_daily.py --source real)...
"%PYTHON%" run_daily.py --source real >nul 2>&1
if errorlevel 1 (
    echo         [WARN] Data refresh failed - dashboard will show cached data
    echo         Check: logs\scheduler.log
) else (
    echo         [OK] Market data updated
)

:step5

:: -- Step 5: Start Dashboard (same construct as main launcher Step 9) --
echo   [5/6] Starting Dashboard on port %DASHBOARD_PORT%...
set "PYTHONUTF8=1"
start "AQF-T-Dashboard" /min /D "%AQFT_DIR%" "%PYTHON%" -X utf8 dashboard.py

:: -- Step 6: Wait for ready --
echo   [6/6] Waiting for Dashboard (up to 30s)...
set "READY=0"
for /L %%i in (1,1,15) do (
    ping -n 3 127.0.0.1 >nul
    curl -s -o nul http://localhost:%DASHBOARD_PORT% 2>nul
    if !errorlevel! equ 0 (
        set "READY=1"
        set /a "SECS=%%i*2"
        goto :dash_up
    )
    <nul set /p ".=."
)
:dash_up

if %READY% equ 1 (
    echo         [OK] Dashboard ready in !SECS!s on port %DASHBOARD_PORT%
) else (
    echo         [WARN] Dashboard not responding yet
    echo         Check: http://localhost:%DASHBOARD_PORT%
)

:: -- Done --
echo.
echo   ============================================================
echo     [*] AQF-T Dashboard Ready
echo   ============================================================
echo.
echo     Dashboard:  http://localhost:%DASHBOARD_PORT%
echo     Scheduler:  schtasks /query /tn "AQF-T Daily Run"
echo.
echo     Close this window to stop all AQF-T services
echo   ============================================================
echo.

ping -n 3 127.0.0.1 >nul
start http://localhost:%DASHBOARD_PORT%
pause
exit /b 0
