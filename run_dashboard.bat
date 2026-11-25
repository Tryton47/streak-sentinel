@echo off
title GitHub Streak Sentinel - Apple Glass Dashboard
echo ========================================================
echo  GitHub Streak Sentinel - macOS Apple Glass Edition
echo ========================================================
echo.

set PYTHON_CMD=python
if exist "C:\Users\andhi\AppData\Local\Programs\Python\Python313\python.exe" (
    set PYTHON_CMD="C:\Users\andhi\AppData\Local\Programs\Python\Python313\python.exe"
)

echo Memulai server...
echo Akses di PC  : http://localhost:8000
echo Akses di HP  : http://192.168.0.102:8000
echo.
%PYTHON_CMD% main.py --server
pause
