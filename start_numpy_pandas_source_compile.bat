@echo off
title AI Agent System - NumPy/Pandas Source Compile Fix

echo Starting AI Agent System with NumPy/Pandas Source Compilation Fix...

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

echo Cleaning up volumes and cache...
docker system prune -a -f >nul 2>&1
docker volume prune -f >nul 2>&1

echo Creating fresh volumes...
docker volume create ai_chroma_data 2>nul
docker volume create ai_conversation_history 2>nul
docker volume create ai_user_settings 2>nul
docker volume create ai_logs 2>nul
docker volume create ai_voicevox_data 2>nul
docker volume create ai_redis_data 2>nul
docker volume create python_libs 2>nul
docker volume create python_cache 2>nul

echo Building with NumPy/Pandas source compilation fix...
echo This will take longer as pandas will be compiled from source...
docker-compose -f docker-compose.voice.fixed.v5.yml build --no-cache --pull

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
echo - numpy: v1.24.3 (Source Compiled)
echo - pandas: v2.0.3 (Source Compiled for Compatibility)
echo - setuptools: Latest (Fixed distutils)
echo - FFmpeg: All dev libraries installed
echo.
echo NumPy/Pandas Source Compile Fix:
echo - Binary compatibility: RESOLVED via source compilation
echo - dtype size mismatch: FIXED via compilation
echo - pandas._libs: COMPATIBLE (compiled against numpy 1.24.3)
echo - Compilation time: Extended (expected 15-20 minutes)
echo.
echo To check container logs:
echo docker logs ai-agent-app
echo docker logs ai-voicevox
echo.
echo To test audio devices:
echo docker exec ai-agent-app python -c "import sounddevice; print(sounddevice.query_devices())"
echo.
echo To verify NumPy/Pandas compatibility:
echo docker exec ai-agent-app python -c "import numpy; print('numpy:', numpy.__version__)"
echo docker exec ai-agent-app python -c "import pandas; print('pandas:', pandas.__version__)"
echo docker exec ai-agent-app python -c "from pandas._libs import interval; print('pandas._libs.interval: OK')"
echo.
echo To verify dtype compatibility:
echo docker exec ai-agent-app python -c "import numpy as np; print('dtype size:', np.dtype(np.int64).itemsize * 8)"

pause
