@echo off
title AcuMeds Production WSGI Launcher
echo ======================================================================
echo           Starting AcuMeds Production Server (Waitress WSGI)
echo ======================================================================

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" prod_server.py %*
) else (
    python prod_server.py %*
)

pause
