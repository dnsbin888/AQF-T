@echo off
echo ============================================================
echo   AQF-T V3.4.5 Full Evolution Loop
echo   Experience -^> Pattern -^> Knowledge -^> Evolve -^> Experiment
echo ============================================================

cd /d D:\AQF-T\31_Learning_Intelligence_Runtime

echo   Starting all learning services (8120-8127)...
start "AQFT-Experience" python experience_engine\server.py
start "AQFT-Evaluation" python evaluation_engine\server.py
start "AQFT-RL" python reinforcement_runtime\server.py
start "AQFT-StrategyMem" python strategy_memory\server.py
start "AQFT-PatternMine" python pattern_mining\server.py
start "AQFT-Knowledge" python knowledge_graph\server.py
start "AQFT-Evolution" python model_evolution\server.py
start "AQFT-Experiment" python experiment_engine\server.py
timeout /t 3 >nul

echo   Running Full Evolution Loop...
python -c "
import asyncio, httpx, random

SCENARIOS = [
    {'regime':'Bull Expansion','volatility':0.12},
    {'regime':'Sideways','volatility':0.08},
    {'regime':'Bear Decline','volatility':0.28},
    {'regime':'Bull Expansion','volatility':0.15},
    {'regime':'High Volatility','volatility':0.45},
]

async def full_evolve():
    async with httpx.AsyncClient(timeout=10.0) as c:
        experiences = []
        for i, sc in enumerate(SCENARIOS):
            print(f'\n--- Step {i+1}/5: {sc[\"regime\"]} ---')

            world = {'regime':sc['regime'],'volatility':sc['volatility']}
            action = random.choice(['BUY','SELL','HOLD','INCREASE','REDUCE'])
            risk = 'APPROVE' if random.random()<0.7 else 'ADJUST'
            outcome = {'return':round(random.gauss(0.01,0.03),4),'drawdown':round(random.uniform(0.01,0.08),3)}

            exp = {'world_state':world,'decision':{'action':action,'confidence':random.uniform(0.5,0.9)},'risk':{'decision':risk},'outcome':outcome}

            # 1. Experience
            r = await c.post('http://127.0.0.1:8120/experience/extract',json=exp)
            print(f'  Experience: {r.json()[\"experience\"][\"id\"]}')

            # 2. Evaluate
            r = await c.post('http://127.0.0.1:8121/evaluation/score',json=exp)

            # 3. RL Learn
            await c.post('http://127.0.0.1:8122/reinforcement/learn',json=exp)

            # 4. Strategy Memory (persistent!)
            await c.post('http://127.0.0.1:8123/strategy_memory/store',json=exp)

            experiences.append(exp)
            await asyncio.sleep(0.5)

        # 5. Pattern Mining
        r = await c.post('http://127.0.0.1:8124/pattern_mining/discover',json=experiences)
        rules = r.json()['rules']
        print(f'\n  Discovered {len(rules)} patterns:')
        for rule in rules[:5]:
            print(f'    {rule[\"condition\"]}')

        # 6. Knowledge Graph
        r = await c.get('http://127.0.0.1:8125/knowledge_graph/traverse?from_node=rate_cut')
        print(f'\n  Causal chain: {r.json()[\"causal_chain\"]}')

        # 7. Model Evolution
        r = await c.post('http://127.0.0.1:8126/model_evolution/evolve',json={})
        print(f'  Evolution: gen={r.json()[\"generation\"]}')

        # 8. Experiment
        r = await c.post('http://127.0.0.1:8127/experiment/run',json={'description':'Test Bull strategy','regime':'Bull Expansion'})
        print(f'  Experiment: {r.json()[\"experiment\"][\"verdict\"]}')

        # Summary
        print(f'\n{\"=\"*50}')
        r = await c.get('http://127.0.0.1:8123/strategy_memory/query?regime=Bull')
        print(f'  Memory: {r.json()[\"summary\"]}')
        r = await c.get('http://127.0.0.1:8126/model_evolution/portfolio')
        pf = r.json()
        print(f'  Best strategy: {pf[\"best\"]} (gen {pf[\"generation\"]})')
        r = await c.get('http://127.0.0.1:8122/reinforcement/policy')
        print(f'  RL policy: {len(r.json()[\"policy\"])} rules learned')
        print(f'{\"=\"*50}')
        print(f'\n  V3.4.5 EVOLUTION COMPLETE')
        print(f'  AQF-T now: Remembers + Discovers + Evolves + Experiments')

asyncio.run(full_evolve())
"
pause
