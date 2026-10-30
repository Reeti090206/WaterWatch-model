Set-Location -Path $PSScriptRoot
$env:PYTHONPATH = "D:\Lib\site-packages;$PSScriptRoot"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting WaterWatch AI - Backend & Frontend Services" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\Lib\site-packages;$PSScriptRoot'; & 'D:\python.exe' waterwatch_integration/run_integration.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'waterwatch_integration/frontend'; npm run dev"

Write-Host "`nBackend API & Swagger: http://127.0.0.1:8080/docs" -ForegroundColor Green
Write-Host "Frontend Dashboard:   http://localhost:3000`n" -ForegroundColor Green

