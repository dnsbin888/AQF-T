"""
AQF-T Paper Trading Runner  模拟交易日线运行器
================================================
每日运行: 加载市场数据 -> 跑主管线 -> 输出报告

模式:
  --mode single  单日运行 (默认)
  --mode batch   批量回放 (N天连续)
  --mode replay  L2 Replay验证

用法:
  python paper_runner.py                  # 单日模拟
  python paper_runner.py --mode batch     # 批量回放
  python paper_runner.py --date 2026-07-30  # 指定日期
"""

import argparse
import random
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from pipeline import ProductionPipeline, PipelineState

# 真实数据适配器 (Phase 1: AKSHARE EOD)
try:
    from data.market_data_adapter import MarketDataAdapter, create_adapter
    REAL_DATA_AVAILABLE = True
except ImportError:
    REAL_DATA_AVAILABLE = False
    MarketDataAdapter = None
    create_adapter = None


# ===============================================================
# Mock Data Generators (Paper Trading)
# ===============================================================

class MarketDataSimulator:
    """市场数据模拟器  Paper Trading 用"""

    # A股常见标的池
    WATCHLIST_POOL = [
        {"symbol": "000001", "name": "平安银行", "sector": "金融"},
        {"symbol": "000002", "name": "万科A", "sector": "地产"},
        {"symbol": "000858", "name": "五粮液", "sector": "白酒"},
        {"symbol": "002594", "name": "比亚迪", "sector": "新能源"},
        {"symbol": "300750", "name": "宁德时代", "sector": "新能源"},
        {"symbol": "600519", "name": "贵州茅台", "sector": "白酒"},
        {"symbol": "601012", "name": "隆基绿能", "sector": "光伏"},
        {"symbol": "688981", "name": "中芯国际", "sector": "芯片"},
        {"symbol": "300059", "name": "东方财富", "sector": "券商"},
        {"symbol": "002230", "name": "科大讯飞", "sector": "AI"},
    ]

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self._day_counter = 0

    def generate_market_stats(self, phase: str = None) -> dict:
        """
        生成全市场统计数据

        Args:
            phase: 指定情绪阶段 (冰点期/回暖期/高潮期/退潮期), None则随机
        """
        if phase is None:
            phase = random.choice(["冰点期", "回暖期", "高潮期", "退潮期"])

        phase_config = {
            "冰点期": {
                "limit_up_count": random.randint(15, 30),
                "limit_down_count": random.randint(35, 80),
                "max_board_height": random.randint(1, 3),
                "炸板率": random.uniform(0.30, 0.50),
                "promotion_rate": random.uniform(0.05, 0.15),
                "north_bound_net": random.uniform(-30, -5),
                "margin_balance_change": random.uniform(-0.05, -0.01),
            },
            "回暖期": {
                "limit_up_count": random.randint(40, 70),
                "limit_down_count": random.randint(10, 25),
                "max_board_height": random.randint(3, 5),
                "炸板率": random.uniform(0.20, 0.35),
                "promotion_rate": random.uniform(0.20, 0.40),
                "north_bound_net": random.uniform(-5, 15),
                "margin_balance_change": random.uniform(-0.01, 0.02),
            },
            "高潮期": {
                "limit_up_count": random.randint(80, 150),
                "limit_down_count": random.randint(0, 10),
                "max_board_height": random.randint(6, 10),
                "炸板率": random.uniform(0.10, 0.25),
                "promotion_rate": random.uniform(0.30, 0.55),
                "north_bound_net": random.uniform(10, 50),
                "margin_balance_change": random.uniform(0.01, 0.05),
            },
            "退潮期": {
                "limit_up_count": random.randint(20, 40),
                "limit_down_count": random.randint(50, 120),
                "max_board_height": random.randint(1, 2),
                "炸板率": random.uniform(0.40, 0.65),
                "promotion_rate": random.uniform(0.02, 0.10),
                "north_bound_net": random.uniform(-50, -15),
                "margin_balance_change": random.uniform(-0.05, -0.02),
            },
        }

        stats = phase_config[phase].copy()
        stats["board_ladder"] = self._generate_ladder(stats["max_board_height"])
        return stats

    def _generate_ladder(self, max_height: int) -> dict:
        """生成连板梯队"""
        ladder = {}
        for h in range(2, max_height + 1):
            count = max(0, random.randint(2, 8) - h)
            ladder[f"{h}板"] = count
        if max_height >= 5:
            ladder["5+板"] = random.randint(0, 2)
        return ladder

    def generate_watchlist(self, regime_allows_a: bool = True,
                           regime_allows_b: bool = True) -> list[dict]:
        """
        生成监控列表  包含模拟的 features / l2_features / ctx

        Path A (回封板) 需要 ctx 有板/炸板/回封相关字段
        Path B (半路) 需要 features 有趋势/题材/L2字段
        """
        # 根据 Regime 决定哪些标的活跃
        pool = random.sample(self.WATCHLIST_POOL, random.randint(6, 10))
        watchlist = []

        for stock in pool:
            symbol = stock["symbol"]

            # -- 通用 features --
            sector_pct = random.uniform(-3, 5)
            features = {
                "symbol": symbol,
                "ma_5": random.uniform(10, 200),
                "ma_20": random.uniform(10, 200),
                "volume_ratio": random.uniform(0.5, 3.0),
                "theme_heat": random.uniform(0, 1),
                "sector_score": random.uniform(0, 1),
                # P1 SectorFlow fields
                "sector": stock["sector"],
                "sector_limit_up_change": random.uniform(-0.3, 0.5),
                "sector_fund_flow": random.uniform(-10, 20),
                "sector_fund_flow_avg": random.uniform(1, 10),
                "sector_pct": sector_pct,
                "sector_volume_change": random.uniform(-0.5, 1.0),
                "is_leader": random.random() > 0.8,
                # P1 RelativeStrength fields
                "stock_5d_return": random.uniform(-0.08, 0.15),
                "market_5d_return": random.uniform(-0.03, 0.05),
                "sector_5d_return": sector_pct / 100,
                "leader_5d_return": random.uniform(-0.05, 0.18),
            }

            # -- L2 features --
            l2_features = {
                "symbol": symbol,
                "net_big_flow": random.uniform(-500, 2000),
                "seal_ratio": random.uniform(0, 15),
                "ddy": random.uniform(-2, 3),
            }

            # -- Perception ctx (Path A 用) --
            is_healthy_break = random.random() > 0.4  # 60% 洗盘型
            ctx = {
                "symbol": symbol,

                # 炸板分类相关
                "break_drop_pct": random.uniform(0.01, 0.04) if is_healthy_break else random.uniform(0.05, 0.12),
                "white_above_yellow": is_healthy_break,
                "buy_absorption": is_healthy_break,
                "big_order_on_break": random.random() > 0.5,
                "board_count": random.randint(1, 6),

                # 板块地位相关
                "sector_limit_up_count": random.randint(1, 12),
                "follower_count": random.randint(0, 5),
                "theme_days": random.randint(1, 8),
                "theme_name": stock["sector"],

                # 回封确认相关
                "reseal_1min_vol": random.randint(100, 500),
                "first_seal_1min_vol": random.randint(300, 800),
                "break_to_reseal_min": random.randint(2, 20),
                "linkage_count": random.randint(0, 3),

                # 龙头判定相关
                "seal_ratio": random.uniform(0.01, 0.10),
                "longhu_seats": random.randint(0, 5),
                "auction_amount": random.uniform(1000, 10000),
                "float_market_cap": random.uniform(10, 80),
                "gap_up_pct": random.uniform(-0.03, 0.07),

                # P1 SectorFlow ctx
                "sector": stock["sector"],
                "sector_limit_up_change": random.uniform(-0.3, 0.5),
                "sector_fund_flow": random.uniform(-10, 20),
                "sector_fund_flow_avg": random.uniform(1, 10),
                "sector_pct": sector_pct,
                "sector_volume_change": random.uniform(-0.5, 1.0),
                "is_leader": random.random() > 0.8,
                # P1 RelativeStrength ctx
                "stock_5d_return": features["stock_5d_return"],
                "market_5d_return": features["market_5d_return"],
                "sector_5d_return": features["sector_5d_return"],
                "leader_5d_return": features["leader_5d_return"],
            }

            watchlist.append({
                "symbol": symbol,
                "name": stock["name"],
                "sector": stock["sector"],
                "features": features,
                "l2_features": l2_features,
                "ctx": ctx,
            })

        return watchlist


