@echo off
title LiteTutor Edge Node Launcher

echo ===================================================
echo       LiteTutor 2.5 Edge Node Launcher
echo ===================================================
echo.

echo [1/3] Starting Cpolar Tunnel...
start "Cpolar Tunnel (Port 8000)" cmd /k "cpolar http 8000"

timeout /t 2 /nobreak >nul

echo [2/3] Changing to working directory...
cd /d D:\MEAdesktop\work\skills

echo [3/3] Waking up Conda and Server Node...
:: 使用您提供的精确路径强行唤醒 Conda
start "LiteTutor Server Node" cmd /k "call D:\conda\Scripts\activate.bat && conda activate lite_tutor && python server.py"

echo.
echo ===================================================
echo [SUCCESS] All tasks dispatched!
echo You can close this main launcher window now.
echo ===================================================
pause