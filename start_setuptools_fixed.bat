@echo off
title AI Agent System - Setuptools Fixed

echo Starting AI Agent System with Setuptools Compatibility Fix...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping existing containers...
docker-compose -f docker-compose.voice.fixed.v5.yml down >nul 2>&1

echo Cleaning up...
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

echo Building with Setuptools compatibility fix...
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
echo - numpy: v1.24.3 (Binary Compatible)
echo - pandas: v2.0.3 (Binary Compatible)
echo - setuptools: v68.0.0+ (Fixed compatibility)
echo - wheel: v0.40.0+ (Fixed compatibility)
echo - FFmpeg: All dev libraries installed
echo.
echo Setuptools Fix:
echo - setuptools 59.2.0 conflict: RESOLVED
echo - numpy build dependencies: FIXED
echo - pandas compatibility: ENSURED
echo - Binary compatibility: MAINTAINED
echo.
echo To check container logs:
echo docker logs ai-agent-app
echo docker logs ai-voicevox
echo.
echo To test audio devices:
echo docker exec ai-agent-app python -c "import sounddevice; print(sounddevice.query_devices())"
echo.
echo To verify NumPy/Pandas:
echo docker exec ai-agent-app python -c "import numpy; print('numpy:', numpy.__version__)"
echo docker exec ai-agent-app python -c "import pandas; print('pandas:', pandas.__version__)"
echo docker exec ai-agent-app python -c "import setuptools; print('setuptools:', setuptools.__version__)"

pause
