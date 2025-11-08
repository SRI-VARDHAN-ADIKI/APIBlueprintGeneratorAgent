@echo off
REM Startup script for README Generator Agent on Windows

echo ====================================
echo   README Generator Agent
echo   Starting Application...
echo ====================================

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv\ (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting FastAPI server...
start "FastAPI Server" cmd /k "venv\Scripts\activate.bat && python main.py"

timeout /t 3 /nobreak > nul

echo.
echo Starting Streamlit UI...
start "Streamlit UI" cmd /k "venv\Scripts\activate.bat && streamlit run ui\streamlit_app.py"

echo.
echo ====================================
echo   Application Started!
echo   FastAPI: http://localhost:8000
echo   Streamlit: http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo ====================================
echo.
echo Press any key to stop all servers...
pause > nul

REM Kill the servers
taskkill /F /FI "WINDOWTITLE eq FastAPI Server*" > nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Streamlit UI*" > nul 2>&1

echo Servers stopped.
