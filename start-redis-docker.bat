@echo off
echo Starting Redis with Docker...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Redis container already exists
docker ps -a | findstr podium-redis >nul 2>&1
if %errorlevel% equ 0 (
    echo Redis container already exists. Starting it...
    docker start podium-redis
) else (
    echo Creating and starting new Redis container...
    docker run -d --name podium-redis -p 6379:6379 redis:latest
)

echo.
echo ✅ Redis is now running on localhost:6379
echo.
echo To stop Redis: docker stop podium-redis
echo To remove Redis: docker rm podium-redis
echo.
pause
