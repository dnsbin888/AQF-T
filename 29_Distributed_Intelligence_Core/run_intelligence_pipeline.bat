@echo off
echo ============================================================
echo   AQF-T V3.2.0 Distributed Intelligence Core
echo ============================================================
echo.
echo   Starting Intelligence Pipeline...
echo   (Services must already be running — start_all_services.bat)
echo.

cd /d D:\AQF-T\29_Distributed_Intelligence_Core

echo   Running: Market Data Feed + Intelligence Pipeline
echo.
python -c "
import asyncio, threading, time
from data_pipeline.market_data_feed import MarketDataSimulator
from agent_orchestration.intelligence_pipeline import IntelligencePipeline

# Start market data in background
sim = MarketDataSimulator()
thread = threading.Thread(target=sim.start_stream, args=(3.0,), daemon=True)
thread.start()
time.sleep(0.5)

# Run intelligence pipeline
async def run():
    pipeline = IntelligencePipeline()
    for i in range(3):
        print(f'\n--- Pipeline Run {i+1}/3 ---')
        await pipeline.run(symbol='000300')
        await asyncio.sleep(5)
    print('\nPipeline complete. Market data feed continues in background.')

asyncio.run(run())
"
echo.
echo   Pipeline finished. Press Ctrl+C to stop data feed.
pause
