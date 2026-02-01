@echo off
title Docker Complete Ollama + VRM + 音声認識 AIエージェントシステム

echo Starting Docker Complete Ollama + VRM + 音声認識 AIエージェントシステム...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Checking NVIDIA Docker support...
docker run --rm --gpus all nvidia/cuda:12.1-runtime-ubuntu22.04 nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ERROR: NVIDIA Docker support not available
    echo Please install NVIDIA Container Toolkit
    pause
    exit /b 1
)

echo Stopping existing containers...
docker stop ai-agent-ollama-complete 2>nul
docker rm ai-agent-ollama-complete 2>nul

echo Building Complete Ollama VRM integrated image...
echo This will download and pre-load all models during build...
docker build -f Dockerfile.ollama.complete -t ai-agent-ollama-complete .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting Complete Ollama VRM integrated container...
docker run -d --name ai-agent-ollama-complete --gpus all -p 8501:8501 -p 8000:8000 -p 11434:11434 --restart unless-stopped ai-agent-ollama-complete

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Complete Ollama VRM AI Agent System is running
echo.
echo Access URLs:
echo - Main App: http://localhost:8501
echo - API Server: http://localhost:8000
echo - Ollama API: http://localhost:11434
echo - VRM Avatar: http://localhost:8000/avatar.vrm
echo.
echo System Features:
echo - Docker-based Ollama: ENABLED
echo - Pre-loaded Models: ENABLED
echo - GPU Acceleration: ENABLED
echo - VRM Avatar Display: ENABLED
echo - Voice Recognition: ENABLED
echo - Voice Synthesis: ENABLED
echo - Multi-Personality System: ENABLED
echo - Conversation History: ENABLED
echo.
echo Pre-loaded Models:
echo - llama3.1:8b (Main LLM)
echo - llama3.2 (Latest version)
echo - llama3.2-vision (Vision model)
echo.
echo GPU Information:
docker exec ai-agent-ollama-complete nvidia-smi
echo.
echo Model Status:
echo Checking if models are properly loaded...
timeout /t 10 /nobreak >nul
docker exec ai-agent-ollama-complete ollama list
echo.
echo Setup Instructions:
echo 1. Wait for all services to start (may take 2-3 minutes)
echo 2. Open http://localhost:8501 in your browser
echo 3. Test your microphone with the "🔧 マイクテスト" button
echo 4. Select personality from sidebar
echo 5. Start voice conversation with AI
echo.
echo Usage Flow:
echo 1. 🔧 Test microphone
echo 2. 🎭 Select personality
echo 3. 🎤 Record voice input
echo 4. 🤖 Get AI response (instant, no download)
echo 5. 🤖 Watch VRM avatar expression
echo 6. 💾 Save conversation if desired
echo.
echo Advantages of Complete Docker System:
echo - ✅ All models pre-loaded in VRAM
echo - ✅ No download delays during usage
echo - ✅ GPU acceleration enabled
echo - ✅ Complete containerization
echo - ✅ Easy deployment
echo - ✅ Consistent environment
echo.
echo Container Management:
echo - View logs: docker logs ai-agent-ollama-complete
echo - Execute commands: docker exec -it ai-agent-ollama-complete bash
echo - Check GPU: docker exec ai-agent-ollama-complete nvidia-smi
echo - Check models: docker exec ai-agent-ollama-complete ollama list
echo.
echo To stop:
echo docker stop ai-agent-ollama-complete
echo docker rm ai-agent-ollama-complete
echo.
echo Waiting for services to start...
echo This may take 2-3 minutes as models are loading into VRAM...

:wait_loop
timeout /t 15 /nobreak >nul
echo Checking service status...

powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Main App is responding!' } catch { Write-Host 'Main App still starting...' }"
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: API Server is responding!' } catch { Write-Host 'API Server still starting...' }"
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:11434/api/tags -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Ollama API is responding!' } catch { Write-Host 'Ollama API still starting...' }"

echo.
echo Checking model status...
docker exec ai-agent-ollama-complete ollama list 2>nul
if errorlevel 1 (
    echo Models may still be loading...
) else (
    echo Models are loaded and ready!
)

echo.
echo Checking GPU usage...
docker exec ai-agent-ollama-complete nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>nul
if errorlevel 1 (
    echo GPU information not available
) else (
    echo VRAM usage displayed above
)

echo.
echo Please open your browser and go to: http://localhost:8501
echo.
echo Complete Docker Ollama VRM AI Agent Features:
echo 1. 🎙️ High-quality voice recording
echo 2. 🤖 Instant AI responses (no download delays)
echo 3. 🤖 3D VRM avatar with expressions
echo 4. 🎭 Multi-personality AI system
echo 5. 💬 Natural voice conversation
echo 6. 📊 Conversation history tracking
echo 7. 💾 Export conversation data
echo 8. 🚀 GPU-accelerated processing
echo 9. 📦 Pre-loaded models in VRAM
echo 10. 🐳 Complete containerization
echo.
echo Technical Stack:
echo - Docker + NVIDIA Container Toolkit
echo - Ollama (containerized)
echo - CUDA 12.1 Runtime
echo - WebRTC/MediaRecorder API
echo - faster-whisper (speech recognition)
echo - llama3.1:8b + llama3.2 + llama3.2-vision
echo - Three.js + three-vrm (3D avatar)
echo - pyttsx3 (text-to-speech)
echo - Streamlit (UI framework)
echo - FastAPI (API server)
echo.
echo Model Information:
echo - All models are pre-loaded during Docker build
echo - Models remain in VRAM for instant access
echo - No download delays during conversations
echo - GPU acceleration for faster inference
echo.
echo Note: This system requires NVIDIA GPU with sufficient VRAM
echo Recommended: 8GB+ VRAM for llama3.1:8b model

pause
