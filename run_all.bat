@echo off
cd /d "%~dp0"
echo ========================================================
echo  Starting WaterWatch AI Services
echo ========================================================
start "WaterWatch AI - FastAPI Backend (Port 8080)" cmd /k "%~dp0run_backend.bat"
start "WaterWatch AI - Next.js Frontend (Port 3000)" cmd /k "%~dp0run_frontend.bat"
echo.
echo Both services are starting in dedicated terminal windows:
echo - Backend API & Docs: http://127.0.0.1:8080/docs
echo - Interactive Dashboard: http://localhost:3000
echo ========================================================

