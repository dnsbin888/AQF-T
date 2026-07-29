"""M1 测试运行器 — 结果写入文件"""
import sys
sys.path.insert(0, ".")

results = []

# ── data_model ──
try:
    from data_quality.tests.test_data_model import (
        test_tick_creation, test_bar_creation, test_bar_immutable, test_orderbook_creation
    )
    test_tick_creation(); results.append("✅ test_tick_creation")
    test_bar_creation(); results.append("✅ test_bar_creation")
    test_bar_immutable(); results.append("✅ test_bar_immutable")
    test_orderbook_creation(); results.append("✅ test_orderbook_creation")
except Exception as e:
    results.append(f"❌ data_model: {e}")

# ── validator ──
try:
    from data_quality.tests.test_validator import (
        test_normal_bar_passes, test_negative_price_fails, test_ohlc_violation_fails,
        test_negative_volume_fails, test_custom_rule_registration, test_critical_severity_in_result
    )
    test_normal_bar_passes(); results.append("✅ test_normal_bar_passes")
    test_negative_price_fails(); results.append("✅ test_negative_price_fails")
    test_ohlc_violation_fails(); results.append("✅ test_ohlc_violation_fails")
    test_negative_volume_fails(); results.append("✅ test_negative_volume_fails")
    test_custom_rule_registration(); results.append("✅ test_custom_rule_registration")
    test_critical_severity_in_result(); results.append("✅ test_critical_severity")
except Exception as e:
    results.append(f"❌ validator: {e}")

# ── anomaly ──
try:
    from data_quality.tests.test_anomaly import (
        test_normal_no_anomaly, test_duplicate_timestamp, test_price_jump_detection,
        test_gap_detection, test_l2_freeze_detection
    )
    test_normal_no_anomaly(); results.append("✅ test_normal_no_anomaly")
    test_duplicate_timestamp(); results.append("✅ test_duplicate_timestamp")
    test_price_jump_detection(); results.append("✅ test_price_jump")
    test_gap_detection(); results.append("✅ test_gap_detection")
    test_l2_freeze_detection(); results.append("✅ test_l2_freeze")
except Exception as e:
    results.append(f"❌ anomaly: {e}")

# ── recovery ──
try:
    from data_quality.tests.test_recovery import (
        test_info_passes, test_warning_retries_then_fails, test_critical_fails_directly, test_reset_retries
    )
    test_info_passes(); results.append("✅ test_info_passes")
    test_warning_retries_then_fails(); results.append("✅ test_warning_retries")
    test_critical_fails_directly(); results.append("✅ test_critical_fails")
    test_reset_retries(); results.append("✅ test_reset_retries")
except Exception as e:
    results.append(f"❌ recovery: {e}")

# ── health ──
try:
    from data_quality.tests.test_health import (
        test_initial_score_full, test_failed_validations_lower_score,
        test_missing_data_lowers_completeness, test_is_healthy
    )
    test_initial_score_full(); results.append("✅ test_initial_score")
    test_failed_validations_lower_score(); results.append("✅ test_failed_validations")
    test_missing_data_lowers_completeness(); results.append("✅ test_missing_data")
    test_is_healthy(); results.append("✅ test_is_healthy")
except Exception as e:
    results.append(f"❌ health: {e}")

# ── report ──
try:
    from data_quality.tests.test_report import test_empty_report_generates, test_report_includes_errors
    test_empty_report_generates(); results.append("✅ test_empty_report")
    test_report_includes_errors(); results.append("✅ test_report_errors")
except Exception as e:
    results.append(f"❌ report: {e}")

# ── 输出 ──
passed = sum(1 for r in results if "✅" in r)
failed = sum(1 for r in results if "❌" in r)
total = len(results)

output = f"""
================================================================
  AQF-T M1 Test Results
  通过: {passed}/{total} | 失败: {failed}
================================================================
""" + "\n".join(results) + f"""
================================================================
  {'✅ ALL PASSED' if failed == 0 else '❌ SOME FAILED'}
================================================================
"""

with open("test_results.txt", "w", encoding="utf-8") as f:
    f.write(output)

print(output)
