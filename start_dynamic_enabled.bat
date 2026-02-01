@echo off
title AI Agent System - Dynamic Install Enabled

echo Starting AI Agent System with Dynamic Install...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Cleaning up...
docker-compose -f docker-compose.dynamic.enabled.yml down >nul 2>&1
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
docker-compose -f docker-compose.dynamic.enabled.yml build --no-cache

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting...
docker-compose -f docker-compose.dynamic.enabled.yml up -d

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: AI Agent System is running
echo Access: http://localhost:8501

pause
