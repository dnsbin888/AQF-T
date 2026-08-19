@echo off
REM AQF-T Daily Runner — Windows Task Scheduler entry
REM Trigger: Daily 15:30

cd /d D:\AQF-T\AQF-T_Production

echo [%date% %time%] AQF-T Daily Run START >> logs\scheduler.log

"C:\Program Files\Python312\python.exe" run_daily.py --source real >> logs\scheduler.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] SUCCESS >> logs\scheduler.log
    echo [%date% %time%] Shadow v3 bridge START >> logs\scheduler.log
    "C:\Program Files\Python312\python.exe" D:\quant_framework\scripts\shadow_aqft_v3.py --once >> logs\scheduler.log 2>&1
) else (
    echo [%date% %time%] FAILED (exit=%ERRORLEVEL%) >> logs\scheduler.log
)
