@echo off
title Audio Device Selector - マイクデバイス選択機能

echo Starting Audio Device Selector - マイクデバイス選択機能...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping existing containers...
docker stop ai-agent-audio 2>nul
docker rm ai-agent-audio 2>nul
docker stop ai-agent-selector 2>nul
docker rm ai-agent-selector 2>nul

echo Building device selector image...
docker build -f Dockerfile.audio -t ai-agent-selector .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting device selector container...
docker run -d --name ai-agent-selector -p 8501:8501 --restart unless-stopped ai-agent-selector

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Audio Device Selector is running
echo.
echo Access URL: http://localhost:8501
echo.
echo New Features:
echo - Device Selection: ENABLED
echo - Microphone Switching: ENABLED
echo - Input Device Detection: ENABLED
echo - Device-specific Recording: ENABLED
echo - TTS Voice Selection: ENABLED
echo.
echo Device Selection Features:
echo - List all available input devices
echo - Select specific microphone by ID
echo - Display device information
echo - Test recording with selected device
echo - Switch between devices dynamically
echo.
echo To check logs:
echo docker logs ai-agent-selector
echo.
echo To stop:
echo docker stop ai-agent-selector
echo docker rm ai-agent-selector
echo.
echo Waiting for app to start...
timeout /t 10 /nobreak >nul

echo Checking if app is running...
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: App is responding!' } catch { Write-Host 'App may still be starting...' }"

echo.
echo Please open your browser and go to: http://localhost:8501
echo.
echo New Features to Test:
echo 1. 🎤 Microphone device selection in sidebar
echo 2. 🎙️ Device-specific recording test
echo 3. 🗣️ TTS voice selection
echo 4. 📊 Detailed device information
echo 5. 🔧 Troubleshooting help

pause
