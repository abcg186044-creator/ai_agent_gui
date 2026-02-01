@echo off
title Docker Standard Ollama + VRM + 音声認識 AIエージェントシステム

echo Starting Docker Standard Ollama + VRM + 音声認識 AIエージェントシステム...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Stopping existing containers...
docker stop ai-agent-ollama-standard 2>nul
docker rm ai-agent-ollama-standard 2>nul

echo Building Standard Ollama VRM integrated image...
echo This will create a container with Ollama pre-installed...
docker build -f Dockerfile.ollama.standard -t ai-agent-ollama-standard .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting Standard Ollama VRM integrated container...
docker run -d --name ai-agent-ollama-standard -p 8501:8501 -p 8000:8000 -p 11434:11434 --restart unless-stopped ai-agent-ollama-standard

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Standard Ollama VRM AI Agent System is running
echo.
echo Access URLs:
echo - Main App: http://localhost:8501
echo - API Server: http://localhost:8000
echo - Ollama API: http://localhost:11434
echo - VRM Avatar: http://localhost:8000/avatar.vrm
echo.
echo System Features:
echo - Docker-based Ollama: ENABLED
echo - CPU Processing: ENABLED
echo - VRM Avatar Display: ENABLED
echo - Voice Recognition: ENABLED
echo - Voice Synthesis: ENABLED
echo - Multi-Personality System: ENABLED
echo - Conversation History: ENABLED
echo.
echo Setup Instructions:
echo 1. Wait for all services to start (may take 1-2 minutes)
echo 2. Open http://localhost:8501 in your browser
echo 3. Download models in container:
echo    docker exec -it ai-agent-ollama-standard ollama pull llama3.1:8b
echo    docker exec -it ai-agent-ollama-standard ollama pull llama3.2:latest
echo 4. Test your microphone with the "🔧 マイクテスト" button
echo 5. Select personality from sidebar
echo 6. Start voice conversation with AI
echo.
echo Model Management:
echo - Download models: docker exec -it ai-agent-ollama-standard ollama pull [model]
echo - List models: docker exec -it ai-agent-ollama-standard ollama list
echo - Remove models: docker exec -it ai-agent-ollama-standard ollama rm [model]
echo.
echo Usage Flow:
echo 1. 🔧 Test microphone
echo 2. 🎭 Select personality
echo 3. 📥 Download AI models (one-time setup)
echo 4. 🎤 Record voice input
echo 5. 🤖 Get AI response
echo 6. 🤖 Watch VRM avatar expression
echo 7. 💾 Save conversation if desired
echo.
echo Container Management:
echo - View logs: docker logs ai-agent-ollama-standard
echo - Execute commands: docker exec -it ai-agent-ollama-standard bash
echo - Check models: docker exec -it ai-agent-ollama-standard ollama list
echo.
echo To stop:
echo docker stop ai-agent-ollama-standard
echo docker rm ai-agent-ollama-standard
echo.
echo Waiting for services to start...
timeout /t 15 /nobreak >nul

echo Checking service status...
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Main App is responding!' } catch { Write-Host 'Main App still starting...' }"
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: API Server is responding!' } catch { Write-Host 'API Server still starting...' }"
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:11434/api/tags -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Ollama API is responding!' } catch { Write-Host 'Ollama API still starting...' }"

echo.
echo Please open your browser and go to: http://localhost:8501
echo.
echo Standard Docker Ollama VRM AI Agent Features:
echo 1. 🎙️ High-quality voice recording
echo 2. 🤖 AI responses (models need to be downloaded)
echo 3. 🤖 3D VRM avatar with expressions
echo 4. 🎭 Multi-personality AI system
echo 5. 💬 Natural voice conversation
echo 6. 📊 Conversation history tracking
echo 7. 💾 Export conversation data
echo 8. 🐳 Complete containerization
echo 9. 💾 Persistent model storage
echo 10. 🔄 Easy model management
echo.
echo Technical Stack:
echo - Docker (containerization)
echo - Ollama (containerized)
echo - Ubuntu 22.04 (base OS)
echo - WebRTC/MediaRecorder API
echo - faster-whisper (speech recognition)
echo - llama3.1:8b + llama3.2 models
echo - Three.js + three-vrm (3D avatar)
echo - pyttsx3 (text-to-speech)
echo - Streamlit (UI framework)
echo - FastAPI (API server)
echo.
echo Model Information:
echo - Models are downloaded per-container
echo - Models persist across container restarts
echo - CPU-based processing (no GPU required)
echo - Models can be managed via docker exec commands
echo.
echo First-time Setup:
echo 1. After container starts, download models:
echo    docker exec -it ai-agent-ollama-standard ollama pull llama3.1:8b
echo 2. Verify models are loaded:
echo    docker exec -it ai-agent-ollama-standard ollama list
echo 3. Start using the AI system
echo.
echo Note: This system uses CPU for AI processing.
echo For GPU acceleration, use the GPU version if available.

pause
