"""
M1 Data Quality — 质量报告生成器
每日自动生成四类证据: Health/Validation/Anomaly/Recovery
"""
from datetime import datetime
from data_quality.health_monitor import DataHealthSnapshot


class QualityReport:
    """M1 Exit 证据生成器"""

    def __init__(self):
        self.health_history: list[DataHealthSnapshot] = []
        self.validation_errors: list[str] = []
        self.anomaly_events: list[str] = []
        self.recovery_events: list[str] = []

    def record_health(self, snapshot: DataHealthSnapshot):
        self.health_history.append(snapshot)

    def record_validation_error(self, detail: str):
        self.validation_errors.append(f"[{datetime.now().isoformat()}] {detail}")

    def record_anomaly(self, detail: str):
        self.anomaly_events.append(f"[{datetime.now().isoformat()}] {detail}")

    def record_recovery(self, detail: str):
        self.recovery_events.append(f"[{datetime.now().isoformat()}] {detail}")

    def generate(self) -> str:
        """生成日报"""
        latest = self.health_history[-1] if self.health_history else None
        score = latest.score if latest else "N/A"

        return f"""
================================================================
  AQF-T M1 Data Quality Report
  日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================

一、综合评分: {score}/100 {'✅' if latest and latest.is_healthy() else '❌'}

二、分类指标:
  完整率: {latest.completeness if latest else 'N/A'}
  新鲜度: {latest.freshness if latest else 'N/A'}
  校验通过率: {latest.validation_pass_rate if latest else 'N/A'}

三、校验错误 ({len(self.validation_errors)}):
{chr(10).join(self.validation_errors[-5:]) or '  无'}

四、异常事件 ({len(self.anomaly_events)}):
{chr(10).join(self.anomaly_events[-5:]) or '  无'}

五、恢复记录 ({len(self.recovery_events)}):
{chr(10).join(self.recovery_events[-5:]) or '  无'}

================================================================
"""
