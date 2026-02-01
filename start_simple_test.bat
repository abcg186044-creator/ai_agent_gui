@echo off
title Simple Test App - Basic Functionality

echo Starting Simple Test App - Basic Functionality Check...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping any existing containers...
docker stop ai-agent-simple 2>nul
docker rm ai-agent-simple 2>nul

echo Creating simple test Dockerfile...
echo FROM python:3.10-slim > Dockerfile.simple
echo. >> Dockerfile.simple
echo RUN apt-get update ^&^& apt-get install -y curl ^&^& rm -rf /var/lib/apt/lists/* >> Dockerfile.simple
echo. >> Dockerfile.simple
echo WORKDIR /app >> Dockerfile.simple
echo. >> Dockerfile.simple
echo RUN pip install --upgrade pip >> Dockerfile.simple
echo RUN pip install --no-cache-dir streamlit==1.28.1 >> Dockerfile.simple
echo. >> Dockerfile.simple
echo COPY simple_test_app.py /app/simple_test_app.py >> Dockerfile.simple
echo. >> Dockerfile.simple
echo EXPOSE 8501 >> Dockerfile.simple
echo. >> Dockerfile.simple
echo CMD ["streamlit", "run", "simple_test_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"] >> Dockerfile.simple

echo Building simple test image...
docker build -f Dockerfile.simple -t ai-agent-simple .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting simple test container...
docker run -d --name ai-agent-simple -p 8501:8501 --restart unless-stopped ai-agent-simple

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Simple Test App is running
echo.
echo Access URL: http://localhost:8501
echo.
echo Features:
echo - Basic Streamlit: ENABLED
echo - Interactive Elements: ENABLED
echo - Real-time Updates: ENABLED
echo.
echo To check logs:
echo docker logs ai-agent-simple
echo.
echo To stop:
echo docker stop ai-agent-simple
echo docker rm ai-agent-simple
echo.
echo Waiting for app to start...
timeout /t 10 /nobreak >nul

echo Checking if app is running...
curl -f http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo WARNING: App may still be starting...
    echo Please wait a moment and try accessing: http://localhost:8501
) else (
    echo SUCCESS: App is responding!
)

echo.
echo Please open your browser and go to: http://localhost:8501

pause
