@echo off
title LiteTutor Edge Node Launcher

echo ===================================================
echo       LiteTutor 2.5 Edge Node Launcher
echo ===================================================
echo.

echo [1/4] Skipping Cpolar (use WebUI tunnel)...

echo [2/4] Changing to working directory...
cd /d D:\MEAdesktop\work\skills

echo [3/4] Waking up Conda and Server Node...
:: 使用您提供的精确路径强行唤醒 Conda
start "LiteTutor Server Node" cmd /k "set EDGE_PUBLIC_URL=https://lt.hk.cpolar.io && call D:\conda\Scripts\activate.bat && conda activate lite_tutor && python server.py"

timeout /t 3 /nobreak >nul

echo [4/4] Starting Streamlit Frontend...
start "LiteTutor Streamlit" cmd /k "call D:\conda\Scripts\activate.bat && conda activate lite_tutor && cd /d D:\MEAdesktop\work\skills && streamlit run app.py"

echo.
echo ===================================================
echo [SUCCESS] All tasks dispatched!
echo You can close this main launcher window now.
echo ===================================================
pause
