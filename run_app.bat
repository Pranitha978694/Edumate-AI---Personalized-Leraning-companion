@echo off
echo Starting EduMate AI - Backend and Frontend...

:: Start Python Backend in a new window
echo Starting Python Backend...
start "EduMate Backend" cmd /k "python backend/main.py"

:: Start Next.js Frontend in a new window
echo Starting Frontend...
start "EduMate Frontend" cmd /k "npm run dev"

echo Both processes are starting in separate windows.
pause
