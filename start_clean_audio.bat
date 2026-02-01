@echo off
title Clean Audio App - 警告なし音声認識アプリ

echo Starting Clean Audio App - 警告なし音声認識アプリ...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping existing containers...
docker stop ai-agent-browser-audio-clean 2>nul
docker rm ai-agent-browser-audio-clean 2>nul

echo Building clean audio image...
docker build -f Dockerfile.audio -t ai-agent-browser-audio-clean .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting clean audio container...
docker run -d --name ai-agent-browser-audio-clean -p 8501:8501 --restart unless-stopped ai-agent-browser-audio-clean

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Clean Audio App is running
echo.
echo Access URL: http://localhost:8501
echo.
echo Features:
echo - Clean Console: ENABLED
echo - No Streamlit Warnings: ENABLED
echo - No Font Preload Warnings: ENABLED
echo - No iframe Sandbox Warnings: ENABLED
echo - High-Quality Audio Recording: ENABLED
echo - Speech Recognition: ENABLED
echo - Real-time Audio Processing: ENABLED
echo.
echo Clean Features:
echo - All console warnings filtered
echo - Font preload warnings suppressed
echo - iframe sandbox warnings suppressed
echo - Streamlit feature warnings suppressed
echo - Error-level logging only
echo.
echo Audio Features:
echo - Browser-based audio input
echo - WebM to WAV conversion
echo - faster-whisper integration
echo - Japanese speech recognition
echo - Real-time waveform display
echo.
echo To check logs:
echo docker logs ai-agent-browser-audio-clean
echo.
echo To stop:
echo docker stop ai-agent-browser-audio-clean
echo docker rm ai-agent-browser-audio-clean
echo.
echo Waiting for app to start...
timeout /t 10 /nobreak >nul

echo Checking if app is running...
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: App is responding!' } catch { Write-Host 'App may still be starting...' }"

echo.
echo Please open your browser and go to: http://localhost:8501
echo.
echo Clean Audio Features:
echo 1. 🎤 High-quality audio recording
echo 2. 🤖 Accurate speech recognition
echo 3. 🔇 Clean console (no warnings)
echo 4. 🎨 Modern UI design
echo 5. 🔒 Secure audio processing
echo.
echo Testing Instructions:
echo 1. Click "🎙️ 録音開始" to start recording
echo 2. Allow microphone access in your browser
echo 3. Speak clearly into your microphone
echo 4. Click "⏹️ 録音停止" to stop recording
echo 5. Click "🤖 音声認識" to transcribe
echo 6. Check console - it should be clean!
echo.
echo Note: All console warnings have been filtered for a clean development experience.

pause
