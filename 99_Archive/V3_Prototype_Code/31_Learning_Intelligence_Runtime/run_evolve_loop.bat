@echo off
echo ============================================================
echo   AQF-T V3.4.0 Evolution Loop
echo   Execute -^> Experience -^> Evaluate -^> Learn -^> Evolve
echo ============================================================

cd /d D:\AQF-T\31_Learning_Intelligence_Runtime

echo   Starting learning services...
start "AQFT-Experience" python experience_engine\server.py
start "AQFT-Evaluation" python evaluation_engine\server.py
start "AQFT-RL" python reinforcement_runtime\server.py
timeout /t 2 >nul

echo   Running Evolution Loop...
python -c "
import asyncio, httpx, random
from datetime import datetime

SCENARIOS = [
    {'regime':'Bull Expansion','volatility':0.12,'trend':'UP'},
    {'regime':'Sideways','volatility':0.08,'trend':'NEUTRAL'},
    {'regime':'Bear Decline','volatility':0.28,'trend':'DOWN'},
    {'regime':'Bull Expansion','volatility':0.15,'trend':'UP'},
    {'regime':'High Volatility','volatility':0.45,'trend':'NEUTRAL'},
]

async def evolve():
    async with httpx.AsyncClient(timeout=10.0) as c:
        for i, scenario in enumerate(SCENARIOS):
            print(f'\n=== Evolution Step {i+1}/5: {scenario[\"regime\"]} ===')

            # 1. World Model state
            world = {'regime':scenario['regime'],'volatility':scenario['volatility']}

            # 2. Decision
            action = random.choice(['BUY','SELL','HOLD','INCREASE','REDUCE'])
            confidence = random.uniform(0.5,0.9)
            print(f'  Action: {action} (conf={confidence:.2f})')

            # 3. Risk check
            risk_score = random.randint(10,50)
            risk_dec = 'APPROVE' if risk_score<30 else 'ADJUST' if risk_score<60 else 'REJECT'
            print(f'  Risk: {risk_dec} (score={risk_score})')

            # 4. Simulated outcome
            pnl = random.gauss(0.01,0.03) if risk_dec!='REJECT' else 0
            drawdown = abs(random.gauss(0.02,0.01))
            outcome = {'return':round(pnl,4),'drawdown':round(drawdown,3),'actual_trend':scenario['trend'],'risk_score':risk_score}
            print(f'  Outcome: return={pnl*100:.2f}% dd={drawdown*100:.2f}%')

            # 5. Extract experience
            exp = {'world_state':world,'decision':{'action':action,'confidence':confidence},'risk':{'decision':risk_dec},'outcome':outcome}
            r = await c.post('http://127.0.0.1:8120/experience/extract',json=exp)
            exp_data = r.json()
            print(f'  Experience: {exp_data[\"experience\"][\"id\"]} (importance={exp_data[\"experience\"][\"importance\"]})')

            # 6. Evaluate modules
            r = await c.post('http://127.0.0.1:8121/evaluation/score',json=exp)
            ev = r.json()['evaluation']
            best = max(ev.items(),key=lambda x:x[1]['cumulative'])
            print(f'  Best module: {best[0]} ({best[1][\"cumulative\"]})')

            # 7. Reinforcement learning
            r = await c.post('http://127.0.0.1:8122/reinforcement/learn',json=exp)
            rl = r.json()
            print(f'  RL: reward={rl[\"reward\"]} q_value={rl[\"q_value\"]}')

            await asyncio.sleep(1)

        # Summary
        print(f'\n{\"=\"*50}')
        r = await c.get('http://127.0.0.1:8121/evaluation/report')
        report = r.json()
        print(f'  EVOLUTION COMPLETE')
        print(f'  Best module: {report[\"best\"]}')
        print(f'  Worst module: {report[\"worst\"]}')

        r = await c.get('http://127.0.0.1:8122/reinforcement/policy')
        policy = r.json()
        print(f'  Learned policy rules: {len(policy[\"policy\"])}')
        for state, rule in policy['policy'].items():
            print(f'    {state}: {rule[\"action\"]} (value={rule[\"value\"]})')

        r = await c.get('http://127.0.0.1:8120/experience/patterns')
        patterns = r.json()
        print(f'  Regimes discovered: {patterns[\"regimes\"]}')
        print(f'{\"=\"*50}')

asyncio.run(evolve())
"
echo.
echo   Evolution loop finished.
pause
