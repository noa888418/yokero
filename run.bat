@echo off
cd /d "%~dp0"
python main.py 2>nul || py main.py
if errorlevel 1 pause
