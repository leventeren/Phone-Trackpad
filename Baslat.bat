@echo off
chcp 65001 >nul
title Phone Trackpad

echo.
echo  Gerekli kutuphaneler kontrol ediliyor...
python -m pip install --quiet websockets pyautogui

echo.
python server.py

pause
