@echo off
echo Starting Next.js frontend...
start "Frontend" cmd /k "cd C:\edumate_ai && npm run dev"

echo Starting Python backend...
start "Backend" cmd /k "cd C:\edumate_ai && python backend/main.py"

echo Both servers are starting in separate windows.