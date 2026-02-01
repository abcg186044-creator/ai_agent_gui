@echo off
title Audio Test App - 音声機能テスト

echo Starting Audio Test App - 音声機能テスト...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping existing test containers...
docker stop ai-agent-simple 2>nul
docker rm ai-agent-simple 2>nul
docker stop ai-agent-audio 2>nul
docker rm ai-agent-audio 2>nul

echo Creating audio test Dockerfile...
(
echo FROM python:3.10-slim
echo.
echo RUN apt-get update ^&^& apt-get install -y ^
echo     curl ^
echo     build-essential ^
echo     pkg-config ^
echo     portaudio19-dev ^
echo     python3-dev ^
echo     python3-setuptools ^
echo     alsa-utils ^
echo     libasound2-dev ^
echo     libportaudio2 ^
echo     libportaudiocpp0 ^
echo     espeak ^
echo     espeak-ng ^
echo     espeak-data ^
echo     libespeak1 ^
echo     libespeak-dev ^
echo     ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo WORKDIR /app
echo.
echo RUN pip install --upgrade pip
echo RUN pip install --no-cache-dir --upgrade pip setuptools wheel
echo RUN pip install --no-cache-dir streamlit==1.28.1
echo RUN pip install --no-cache-dir sounddevice==0.4.6
echo RUN pip install --no-cache-dir pyttsx3==2.90
echo RUN pip install --no-cache-dir numpy==1.24.3
echo RUN pip install --no-cache-dir torch==2.1.0 torchaudio==2.1.0
echo RUN pip install --no-cache-dir "av^>=12.1.0"
echo.
echo COPY audio_test_app.py /app/audio_test_app.py
echo.
echo EXPOSE 8501
echo.
echo CMD ["streamlit", "run", "audio_test_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
) > Dockerfile.audio

echo Building audio test image...
docker build -f Dockerfile.audio -t ai-agent-audio .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting audio test container...
docker run -d --name ai-agent-audio -p 8501:8501 --restart unless-stopped ai-agent-audio

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Audio Test App is running
echo.
echo Access URL: http://localhost:8501
echo.
echo Features:
echo - Basic Streamlit: ENABLED
echo - Audio Input: ENABLED (sounddevice)
echo - Text-to-Speech: ENABLED (pyttsx3)
echo - PyTorch Audio: ENABLED
echo - Audio Processing: ENABLED
echo.
echo Audio Libraries:
echo - sounddevice: v0.4.6
echo - pyttsx3: v2.90
echo - numpy: v1.24.3
echo - torch: v2.1.0
echo - torchaudio: v2.1.0
echo - av: v12.1.0+
echo.
echo To check logs:
echo docker logs ai-agent-audio
echo.
echo To stop:
echo docker stop ai-agent-audio
echo docker rm ai-agent-audio
echo.
echo Waiting for app to start...
timeout /t 15 /nobreak >nul

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
echo.
echo Test the following features:
echo 1. Audio device detection
echo 2. Voice recording test
echo 3. Text-to-speech test
echo 4. PyTorch audio processing

pause
