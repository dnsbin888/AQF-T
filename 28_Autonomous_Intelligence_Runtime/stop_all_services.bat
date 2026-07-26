@echo off
echo Stopping all AQF-T services...
taskkill /F /FI "WINDOWTITLE eq AQFT-*" >nul 2>&1
echo All AQF-T services stopped.