# ===============================================================
# Runners
# ===============================================================

def run_single_day(pipeline: ProductionPipeline,
                   phase: str = None,
                   date: str = None,
                   use_real_data: bool = False) -> PipelineState:
    """
    单日运行  Paper Trading

    Args:
        pipeline: 已初始化的管道
        phase: 市场阶段 (None=随机, 仅 use_real_data=False 时生效)
        date: 日期 (None=今天)
        use_real_data: True=真实数据(AKSHARE EOD), False=模拟器
    """
    from core.clock import clock
    from datetime import datetime as dt
    from strategy.market_regime import MarketRegimeEngine

    clock.override(dt(2026, 7, 1, 10, 0, 0))
    regime_engine = MarketRegimeEngine()

    data_source = "SIMULATOR"
    market_stats = None
    watchlist = []
    event_texts = {}

    # ═══════════════════════════════════════════════════════════
    # Phase 1: 真实数据路径 (AKSHARE EOD)
    # ═══════════════════════════════════════════════════════════
    if use_real_data and REAL_DATA_AVAILABLE:
        print("[CC] 尝试接入真实数据 (AKSHARE EOD)...")
        try:
            adapter = MarketDataAdapter()
            adapter_status = adapter.status()
            print(f"[CC] 数据源: {adapter_status['primary_source']}")

            # ① 全市场统计
            market_stats = adapter.fetch_market_stats(date)
            _meta = market_stats.get("_meta", {})
            if _meta.get("source") == "akshare":
                data_source = "AKSHARE_EOD"
                print(f"[CC] 真实数据获取成功 "
                      f"(涨停{market_stats['limit_up_count']}, "
                      f"跌停{market_stats['limit_down_count']}, "
                      f"最高{market_stats['max_board_height']}板)")
            else:
                data_source = "FALLBACK_FAILSAFE"  # B-4: 诚实标记, 非 SIMULATOR
                print("[CC] WARNING: 使用 fail-safe fallback (无真实数据) → 市场判定=退潮/stop")

            # ② Regime 判断
            regime = regime_engine.evaluate(market_stats)
            print(f"[CC] Regime: {regime.sentiment_phase} "
                  f"(mode={regime.operation_mode}, "
                  f"path_a={regime.path_a_allowed}, "
                  f"path_b={regime.path_b_allowed})")

            # ③ 监控列表 (从涨停池取活跃股票)
            symbols = adapter.fetch_active_symbols(limit=20)
            if symbols:
                watchlist = adapter.fetch_watchlist(symbols)
                print(f"[CC] Watchlist: {len(watchlist)}/{len(symbols)} 只获取成功")
            else:
                print("[CC] WARNING: 无法获取活跃股票列表，watchlist 为空")

            # ④ 事件文本 (Phase 1 暂用空，后续可接 LLM 情绪层)
            event_texts = {}

        except Exception as e:
            print(f"[CC] ERROR 真实数据获取失败: {e}")
            print("[CC] 回退到模拟器...")
            use_real_data = False  # 触发下方 fallback

    # ═══════════════════════════════════════════════════════════
    # Fallback: 模拟器路径 (保持兼容)
    # ═══════════════════════════════════════════════════════════
    if not use_real_data or market_stats is None:
        if use_real_data:
            print("[CC] FALLBACK: 真实数据不可用，使用模拟器")
        data_source = "SIMULATOR"
        sim = MarketDataSimulator()

        # 生成市场数据
        market_stats = sim.generate_market_stats(phase)

        # 先生成 MarketRegime 看允许哪些路径
        regime = regime_engine.evaluate(market_stats)

        # 生成监控列表
        watchlist = sim.generate_watchlist(
            regime_allows_a=regime.path_a_allowed,
            regime_allows_b=regime.path_b_allowed,
        )

        # 生成事件文本 (随机)
        event_sources = [
            "公司公告: 2026年半年度业绩预告增长30%",
            "行业新闻: 政策利好出台, 板块集体走强",
            "龙虎榜: 游资净买入5000万",
            "北向资金加仓, 连续3日净流入",
            "大股东减持计划, 6个月内减持不超过2%",
            "机构调研密集, 近一月20家机构调研",
        ]
        event_texts = {}
        for w in watchlist[:3]:
            if random.random() < 0.3:
                event_texts[w["symbol"]] = random.sample(
                    event_sources, random.randint(1, 2)
                )

    # ═══════════════════════════════════════════════════════════
    # 运行主管线 (不改变 — 接线不改脑)
    # ═══════════════════════════════════════════════════════════
    if date:
        pipeline._last_regime = None

    # 注入数据源标识到 market_stats
    market_stats["_data_source"] = data_source

    state = pipeline.run_daily(
        market_stats=market_stats,
        watchlist=watchlist,
        event_texts=event_texts,
    )

    if date:
        state.date = date

    return state


