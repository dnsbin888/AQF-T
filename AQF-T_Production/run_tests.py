"""M1 测试运行器  结果写入文件"""
import sys
sys.path.insert(0, ".")

results = []

#  data_model 
try:
    from data_quality.tests.test_data_model import (
        test_tick_creation, test_bar_creation, test_bar_immutable, test_orderbook_creation
    )
    test_tick_creation(); results.append("[PASS] test_tick_creation")
    test_bar_creation(); results.append("[PASS] test_bar_creation")
    test_bar_immutable(); results.append("[PASS] test_bar_immutable")
    test_orderbook_creation(); results.append("[PASS] test_orderbook_creation")
except Exception as e:
    results.append(f"[FAIL] data_model: {e}")

#  validator 
try:
    from data_quality.tests.test_validator import (
        test_normal_bar_passes, test_negative_price_fails, test_ohlc_violation_fails,
        test_negative_volume_fails, test_custom_rule_registration, test_critical_severity_in_result
    )
    test_normal_bar_passes(); results.append("[PASS] test_normal_bar_passes")
    test_negative_price_fails(); results.append("[PASS] test_negative_price_fails")
    test_ohlc_violation_fails(); results.append("[PASS] test_ohlc_violation_fails")
    test_negative_volume_fails(); results.append("[PASS] test_negative_volume_fails")
    test_custom_rule_registration(); results.append("[PASS] test_custom_rule_registration")
    test_critical_severity_in_result(); results.append("[PASS] test_critical_severity")
except Exception as e:
    results.append(f"[FAIL] validator: {e}")

#  anomaly 
try:
    from data_quality.tests.test_anomaly import (
        test_normal_no_anomaly, test_duplicate_timestamp, test_price_jump_detection,
        test_gap_detection, test_l2_freeze_detection
    )
    test_normal_no_anomaly(); results.append("[PASS] test_normal_no_anomaly")
    test_duplicate_timestamp(); results.append("[PASS] test_duplicate_timestamp")
    test_price_jump_detection(); results.append("[PASS] test_price_jump")
    test_gap_detection(); results.append("[PASS] test_gap_detection")
    test_l2_freeze_detection(); results.append("[PASS] test_l2_freeze")
except Exception as e:
    results.append(f"[FAIL] anomaly: {e}")

#  recovery 
try:
    from data_quality.tests.test_recovery import (
        test_info_passes, test_warning_retries_then_fails, test_critical_fails_directly, test_reset_retries
    )
    test_info_passes(); results.append("[PASS] test_info_passes")
    test_warning_retries_then_fails(); results.append("[PASS] test_warning_retries")
    test_critical_fails_directly(); results.append("[PASS] test_critical_fails")
    test_reset_retries(); results.append("[PASS] test_reset_retries")
except Exception as e:
    results.append(f"[FAIL] recovery: {e}")

#  health 
try:
    from data_quality.tests.test_health import (
        test_initial_score_full, test_failed_validations_lower_score,
        test_missing_data_lowers_completeness, test_is_healthy
    )
    test_initial_score_full(); results.append("[PASS] test_initial_score")
    test_failed_validations_lower_score(); results.append("[PASS] test_failed_validations")
    test_missing_data_lowers_completeness(); results.append("[PASS] test_missing_data")
    test_is_healthy(); results.append("[PASS] test_is_healthy")
except Exception as e:
    results.append(f"[FAIL] health: {e}")

#  report 
try:
    from data_quality.tests.test_report import test_empty_report_generates, test_report_includes_errors
    test_empty_report_generates(); results.append("[PASS] test_empty_report")
    test_report_includes_errors(); results.append("[PASS] test_report_errors")
except Exception as e:
    results.append(f"[FAIL] report: {e}")

# -- 输出 --
passed = sum(1 for r in results if r.startswith("[PASS]"))
failed = sum(1 for r in results if r.startswith("[FAIL]"))
total = len(results)

output = f"""
================================================================
  AQF-T M1 Test Results
  Passed: {passed}/{total} | Failed: {failed}
================================================================
""" + "\n".join(results) + f"""
================================================================
  {'ALL PASSED' if failed == 0 else 'SOME FAILED'}
================================================================
"""

with open("test_results.txt", "w", encoding="utf-8") as f:
    f.write(output)

print(output)
