@echo off
rem Runs all Haunted House tests and adds the results to tests\stats\test_runs.csv
cd /d "%~dp0"
python run_tests.py %*
pause
