"""极简验证 — 不依赖任何第三方包"""
f = open("check_result.txt", "w", encoding="utf-8")
try:
    from data_quality.data_model import TickRecord, BarRecord
    f.write("✅ data_model OK\n")
except Exception as e:
    f.write(f"❌ data_model FAIL: {e}\n")

try:
    from data_quality.validator import bar_validator
    from datetime import datetime
    b = BarRecord("SH", datetime.now(), 100, 110, 90, 105, 1000, 10000)
    r = bar_validator.validate(b)
    ok = sum(1 for x in r if x.passed)
    f.write(f"✅ validator OK ({ok}/{len(r)} passed)\n")
except Exception as e:
    f.write(f"❌ validator FAIL: {e}\n")

try:
    from data_quality.recovery_manager import RecoveryManager
    rm = RecoveryManager()
    assert rm.decide("critical").value == "fail"
    f.write("✅ recovery_manager OK\n")
except Exception as e:
    f.write(f"❌ recovery_manager FAIL: {e}\n")

try:
    from data_quality.health_monitor import HealthMonitor
    hm = HealthMonitor()
    s = hm.snapshot()
    f.write(f"✅ health_monitor OK (score={s.score})\n")
except Exception as e:
    f.write(f"❌ health_monitor FAIL: {e}\n")

try:
    from data_quality.quality_report import QualityReport
    qr = QualityReport()
    report = qr.generate()
    f.write(f"✅ quality_report OK ({len(report)} chars)\n")
except Exception as e:
    f.write(f"❌ quality_report FAIL: {e}\n")

f.write("\n=== M1 Core Framework: ALL CHECKED ===")
f.close()
