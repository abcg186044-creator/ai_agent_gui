@echo off
title Ollama + VRM + 音声認識 AIエージェントシステム

echo Starting Ollama + VRM + 音声認識 AIエージェントシステム...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping existing containers...
docker stop ai-agent-ollama-vrm 2>nul
docker rm ai-agent-ollama-vrm 2>nul

echo Building Ollama VRM integrated image...
docker build -f Dockerfile.audio -t ai-agent-ollama-vrm .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting Ollama VRM integrated container...
docker run -d --name ai-agent-ollama-vrm -p 8501:8501 -p 8000:8000 --restart unless-stopped ai-agent-ollama-vrm

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Ollama VRM AI Agent System is running
echo.
echo Access URLs:
echo - Main App: http://localhost:8501
echo - API Server: http://localhost:8000
echo - VRM Avatar: http://localhost:8000/avatar.vrm
echo.
echo System Features:
echo - Ollama Integration: ENABLED
echo - Llama3.1:8b Model: ENABLED
echo - VRM Avatar Display: ENABLED
echo - Voice Recognition: ENABLED
echo - Voice Synthesis: ENABLED
echo - Multi-Personality System: ENABLED
echo - Conversation History: ENABLED
echo.
echo AI Features:
echo - Local AI Processing (Ollama)
echo - 3D Avatar Integration (VRM)
echo - Browser-based Audio Input
echo - Real-time Voice Recognition
echo - Japanese Language Support
echo - Multi-Personality AI
echo.
echo Personality System:
echo - 👥 親友エンジニア (Friendly Engineer)
echo - 🪞 分身 (Copy/Alter Ego)
echo - 🎓 エキスパート (Expert)
echo.
echo Setup Instructions:
echo 1. Make sure Ollama is installed and running on host
echo 2. Open http://localhost:8501 in your browser
echo 3. Test your microphone with the "🔧 マイクテスト" button
echo 4. Select personality from sidebar
echo 5. Check Ollama connection in sidebar
echo 6. Download llama3.1:8b model if needed
echo 7. Start voice conversation with AI
echo.
echo Usage Flow:
echo 1. 🔧 Test microphone
echo 2. 🎭 Select personality
echo 3. 🔍 Check Ollama connection
echo 4. 🎤 Record voice input
echo 5. 🤖 Get AI response
echo 6. 🤖 Watch VRM avatar expression
echo 7. 💾 Save conversation if desired
echo.
echo Prerequisites:
echo - Ollama installed on host system
echo - llama3.1:8b model downloaded
echo - VRM avatar file (avatar.vrm) in static folder
echo - Microphone access permission
echo.
echo To check logs:
echo docker logs ai-agent-ollama-vrm
echo.
echo To stop:
echo docker stop ai-agent-ollama-vrm
echo docker rm ai-agent-ollama-vrm
echo.
echo Waiting for app to start...
timeout /t 15 /nobreak >nul

echo Checking if app is running...
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Main App is responding!' } catch { Write-Host 'Main App may still be starting...' }"
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: API Server is responding!' } catch { Write-Host 'API Server may still be starting...' }"

echo.
echo Please open your browser and go to: http://localhost:8501
echo.
echo Ollama VRM AI Agent Features:
echo 1. 🎙️ High-quality voice recording
echo 2. 🤖 Local AI processing (Ollama)
echo 3. 🤖 3D VRM avatar with expressions
echo 4. 🎭 Multi-personality AI system
echo 5. 💬 Natural voice conversation
echo 6. 📊 Conversation history tracking
echo 7. 💾 Export conversation data
echo.
echo Technical Stack:
echo - WebRTC/MediaRecorder API
echo - faster-whisper (speech recognition)
echo - Ollama + llama3.1:8b (local AI)
echo - Three.js + three-vrm (3D avatar)
echo - pyttsx3 (text-to-speech)
echo - Streamlit (UI framework)
echo - FastAPI (API server)
echo - Docker (containerization)
echo.
echo Personality Details:
echo - 親友エンジニア: Friendly, helpful, casual tone
echo - 分身: Empathetic, mirror user's perspective
echo - エキスパート: Professional, detailed, accurate
echo.
echo Note: This system uses Ollama running on your host machine.
echo Make sure Ollama is installed and the llama3.1:8b model is downloaded.

pause
