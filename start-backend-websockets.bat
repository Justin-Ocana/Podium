@echo off
echo ========================================
echo Starting Podium Backend with WebSockets
echo ========================================
echo.

cd backend

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Checking Redis...
python check_redis.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Redis is not running!
    echo WebSockets will not work without Redis.
    echo.
    echo To start Redis:
    echo   - Run: start-redis-docker.bat
    echo   - Or install Memurai from https://www.memurai.com/get-memurai
    echo.
    pause
)

echo.
echo Starting Django with Daphne (ASGI server for WebSockets)...
echo Server will be available at: http://localhost:8000
echo WebSocket endpoint: ws://localhost:8000/ws/notifications/
echo.
echo Press Ctrl+C to stop the server
echo.

python -m daphne -b 0.0.0.0 -p 8000 --application-close-timeout 60 config.asgi:application

pause
