"""
AQF-T Intelligence Pipeline — 智能编排引擎

从"各服务独立返回"升级为"服务链式协同"

Pipeline:
  Market Data → World Model → Agent Council → Decision → Risk → Execution → Memory
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from datetime import datetime
from dataclasses import dataclass, field
from event_bus.event_bus import bus, EventType


@dataclass
class IntelligenceContext:
    """贯穿整个 Pipeline 的上下文"""
    symbol: str = "000300"
    market_data: dict = field(default_factory=dict)
    world_state: dict = field(default_factory=dict)
    agent_consensus: dict = field(default_factory=dict)
    decision: dict = field(default_factory=dict)
    risk_decision: dict = field(default_factory=dict)
    execution_result: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)


class IntelligencePipeline:
    """AQF-T 智能编排 — 按顺序调用所有分布式服务"""

    def __init__(self):
        self.services = {
            "world_model": "http://127.0.0.1:8102",
            "agent_council": "http://127.0.0.1:8101",
            "decision_engine": "http://127.0.0.1:8103",
            "risk_engine": "http://127.0.0.1:8104",
            "memory": "http://127.0.0.1:8105",
        }

    async def run(self, symbol: str = "000300") -> IntelligenceContext:
        """执行完整的 Intelligence Pipeline"""
        ctx = IntelligenceContext(symbol=symbol)
        print(f"\n{'='*60}")
        print(f"  AQF-T Intelligence Pipeline — {symbol}")
        print(f"  {datetime.now().isoformat()}")
        print(f"{'='*60}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Step 1: World Model — 理解世界
            ctx = await self._step_world_model(client, ctx)
            # Step 2: Agent Council — 多智能体协调
            ctx = await self._step_agent_council(client, ctx)
            # Step 3: Decision Engine — 生成决策
            ctx = await self._step_decision(client, ctx)
            # Step 4: Risk Engine — 风险审批
            ctx = await self._step_risk(client, ctx)
            # Step 5: Memory — 经验存储
            ctx = await self._step_memory(client, ctx)

        self._print_summary(ctx)
        return ctx

    async def _step_world_model(self, client, ctx):
        try:
            r = await client.get(f"{self.services['world_model']}/world/state")
            ctx.world_state = r.json()
            bus.publish(EventType.WORLD_STATE, ctx.world_state, "pipeline")
            print(f"  [World Model]  regime={ctx.world_state.get('regime','?')}")
        except Exception as e:
            ctx.errors.append(f"WorldModel: {e}")
        return ctx

    async def _step_agent_council(self, client, ctx):
        try:
            r = await client.post(f"{self.services['agent_council']}/agents/coordinate",
                                  json={"world_state": ctx.world_state})
            ctx.agent_consensus = r.json()
            bus.publish(EventType.AGENT_CONSENSUS, ctx.agent_consensus, "pipeline")
            print(f"  [Agent Council] decision={ctx.agent_consensus.get('supervisor_decision','?')}")
        except Exception as e:
            ctx.errors.append(f"AgentCouncil: {e}")
        return ctx

    async def _step_decision(self, client, ctx):
        try:
            r = await client.post(f"{self.services['decision_engine']}/decision/evaluate",
                                  json={"world_state": ctx.world_state,
                                        "agent_consensus": ctx.agent_consensus})
            ctx.decision = r.json()
            bus.publish(EventType.DECISION, ctx.decision, "pipeline")
            print(f"  [Decision]     action={ctx.decision.get('action','?')} conf={ctx.decision.get('confidence','?')}")
        except Exception as e:
            ctx.errors.append(f"Decision: {e}")
        return ctx

    async def _step_risk(self, client, ctx):
        try:
            r = await client.post(f"{self.services['risk_engine']}/risk/check",
                                  json={"decision": ctx.decision})
            ctx.risk_decision = r.json()
            bus.publish(EventType.RISK_DECISION, ctx.risk_decision, "pipeline")
            decision = ctx.risk_decision.get('decision', '?')
            marker = "✅" if decision == "APPROVE" else "⚠️" if decision == "ADJUST" else "❌"
            print(f"  [Risk Engine]  {marker} {decision} (score={ctx.risk_decision.get('risk_score','?')})")
        except Exception as e:
            ctx.errors.append(f"Risk: {e}")
        return ctx

    async def _step_memory(self, client, ctx):
        try:
            experience = {
                "id": f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "world": ctx.world_state.get("regime", ""),
                "action": ctx.decision.get("action", ""),
                "risk_decision": ctx.risk_decision.get("decision", ""),
                "timestamp": datetime.now().isoformat(),
            }
            await client.post(f"{self.services['memory']}/memory/store", json=experience)
            bus.publish(EventType.MEMORY, experience, "pipeline")
            print(f"  [Memory]       experience stored: {experience['id']}")
        except Exception as e:
            ctx.errors.append(f"Memory: {e}")
        return ctx

    def _print_summary(self, ctx):
        print(f"{'─'*60}")
        print(f"  PIPELINE COMPLETE")
        print(f"  World:  {ctx.world_state.get('regime', 'N/A')}")
        print(f"  Agent:  {ctx.agent_consensus.get('supervisor_decision', 'N/A')}")
        print(f"  Decide: {ctx.decision.get('action', 'N/A')} ({ctx.decision.get('confidence', 0)})")
        print(f"  Risk:   {ctx.risk_decision.get('decision', 'N/A')}")
        if ctx.errors:
            print(f"  Errors: {ctx.errors}")
        print(f"{'='*60}\n")


# ── CLI 入口 ──
async def main():
    pipeline = IntelligencePipeline()
    result = await pipeline.run(symbol="000300")
    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
