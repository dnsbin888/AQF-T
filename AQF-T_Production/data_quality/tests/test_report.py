"""M1 tests — quality_report"""
from data_quality.quality_report import QualityReport


def test_empty_report_generates():
    r = QualityReport()
    report = r.generate()
    assert "AQF-T M1 Data Quality Report" in report
    assert "综合评分" in report


def test_report_includes_errors():
    r = QualityReport()
    r.record_validation_error("测试错误: 价格异常")
    r.record_anomaly("测试异常: 数据中断")
    r.record_recovery("测试恢复: 切换到备用源")
    report = r.generate()
    assert "测试错误" in report
    assert "测试异常" in report
    assert "测试恢复" in report
