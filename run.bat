@echo off
cd /d "%~dp0"
title Distributed Snapshot Simulator (Chandy-Lamport)
echo ====================================================================
echo     Launching Distributed Snapshot Simulator (Chandy-Lamport)
echo     Distributed Computing Final Project & Visualizer
echo ====================================================================
echo.

REM Determine python command (prioritize local python shim or standard python)
set PY_CMD=python
where python >nul 2>nul
if %errorlevel% neq 0 (
    set PY_CMD="C:\Users\sanja\AppData\Local\Python\pythoncore-3.15-64\python.exe"
)

echo Starting HTTP Simulator Server on port 8080...
start "" http://localhost:8080
%PY_CMD% server.py 8080
pause
