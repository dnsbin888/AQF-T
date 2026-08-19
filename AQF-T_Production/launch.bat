@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title AQF-T 决策大脑 v1.0

:: ============================================================
::  AQF-T 一键启动 v1.0 — 集成 Dashboard + 系统检查 + 数据刷新
:: ============================================================

set "PYTHON=C:\Program Files\Python312\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"
set "AQFT_DIR=D:\AQF-T\AQF-T_Production"
set "DASHBOARD_PORT=8081"

:: ── Check Python ──
"%PYTHON%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found at: %PYTHON%
    echo         Please check Python installation
    pause
    exit /b 1
)

echo.
echo   ============================================================
echo     [*] AQF-T 决策大脑 v1.0 — Unified Launcher
echo   ============================================================
echo.
echo     Mode: %~1
echo.

:: ── Step 1: Kill old processes ──
echo   [1/6] Stopping old processes...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":%DASHBOARD_PORT% " ^| findstr LISTENING') do (
    echo         Killing PID %%a (port %DASHBOARD_PORT%)
    taskkill /F /PID %%a >nul 2>&1
)
echo         Done.

:: ── Step 2: Skip bytecode cleanup ──
::   Python 自动失效旧 .pyc, 冷编译浪费 30-60s (同 潜龙一键启动.bat Step2 结论)
echo   [2/6] Skipping bytecode cleanup (Python auto-invalidates .pyc)...
echo         Done.

:: ── Step 3: System check ──
echo   [3/6] Running system check...
cd /d "%AQFT_DIR%"
"%PYTHON%" check.py >nul 2>&1
if %errorlevel% neq 0 (
    echo         [WARN] Some checks failed — see check_result.txt
    type check_result.txt 2>nul
) else (
    echo         [OK] All modules pass
)

:: ── Step 4: Refresh market data (optional, default skip) ──
::   EOD 管线由 15:30 计划任务 run_daily.bat 负责; 启动时不重复跑 (~58s)。
::   如需启动即刷新:  launch.bat --run-daily
if /i "%~1"=="--run-daily" (
    echo   [4/6] Refreshing market data (run_daily.py --source real)...
    "%PYTHON%" run_daily.py --source real >nul 2>&1
    if !errorlevel! neq 0 (
        echo         [WARN] Data refresh failed — dashboard will show cached data
        echo         Check: logs\scheduler.log
    ) else (
        echo         [OK] Market data updated
    )
) else (
    echo   [4/6] Skipping EOD pipeline (15:30 计划任务负责); use --run-daily to force
)

:: ── Step 5: Start Dashboard ──
echo   [5/6] Starting Dashboard on port %DASHBOARD_PORT%...
set "PYTHONUTF8=1"
start "AQFT-Dashboard" cmd /c "chcp 65001 >nul && title AQF-T Dashboard :%DASHBOARD_PORT% && set PYTHONUTF8=1 && cd /d %AQFT_DIR% && "%PYTHON%" dashboard.py && pause"

:: ── Step 6: Wait for ready ──
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

:: ── Done ──
echo.
echo   ============================================================
echo     [*] AQF-T 决策大脑 v1.0 — Ready
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
