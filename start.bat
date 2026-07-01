@echo off
echo Starting Spending Auditor...

:: Start backend
start "Backend" cmd /k "cd /d C:\Users\pur03\Documents\spending-auditor\backend && C:\Users\pur03\Documents\spending-auditor\venv\Scripts\activate.bat && uvicorn main:app --port 8000"

:: Wait 5 seconds for backend to start
timeout /t 5 /nobreak

:: Start frontend
start "Frontend" cmd /k "cd /d C:\Users\pur03\Documents\spending-auditor\frontend && npm run dev"

echo Both servers starting...
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173
pause