def run_batch(pipeline: ProductionPipeline, days: int = 22):
    """
    批量回放 — 连续N天模拟

    模拟完整的月度交易周期: 回暖 → 高潮 → 退潮 → 冰点 → 回暖
    """
    # Paper模式: 时钟固定到交易时段
    from core.clock import clock
    from datetime import datetime as dt
    clock.override(dt(2026, 7, 1, 10, 0, 0))
    # 一个月的典型情绪周期
    cycle = (
        ["回暖期"] * 3 +
        ["高潮期"] * 5 +
        ["高潮期"] * 3 +
        ["退潮期"] * 4 +
        ["冰点期"] * 3 +
        ["回暖期"] * 4
    )

    # 扩展或截断到目标天数
    if days <= len(cycle):
        phases = cycle[:days]
    else:
        phases = cycle * (days // len(cycle) + 1)
        phases = phases[:days]

    results = []
    start_date = datetime(2026, 7, 1)

    print(f"\n{'='*60}")
    print(f"  AQF-T Batch Paper Trading  {days}天")
    print(f"  Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"{'='*60}\n")

    for i, phase in enumerate(phases):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        state = run_single_day(pipeline, phase=phase, date=date)
        results.append(state)

        # 日终刷新 (T+1解锁)
        pipeline.broker.daily_refresh()

        # 打印摘要
        summary = pipeline.daily_summary(state)
        print(summary)
        print()

    # -- 批量统计 --
    print(f"\n{'='*60}")
    print(f"  BATCH SUMMARY  {days}天")
    print(f"{'='*60}")

    trading_days = [r for r in results if r.tradable]
    stopped_days = [r for r in results if not r.tradable]

    total_candidates = sum(r.total_candidates for r in results)
    total_signals = sum(r.total_signals for r in results)
    total_fills = sum(r.total_fills for r in results)
    total_rejected = sum(r.total_rejected for r in results)
    total_errors = sum(len(r.errors) for r in results)

    print(f"  交易天数:     {len(trading_days)}/{days}")
    print(f"  停止天数:     {len(stopped_days)}")
    print(f"  总候选:       {total_candidates}")
    print(f"  总信号:       {total_signals}")
    print(f"  总成交:       {total_fills}")
    print(f"  总拒绝:       {total_rejected}")
    print(f"  总异常:       {total_errors}")
    print(f"  最终账户:     {pipeline.broker.summary()}")

    # Phase分布
    phase_counts = {}
    for r in results:
        if r.regime:
            p = r.regime.sentiment_phase
            phase_counts[p] = phase_counts.get(p, 0) + 1
    print(f"  阶段分布:     {phase_counts}")

    return results


def run_replay(pipeline: ProductionPipeline, replay_file: str):
    """
    L2 Replay 验证  从历史数据文件回放

    replay_file: JSON文件, 每行一条历史数据记录
    """
    replay_path = Path(replay_file)
    if not replay_path.exists():
        print(f"[ERROR] Replay file not found: {replay_file}")
        return

    data = json.loads(replay_path.read_text(encoding="utf-8"))
    days = data if isinstance(data, list) else [data]

    print(f"\n  L2 Replay: {len(days)} days from {replay_file}")

    for day_data in days:
        market_stats = day_data.get("market_stats", {})
        watchlist = day_data.get("watchlist", [])
        event_texts = day_data.get("event_texts", {})

        state = pipeline.run_daily(
            market_stats=market_stats,
            watchlist=watchlist,
            event_texts=event_texts,
        )

        summary = pipeline.daily_summary(state)
        print(summary)

        # 验证: 同数据同结果 (Determinism)
        state2 = pipeline.run_daily(
            market_stats=market_stats,
            watchlist=watchlist,
            event_texts=event_texts,
        )
        assert state.total_signals == state2.total_signals, \
            f"Determinism FAILED: {state.total_signals} vs {state2.total_signals}"
        print("  [OK] Determinism: PASSED")


# ===============================================================
# Main CLI
# ===============================================================

def main():
    parser = argparse.ArgumentParser(
        description="AQF-T Paper Trading Runner  模拟交易日线运行器"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["single", "batch", "replay"],
        default="single",
        help="运行模式: single(单日) | batch(批量) | replay(回放)"
    )
    parser.add_argument(
        "--days", "-d",
        type=int, default=22,
        help="批量模式下的天数 (默认22)"
    )
    parser.add_argument(
        "--phase", "-p",
        choices=["冰点期", "回暖期", "高潮期", "退潮期"],
        default=None,
        help="指定市场阶段 (默认随机)"
    )
    parser.add_argument(
        "--date",
        default=None,
        help="指定日期 YYYY-MM-DD"
    )
    parser.add_argument(
        "--replay-file", "-f",
        default=None,
        help="Replay JSON文件路径"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int, default=42,
        help="随机种子 (默认42, 确保可复现)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式"
    )

    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 创建 Pipeline
    pipeline = ProductionPipeline()

    print(f"\n{'='*60}")
    print(f"  AQF-T Production V{pipeline.config.get('system', {}).get('version', '1.0')}")
    print(f"  Mode: {pipeline.mode}")
    print(f"  Runner: {args.mode}")
    print(f"  Seed: {args.seed}")
    print(f"  {datetime.now().isoformat()}")
    print(f"{'='*60}")

    if args.mode == "single":
        state = run_single_day(
            pipeline,
            phase=args.phase,
            date=args.date,
        )
        print(pipeline.daily_summary(state))

    elif args.mode == "batch":
        run_batch(pipeline, days=args.days)

    elif args.mode == "replay":
        if not args.replay_file:
            print("[ERROR] --replay-file required for replay mode")
            sys.exit(1)
        run_replay(pipeline, args.replay_file)

    # 最终状态
    if not args.quiet:
        print(f"\n  System Health: {pipeline.monitor.check().to_dict()}")
        print(f"  Model Registry: {len(pipeline.model_registry.list_all())} models")
        print(f"  Event Bus History: {len(bus.recent())} events")


if __name__ == "__main__":
    main()
