@echo off
echo 🚀 Starting AI Chatbot Backend Server...
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Start the server
echo 🚀 Starting server...
python start.py

pause
