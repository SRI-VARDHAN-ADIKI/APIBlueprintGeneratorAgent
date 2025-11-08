@echo off
REM Production mode - no auto-reload
echo ================================================
echo README Generator Agent - Production Mode
echo ================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run production server
python run_production.py
