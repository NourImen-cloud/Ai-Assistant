@echo off
title Echo Mind - Production Server
color 0A

echo ===================================================
echo           ECHO MIND - PRODUCTION LAUNCHER
echo ===================================================
echo.

cd /d "%~dp0"

:: 1. Ensure frontend production build exists
if not exist "frontend\dist\index.html" (
    echo [1/2] Building Frontend UI for production...
    cd frontend
    call npm run build
    cd ..
) else (
    echo [1/2] Frontend production build found.
)

:: 2. Launch FastAPI backend + UI (single unified server on port 8001)
echo [2/2] Starting Echo Mind on http://127.0.0.1:8001 ...
start "" http://127.0.0.1:8001

python api/server.py
