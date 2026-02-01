@echo off
title AI Agent System - Debug Mode

echo Starting AI Agent System in Debug Mode...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Cleaning up...
docker-compose -f docker-compose.network.fixed.yml down >nul 2>&1
docker system prune -f >nul 2>&1

echo Creating volumes...
docker volume create ai_chroma_data 2>nul
docker volume create ai_conversation_history 2>nul
docker volume create ai_user_settings 2>nul
docker volume create ai_logs 2>nul
docker volume create ai_voicevox_data 2>nul
docker volume create ai_redis_data 2>nul
docker volume create python_libs 2>nul
docker volume create python_cache 2>nul

echo Building...
docker-compose -f docker-compose.network.fixed.yml build --no-cache

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting...
docker-compose -f docker-compose.network.fixed.yml up -d

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: AI Agent System is running
echo.
echo Access URLs:
echo - Local: http://localhost:8501
echo - Debug: http://localhost:8501 (Debug Mode)
echo - Network: http://[YOUR_IP]:8501
echo.
echo Debug Features:
echo - Detailed connection logging
echo - URL testing with status
echo - Error tracking and reporting
echo - Environment variable display
echo.
echo To check container logs:
echo docker logs ai-agent-app
echo docker logs ai-ollama
echo.
echo To test connection manually:
echo docker exec ai-agent-app curl -f http://ollama:11434/api/tags
echo docker exec ai-agent-app curl -f http://localhost:11434/api/tags

pause
