"""
AQF-T Production  主程序入口
==============================
启动: python main.py [--mode paper|live] [--cmd run|status|test|backtest]

命令:
  run      运行主管线 (默认)
  status   查看系统状态
  test     运行测试套件
  backtest 运行回测

用法:
  python main.py                          # Paper Trading 单日运行
  python main.py --mode live              # 实盘模式 (需QMT连接)
  python main.py --cmd status             # 系统状态
  python main.py --cmd test               # 运行测试
  python main.py --cmd batch --days 22    # 批量22天回放
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 确保项目根目录在 path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import ProductionPipeline, create_pipeline
from paper_runner import run_single_day, run_batch, MarketDataSimulator


def cmd_run(args):
    """运行主管线"""
    pipeline = create_pipeline(args.mode)

    print(f"""
{'='*60}
  AQF-T Production V{pipeline.config.get('system', {}).get('version', '1.0')}
  Mode: {pipeline.mode}
  QMT L2: {'ON' if pipeline.config.get('data', {}).get('l2_enabled') else 'OFF'}
  Kill Switch: {'ACTIVE' if pipeline.config.get('risk', {}).get('kill_switch') else 'OFF'}
  {datetime.now().isoformat()}
{'='*60}
""")

    if args.cmd == "batch":
        run_batch(pipeline, days=args.days)
    else:
        state = run_single_day(
            pipeline,
            phase=args.phase,
            date=args.date,
            use_real_data=(args.source == "real"),
        )
        print(pipeline.daily_summary(state))


def cmd_status(args):
    """查看系统状态"""
    pipeline = ProductionPipeline()
    status = pipeline.status()

    print(f"""
{'='*60}
  AQF-T Production  System Status
{'='*60}
  Mode:        {status['mode']}
  Last Regime: {status['last_regime'] or 'N/A'}
  Positions:   {status['positions']}
  Trades:      {status['trades_today']}

  Account:
    Cash:       {status['account']['cash']:,.2f}
    Positions:  {status['account']['positions']}
    TotalValue: {status['account']['total_value']:,.2f}
    TotalTrades:{status['account']['total_trades']}

  Health:
    QMT:        {status['health']['qmt']}
    L2 Age:     {status['health']['l2_age']}
    DB:         {status['health']['db']}
    CPU:        {status['health']['cpu']}
    Memory:     {status['health']['memory']}
    Overall:    {status['health']['overall']}
{'='*60}
""")


def cmd_test(args):
    """运行测试套件"""
    print("\n  Running AQF-T Test Suite...\n")

    # 运行 M1 测试
    try:
        from run_tests import results as m1_results
        exec(open("run_tests.py", encoding="utf-8").read())
    except Exception as e:
        print(f"  M1 Tests: ERROR  {e}")

    # 端到端 Pipeline 测试
    print("\n  -- Pipeline E2E Test --")
    try:
        from tests.test_pipeline import run_all_tests
        passed, failed = run_all_tests()
        if failed > 0:
            print(f"  Pipeline E2E: {failed} FAILED")
        else:
            print("  Pipeline E2E: ALL PASSED")
    except Exception as e:
        print(f"  Pipeline E2E ERROR: {e}")

    print("\n  Done.")


def cmd_backtest(args):
    """运行回测"""
    from learning.backtest_engine import BacktestEngine, BacktestConfig

    config = BacktestConfig(
        start_date=args.start or "2023-01-01",
        end_date=args.end or "2026-06-30",
        initial_cash=args.cash or 1_000_000.0,
    )

    print(f"""
{'='*60}
  AQF-T Backtest
  Period: {config.start_date} -> {config.end_date}
  Cash: {config.initial_cash:,.0f}
{'='*60}
""")

    # TODO: 加载真实数据 + 生成信号
    # engine = BacktestEngine(config)
    # result = engine.run(data, signals)
    print("  Backtest engine ready. 需要提供 data + signals 输入。")


def main():
    parser = argparse.ArgumentParser(
        description="AQF-T Production  智能交易系统"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["paper", "live"],
        default="paper",
        help="运行模式: paper(模拟) | live(实盘)"
    )
    parser.add_argument(
        "--cmd",
        choices=["run", "status", "test", "batch", "backtest"],
        default="run",
        help="命令: run|status|test|batch|backtest"
    )
    parser.add_argument("--days", "-d", type=int, default=22)
    parser.add_argument("--phase", "-p", choices=["冰点期", "回暖期", "高潮期", "退潮期"])
    parser.add_argument("--date")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--cash", type=float)
    parser.add_argument("--seed", "-s", type=int, default=42)
    parser.add_argument(
        "--source",
        choices=["sim", "real"],
        default="sim",
        help="数据源: sim(模拟器) | real(AKSHARE EOD)"
    )

    args = parser.parse_args()

    # 路由
    if args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "test":
        cmd_test(args)
    elif args.cmd == "backtest":
        cmd_backtest(args)
    elif args.cmd in ("run", "batch"):
        cmd_run(args)
    else:
        cmd_run(args)


if __name__ == "__main__":
    main()
