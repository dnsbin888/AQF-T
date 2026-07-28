"""
AQF-T Production — 主程序入口

启动: python main.py
模式: paper (模拟) / live (实盘)
"""
import yaml
from pathlib import Path
from datetime import datetime


def load_config():
    with open("config/system.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    print("=" * 60)
    print(f"  AQF-T Production V{config['system']['version']}")
    print(f"  Mode: {config['system']['mode']}")
    print(f"  QMT L2: {'ON' if config['data']['l2_enabled'] else 'OFF'}")
    print(f"  Kill Switch: {'ACTIVE' if config['risk']['kill_switch'] else 'OFF'}")
    print(f"  {datetime.now().isoformat()}")
    print("=" * 60)

    # To be implemented per phase:
    # Phase 1: Data — QMT L2 → SQLite
    # Phase 2: Strategy — Dragon + Sentiment
    # Phase 3: Risk + Execution
    # Phase 4: Review
    # Phase 5: Learning
    # Phase 6: Live Trading

    print("\n  Ready. Implement phases per README.")
    print("  Phase 1: python data/sources/qmt_l2_loader.py")


if __name__ == "__main__":
    main()
