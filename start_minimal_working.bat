@echo off
title AI Agent System - Minimal Working Version

echo Starting AI Agent System with Minimal Working Configuration...

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

echo Building minimal working version...
echo This version uses only essential packages to ensure basic functionality...

REM Create a simple working Dockerfile
echo FROM python:3.10-slim > Dockerfile.minimal
echo. >> Dockerfile.minimal
echo RUN apt-get update ^&^& apt-get install -y curl wget git build-essential pkg-config portaudio19-dev python3-dev python3-setuptools alsa-utils libasound2-dev libportaudio2 libportaudiocpp0 espeak espeak-ng espeak-data libespeak1 libespeak-dev ffmpeg libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libswresample-dev ^&^& rm -rf /var/lib/apt/lists/* >> Dockerfile.minimal
echo. >> Dockerfile.minimal
echo WORKDIR /app >> Dockerfile.minimal
echo. >> Dockerfile.minimal
echo RUN pip install --upgrade pip >> Dockerfile.minimal
echo RUN pip install --no-cache-dir --upgrade pip setuptools wheel >> Dockerfile.minimal
echo RUN pip install --no-cache-dir streamlit==1.28.1 requests==2.31.0 python-dotenv==1.0.0 >> Dockerfile.minimal
echo RUN pip install --no-cache-dir torch==2.1.0 torchaudio==2.1.0 torchvision==0.16.0 >> Dockerfile.minimal
echo RUN pip install --no-cache-dir sounddevice==0.4.6 pyttsx3==2.90 >> Dockerfile.minimal
echo RUN pip install --no-cache-dir redis==4.6.0 openai==0.28.1 >> Dockerfile.minimal
echo RUN pip install --no-cache-dir "av>=12.1.0" >> Dockerfile.minimal
echo RUN pip install --no-cache-dir "sentence-transformers==2.2.2" >> Dockerfile.minimal
echo RUN pip install --no-cache-dir "faster-whisper>=1.0.3" >> Dockerfile.minimal
echo. >> Dockerfile.minimal
echo COPY voice_fixed_ai_agent.py /app/voice_fixed_ai_agent.py >> Dockerfile.minimal
echo COPY scripts/ /app/scripts/ >> Dockerfile.minimal
echo. >> Dockerfile.minimal
echo RUN mkdir -p /app/data/chroma /app/data/conversations /app/data/settings /app/data/logs >> Dockerfile.minimal
echo. >> Dockerfile.minimal
echo EXPOSE 8501 >> Dockerfile.minimal
echo. >> Dockerfile.minimal
echo CMD ["streamlit", "run", "voice_fixed_ai_agent.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"] >> Dockerfile.minimal

echo Building minimal Docker image...
docker build -f Dockerfile.minimal -t ai-agent-minimal .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting minimal container...
docker run -d --name ai-agent-minimal -p 8501:8501 --restart unless-stopped ai-agent-minimal

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: AI Agent System is running (Minimal Version)
echo.
echo Access URLs:
echo - Local: http://localhost:8501
echo - Network: http://[YOUR_IP]:8501
echo.
echo Minimal Version Features:
echo - Basic Streamlit: ENABLED
echo - PyTorch: ENABLED
echo - Audio Processing: ENABLED
echo - TTS: ENABLED
echo.
echo To check container logs:
echo docker logs ai-agent-minimal
echo.
echo To stop container:
echo docker stop ai-agent-minimal
echo docker rm ai-agent-minimal

pause
