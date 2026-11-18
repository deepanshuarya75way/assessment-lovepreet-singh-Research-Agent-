@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
)

echo Installing/checking dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Starting Research Agent v4...
echo Open http://127.0.0.1:8000
echo.
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
