@echo off
title AI Agent System - Network Fixed

echo Starting AI Agent System with Network Fix...

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
echo - Network: http://[YOUR_IP]:8501
echo.
echo Network Features:
echo - Container communication: ENABLED
echo - External access: ENABLED
echo - Auto IP detection: ENABLED
echo - Connection fallback: ENABLED
echo.
echo PyTorch Version Fix:
echo - torch: 2.1.0 (compatible)
echo - torchaudio: 2.1.0 (compatible)
echo - torchvision: 0.16.0 (compatible)
echo.
echo Privacy Settings:
echo - Usage stats: DISABLED
echo - Data collection: DISABLED
echo - Anonymous metrics: DISABLED

pause
