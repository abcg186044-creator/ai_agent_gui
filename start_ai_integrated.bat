@echo off
title AI Integrated Voice Chat - AI音声対話システム

echo Starting AI Integrated Voice Chat - AI音声対話システム...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping existing containers...
docker stop ai-agent-integrated 2>nul
docker rm ai-agent-integrated 2>nul

echo Building AI integrated image...
docker build -f Dockerfile.audio -t ai-agent-integrated .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting AI integrated container...
docker run -d --name ai-agent-integrated -p 8501:8501 --restart unless-stopped ai-agent-integrated

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: AI Integrated Voice Chat is running
echo.
echo Access URL: http://localhost:8501
echo.
echo AI Features:
echo - Voice Input: ENABLED
echo - Speech Recognition: ENABLED
echo - AI Conversation: ENABLED
echo - OpenAI Integration: ENABLED
echo - Conversation History: ENABLED
echo - TTS (Text-to-Speech): ENABLED
echo - Real-time Audio Processing: ENABLED
echo.
echo Audio Features:
echo - Browser-based audio input
echo - Real-time volume monitoring
echo - WebM to WAV conversion
echo - High-quality audio capture
echo - Noise cancellation
echo - Echo cancellation
echo.
echo AI Features:
echo - OpenAI GPT-3.5-turbo integration
echo - Japanese language support
echo - Context-aware conversation
echo - Conversation history management
echo - JSON export functionality
echo - Error handling and retry
echo.
echo Setup Instructions:
echo 1. Open http://localhost:8501 in your browser
echo 2. Set your OpenAI API key in the sidebar
echo 3. Test your microphone with the "🔧 マイクテスト" button
echo 4. Start recording with "🎙️ 録音開始"
echo 5. Click "🤖 音声認識とAI応答" for full AI processing
echo.
echo Usage Flow:
echo 1. 🔧 Test microphone
echo 2. 🎙️ Record your voice
echo 3. 🤖 Get AI response
echo 4. 💬 View conversation history
echo 5. 💾 Save conversation if desired
echo.
echo To check logs:
echo docker logs ai-agent-integrated
echo.
echo To stop:
echo docker stop ai-agent-integrated
echo docker rm ai-agent-integrated
echo.
echo Waiting for app to start...
timeout /t 10 /nobreak >nul

echo Checking if app is running...
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: App is responding!' } catch { Write-Host 'App may still be starting...' }"

echo.
echo Please open your browser and go to: http://localhost:8501
echo.
echo AI Voice Chat Features:
echo 1. 🎙️ High-quality voice recording
echo 2. 🤖 AI-powered conversation
echo 3. 💬 Natural language processing
echo 4. 📊 Conversation history tracking
echo 5. 🔊 Optional text-to-speech output
echo 6. 💾 Export conversation data
echo.
echo Technical Stack:
echo - WebRTC/MediaRecorder API
echo - faster-whisper (speech recognition)
echo - OpenAI GPT-3.5-turbo (AI response)
echo - pyttsx3 (text-to-speech)
echo - Streamlit (UI framework)
echo - Docker (containerization)
echo.
echo Note: You need to set your OpenAI API key in the sidebar to use AI features.

pause
