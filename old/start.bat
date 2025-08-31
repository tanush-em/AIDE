@echo off
echo 🚀 Starting AIDE - Academic AI Management System
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo [INFO] Checking system requirements...
echo [SUCCESS] Python: 
python --version
echo [SUCCESS] Node.js: 
node --version
echo [SUCCESS] npm: 
npm --version

REM Backend setup
echo [INFO] Setting up backend...

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python dependencies installed successfully
)

REM Start backend in background
echo [INFO] Starting backend server...
start "Backend Server" python app.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:5001/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend server failed to start
    pause
    exit /b 1
) else (
    echo [SUCCESS] Backend server started successfully on http://localhost:5001
)

REM Go back to root directory
cd ..

REM Frontend setup
echo [INFO] Setting up frontend...

cd aide

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
npm install

if errorlevel 1 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
) else (
    echo [SUCCESS] Node.js dependencies installed successfully
)

REM Start frontend in background
echo [INFO] Starting frontend server...
start "Frontend Server" npm run dev

REM Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

REM Check if frontend is running
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend server failed to start
    pause
    exit /b 1
) else (
    echo [SUCCESS] Frontend server started successfully on http://localhost:3000
)

REM Go back to root directory
cd ..

echo.
echo 🎉 AIDE is now running!
echo =======================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5001
echo.
echo Demo Credentials:
echo Student:  tmtanush@gmail.com / 1234
echo Faculty:  justindhas@gmail.com / 1234
echo.
echo Press any key to stop all services...

pause

REM Stop services
echo [INFO] Stopping services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo [SUCCESS] All services stopped
