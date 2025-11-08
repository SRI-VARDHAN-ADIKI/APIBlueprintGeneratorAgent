@echo off
REM Development mode - with auto-reload
echo ================================================
echo README Generator Agent - Development Mode
echo ================================================
echo Auto-reload enabled (only watches app/ and ui/)
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run development server
python main.py
