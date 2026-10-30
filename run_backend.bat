@echo off
cd /d "%~dp0"
set "PYTHONPATH=D:\Lib\site-packages;%CD%"
"D:\python.exe" waterwatch_integration\run_integration.py
pause

