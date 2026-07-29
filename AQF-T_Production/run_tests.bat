@echo off
cd /d D:\AQF-T\AQF-T_Production
python run_tests.py
echo.
echo Results saved to test_results.txt
notepad test_results.txt
