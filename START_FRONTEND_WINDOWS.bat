@echo off
setlocal
cd /d "%~dp0frontend"
if not exist .env.local (
  echo NEXT_PUBLIC_API_URL=http://localhost:8000>.env.local
)
if not exist node_modules (
  echo Installing frontend dependencies...
  call npm install
  if errorlevel 1 (echo npm install failed.& pause & exit /b 1)
)
call npm run dev
pause
