@echo off
title AI Agent System - Voice Fixed v5 (Upgraded)

echo Starting AI Agent System with Voice Fix v5 (Upgraded)...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Cleaning up...
docker-compose -f docker-compose.voice.fixed.v5.yml down >nul 2>&1
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
docker-compose -f docker-compose.voice.fixed.v5.yml build --no-cache

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting...
docker-compose -f docker-compose.voice.fixed.v5.yml up -d

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
echo Voice Features:
echo - pyttsx3: ENABLED
echo - VOICEVOX: ENABLED
echo - eSpeak: ENABLED
echo - Audio Devices: ENABLED
echo.
echo Audio Engine Status:
echo - TTS Engines: Multiple
echo - Recording: Smart Buffering
echo - Playback: Auto-detection
echo.
echo Build Compatibility:
echo - PyAV: v12.1.0+ (Pre-compiled Binary)
echo - faster-whisper: v1.0.3+ (Upgraded)
echo - numpy: Latest (Compatible)
echo - setuptools: Latest (Fixed distutils)
echo - FFmpeg: All dev libraries installed
echo.
echo To check container logs:
echo docker logs ai-agent-app
echo docker logs ai-voicevox
echo.
echo To test audio devices:
echo docker exec ai-agent-app python -c "import sounddevice; print(sounddevice.query_devices())"

pause
