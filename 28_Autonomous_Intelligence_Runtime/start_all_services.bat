@echo off
echo ============================================================
echo   AQF-T V3.1.1 Distributed Intelligence Runtime
echo ============================================================
echo.
echo   Starting 8 independent services...
echo.

cd /d D:\AQF-T\28_Autonomous_Intelligence_Runtime

echo   [1/8] Service Registry          :8100
start "AQFT-Registry"        python service_registry\registry.py
timeout /t 1 >nul

echo   [2/8] Agent Council             :8101
start "AQFT-Agent"           python agent_service\server.py
timeout /t 1 >nul

echo   [3/8] World Model               :8102
start "AQFT-WorldModel"      python world_model_service\server.py
timeout /t 1 >nul

echo   [4/8] Decision Engine           :8103
start "AQFT-Decision"        python decision_service\server.py
timeout /t 1 >nul

echo   [5/8] Risk Engine (Kill Switch) :8104
start "AQFT-Risk"            python risk_service\server.py
timeout /t 1 >nul

echo   [6/8] Memory Service            :8105
start "AQFT-Memory"          python memory_service\server.py
timeout /t 1 >nul

echo   [7/8] Market Data Service       :8106
echo         (standby)
timeout /t 1 >nul

echo   [8/8] Gateway + Console         :8080
start "AQFT-Gateway"         python ..\..\apps\console\server.py
timeout /t 3 >nul

echo.
echo ============================================================
echo   AQF-T Distributed Runtime ONLINE
echo.
echo   Console:  http://127.0.0.1:8080
echo   API Docs: http://127.0.0.1:8080/docs
echo.
echo   Services:
echo     Registry:  http://127.0.0.1:8100
echo     Agent:     http://127.0.0.1:8101
echo     World:     http://127.0.0.1:8102
echo     Decision:  http://127.0.0.1:8103
echo     Risk:      http://127.0.0.1:8104
echo     Memory:    http://127.0.0.1:8105
echo ============================================================
echo.
echo   Press Ctrl+C in each window to stop.
echo   Or run: taskkill /F /FI "WINDOWTITLE eq AQFT-*"
echo.
