@echo off
echo Starting Next.js + Flask Full-Stack Application...

REM Start Flask backend
echo Starting Flask backend...
cd backend
call venv\Scripts\activate
start "Flask Backend" python app.py
cd ..

REM Wait a moment for backend to start
timeout /t 2 /nobreak >nul

REM Start Next.js frontend
echo Starting Next.js frontend...
cd frontend
start "Next.js Frontend" npm run dev
cd ..

echo Applications started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:5000
echo.
echo Press any key to stop both applications...
pause >nul

REM Kill background processes (Windows equivalent)
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
