@echo off
setlocal
cd /d "%~dp0backend"
if not exist .env (
  echo ERROR: backend\.env is missing. Copy .env.example to .env and edit credentials.
  pause
  exit /b 1
)
if not exist .venv (
  echo Creating Python virtual environment...
  py -3.11 -m venv .venv
  if errorlevel 1 (echo Python 3.11 not found. Install Python 3.11 and retry.& pause & exit /b 1)
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed.& pause & exit /b 1)
echo Checking database connections via API startup...
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
