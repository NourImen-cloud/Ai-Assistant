@echo off
title Echo Mind - Personal AI Assistant
color 0B

echo ===================================================
echo           ECHO MIND - AI ASSISTANT LAUNCHER
echo ===================================================
echo.

:: Check for .env file
if not exist ".env" (
    echo [.env] not found. Creating from .env.example...
    copy .env.example .env
    echo Please configure your GROQ_API_KEY in .env if needed.
    echo.
)

:: Start Backend API Server
echo [1/2] Starting Echo Mind Backend Server (Port 8001)...
start "Echo Mind - Backend API" cmd /k "python api/server.py"

:: Wait 2 seconds for backend to initialize
timeout /t 2 /nobreak >nul

:: Start Frontend UI
echo [2/2] Starting Frontend UI...
cd frontend
start "Echo Mind - Web UI" cmd /k "npm run dev"

echo.
echo ===================================================
echo   Echo Mind is running!
echo   UI:      http://localhost:5173
echo   API:     http://127.0.0.1:8001
echo   Swagger: http://127.0.0.1:8001/docs
echo ===================================================
echo.
pause
