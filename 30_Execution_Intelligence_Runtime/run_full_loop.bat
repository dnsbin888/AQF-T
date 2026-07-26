@echo off
echo ============================================================
echo   AQF-T V3.3.0 Full Intelligence Loop
echo ============================================================
echo.
echo   Think -^> Decide -^> Execute -^> Simulate -^> Learn
echo   (Services must be running: start_all_services.bat)
echo.

cd /d D:\AQF-T\30_Execution_Intelligence_Runtime

echo   Starting execution services...
start "AQFT-Execution" python execution_engine\server.py
start "AQFT-Simulation" python simulation_engine\server.py
start "AQFT-Portfolio" python portfolio_manager\server.py
timeout /t 3 >nul

echo.
echo   Running Full Intelligence Loop (3 iterations)...
python -c "
import asyncio, httpx, random
from datetime import datetime

SYMBOLS = ['000300', '600519', '300750']

async def full_loop():
    async with httpx.AsyncClient(timeout=10.0) as c:
        for i in range(3):
            symbol = random.choice(SYMBOLS)
            print(f'\n=== Loop {i+1}/3: {symbol} ===')

            # 1. World Model
            r = await c.get('http://127.0.0.1:8102/world/state')
            world = r.json()
            print(f'  World:  {world[\"regime\"]}')

            # 2. Agent Council
            r = await c.post('http://127.0.0.1:8101/agents/coordinate', json={'world': world})
            consensus = r.json()
            print(f'  Agent:  {consensus[\"supervisor_decision\"]}')

            # 3. Decision
            r = await c.post('http://127.0.0.1:8103/decision/evaluate', json={'world_state': world})
            decision = r.json()
            print(f'  Decide: {decision[\"action\"]} (conf={decision[\"confidence\"]})')

            # 4. Risk
            r = await c.post('http://127.0.0.1:8104/risk/check', json={'decision': decision})
            risk = r.json()
            marker = '✅' if risk['decision']=='APPROVE' else '⚠️' if risk['decision']=='ADJUST' else '❌'
            print(f'  Risk:   {marker} {risk[\"decision\"]}')

            # 5. Execution
            price = random.uniform(50, 200)
            r = await c.post('http://127.0.0.1:8110/execution/execute', json={
                'symbol': symbol, 'action': decision['action'],
                'quantity': random.choice([100,200,500]),
                'price': price, 'risk_decision': risk['decision']
            })
            order = r.json()
            print(f'  Order:  {order[\"order\"][\"order_id\"]} ({order[\"status\"]})')

            # 6. Simulation (if approved)
            if risk['decision'] != 'REJECT' and order['status'] == 'CREATED':
                r = await c.post('http://127.0.0.1:8111/simulation/fill', json=order['order'])
                fill = r.json()
                print(f'  Sim:    {fill[\"status\"]} @ {fill.get(\"fill_price\",\"?\")} (slip={fill.get(\"slippage\",0)}%)')

                # 7. Portfolio update
                r = await c.post('http://127.0.0.1:8112/portfolio/update', json=fill)
                pf = r.json()
                print(f'  Port:   value={pf[\"total_value\"]:.0f}')

            # 8. Memory
            await c.post('http://127.0.0.1:8105/memory/store', json={
                'id': f'EXP-{datetime.now().strftime(\"%H%M%S\")}',
                'world': world.get('regime',''),
                'action': decision.get('action',''),
                'risk': risk.get('decision',''),
                'timestamp': datetime.now().isoformat()
            })
            print(f'  Memory: stored')

            await asyncio.sleep(3)

        # Summary
        r = await c.get('http://127.0.0.1:8112/portfolio/status')
        pf = r.json()
        print(f'\n{\"=\"*50}')
        print(f'  FULL LOOP COMPLETE')
        print(f'  Portfolio: {pf[\"total_value\"]:.0f} | PnL: {pf[\"pnl_pct\"]}% | MaxDD: {pf[\"max_drawdown\"]}% | Trades: {pf[\"total_trades\"]}')
        print(f'{\"=\"*50}')

asyncio.run(full_loop())
"
echo.
echo   Full loop finished.
pause
