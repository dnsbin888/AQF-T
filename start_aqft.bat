@echo off
echo ============================================================
echo   AQF-T V3.1.0 — Autonomous Quantitative Fusion Trading System
echo ============================================================
echo.
echo   Starting AQF-T Intelligence Console...
echo   Open: http://127.0.0.1:8080
echo.
echo   API Docs: http://127.0.0.1:8080/docs
echo ============================================================
echo.

cd /d D:\AQF-T
python -m uvicorn apps.console.server:app --host 127.0.0.1 --port 8080 --reload
