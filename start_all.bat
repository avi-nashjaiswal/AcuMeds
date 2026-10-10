@echo off
title AcuMeds Multi-System Launcher
echo ======================================================================
echo           Starting All 5 AcuMeds Systems Simultaneously
echo ======================================================================

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run_all.py %*
) else (
    python run_all.py %*
)

pause
