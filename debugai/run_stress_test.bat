@echo off
cd /d "%~dp0"
echo Running DebugAI Stress Test...
echo.
"C:\Users\AKSHAY\AppData\Local\Programs\Python\Python312\python.exe" tests\stress_test.py
echo.
echo ========================================
echo Test completed. 
echo ========================================
pause
