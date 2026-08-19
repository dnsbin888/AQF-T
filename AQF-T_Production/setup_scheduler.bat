@echo off
REM AQF-T Daily Scheduler Setup — 以管理员身份运行此文件

cd /d D:\AQF-T\AQF-T_Production

echo === AQF-T Scheduler Setup ===
echo.

REM 删除旧任务
schtasks /delete /tn "AQF-T Daily Run" /f 2>nul

REM 创建新任务：每天 15:30 触发
schtasks /create ^
  /tn "AQF-T Daily Run" ^
  /tr "D:\AQF-T\AQF-T_Production\run_daily.bat" ^
  /sc daily ^
  /st 15:30 ^
  /ru %USERNAME% ^
  /rl limited ^
  /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === SUCCESS ===
    echo Task 'AQF-T Daily Run' installed.
    echo Schedule: Daily at 15:30
    echo.
    echo Verify:
    echo   schtasks /query /tn "AQF-T Daily Run"
    echo   schtasks /run /tn "AQF-T Daily Run"
) else (
    echo.
    echo === FAILED ===
    echo Error code: %ERRORLEVEL%
    echo Make sure you run this as Administrator.
)

pause
