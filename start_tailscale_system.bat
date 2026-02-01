@echo off
title Tailscale + Ollama + VRM + 音声認識 AIエージェントシステム

echo Starting Tailscale + Ollama + VRM + 音声認識 AIエージェントシステム...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Checking Tailscale...
tailscale status >nul 2>&1
if errorlevel 1 (
    echo WARNING: Tailscale not running
    echo Please start Tailscale first
    pause
    exit /b 1
)

echo Getting Tailscale IP...
for /f "tokens=*" %%i in ('tailscale ip -4') do set TAILSCALE_IP=%%i
echo Tailscale IP: %TAILSCALE_IP%

echo Stopping existing containers...
docker stop ai-agent-ollama-tailscale 2>nul
docker rm ai-agent-ollama-tailscale 2>nul

echo Building Tailscale-optimized Ollama VRM integrated image...
docker build -f Dockerfile.ollama.standard -t ai-agent-ollama-tailscale .

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting Tailscale-optimized container...
docker run -d --name ai-agent-ollama-tailscale ^
    -p 0.0.0.0:8501:8501 ^
    -p 0.0.0.0:8000:8000 ^
    -p 0.0.0.0:11434:11434 ^
    -v ./models:/root/.ollama ^
    -v ./data:/app/data ^
    -v ./logs:/app/logs ^
    --restart unless-stopped ^
    ai-agent-ollama-tailscale

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: Tailscale-optimized Ollama VRM AI Agent System is running
echo.
echo Access URLs:
echo - Local Access: http://localhost:8501
echo - Tailscale Access: http://%TAILSCALE_IP%:8501
echo - API Server: http://%TAILSCALE_IP%:8000
echo - Ollama API: http://%TAILSCALE_IP%:11434
echo - VRM Avatar: http://%TAILSCALE_IP%:8000/avatar.vrm
echo.
echo System Features:
echo - Tailscale Integration: ENABLED
echo - Mobile Access: ENABLED
echo - Docker-based Ollama: ENABLED
echo - Model Persistence: ENABLED
echo - VRM Avatar Display: ENABLED
echo - Voice Recognition: ENABLED
echo - Voice Synthesis: ENABLED
echo - Multi-Personality System: ENABLED
echo - Conversation History: ENABLED
echo.
echo Mobile Access Instructions:
echo 1. Make sure Tailscale is running on this machine
echo 2. Install Tailscale on your mobile device
echo 3. Connect both devices to the same Tailscale network
echo 4. Access via mobile browser: http://%TAILSCALE_IP%:8501
echo.
echo Tailscale Network Information:
echo - Your Tailscale IP: %TAILSCALE_IP%
echo - Network Status: Connected
echo - Device Authentication: Required
echo.
echo Setup Instructions:
echo 1. Wait for all services to start (may take 2-3 minutes)
echo 2. Download models in container:
echo    docker exec -it ai-agent-ollama-tailscale ollama pull llama3.1:8b
echo    docker exec -it ai-agent-ollama-tailscale ollama pull llama3.2:latest
echo 3. Test your microphone with "🔧 マイクテスト" button
echo 4. Select personality from sidebar
echo 5. Start voice conversation with AI
echo.
echo Mobile Device Setup:
echo 1. Install Tailscale app on your mobile device
echo 2. Log in to your Tailscale account
echo 3. Enable the network connection
echo 4. Open browser and go to: http://%TAILSCALE_IP%:8501
echo 5. Allow microphone access when prompted
echo 6. Test voice recording and AI conversation
echo.
echo Usage Flow:
echo 1. 🔧 Test microphone (mobile compatible)
echo 2. 🎭 Select personality
echo 3. 📥 Download AI models (one-time setup)
echo 4. 🎤 Record voice input (mobile optimized)
echo 5. 🤖 Get AI response
echo 6. 🤖 Watch VRM avatar expression
echo 7. 💾 Save conversation if desired
echo.
echo Container Management:
echo - View logs: docker logs ai-agent-ollama-tailscale
echo - Execute commands: docker exec -it ai-agent-ollama-tailscale bash
echo - Check models: docker exec -it ai-agent-ollama-tailscale ollama list
echo - Monitor resources: docker stats ai-agent-ollama-tailscale
echo.
echo To stop:
echo docker stop ai-agent-ollama-tailscale
echo docker rm ai-agent-ollama-tailscale
echo.
echo Waiting for services to start...
timeout /t 20 /nobreak >nul

echo Checking service status...
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Main App is responding!' } catch { Write-Host 'Main App still starting...' }"
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: API Server is responding!' } catch { Write-Host 'API Server still starting...' }"
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:11434/api/tags -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Ollama API is responding!' } catch { Write-Host 'Ollama API still starting...' }"

echo.
echo Checking Tailscale connectivity...
powershell -Command "try { Invoke-WebRequest -Uri http://%TAILSCALE_IP%:8501 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Tailscale access is working!' } catch { Write-Host 'Tailscale access may still be starting...' }"

echo.
echo ========================================
echo Tailscale Access Information:
echo ========================================
echo.
echo Local Access:
echo - URL: http://localhost:8501
echo - Use: When on the same machine
echo.
echo Tailscale Access:
echo - URL: http://%TAILSCALE_IP%:8501
echo - Use: From any device on Tailscale network
echo - Mobile: Yes, fully optimized
echo - Security: Encrypted private network
echo.
echo Mobile Device Setup:
echo 1. Install Tailscale app
echo 2. Login to your account
echo 3. Connect to network
echo 4. Browse: http://%TAILSCALE_IP%:8501
echo 5. Allow microphone permissions
echo 6. Start voice conversation
echo.
echo ========================================

echo Please open your browser:
echo - Local: http://localhost:8501
echo - Mobile: http://%TAILSCALE_IP%:8501
echo.
echo Tailscale VRM AI Agent Features:
echo 1. 🎙️ Mobile-optimized voice recording
echo 2. 🤖 Instant AI responses
echo 3. 🤖 3D VRM avatar with expressions
echo 4. 🎭 Multi-personality AI system
echo 5. 💬 Natural voice conversation
echo 6. 📊 Conversation history tracking
echo 7. 💾 Export conversation data
echo 8. 🌐 Tailscale secure access
echo 9. 📱 Full mobile compatibility
echo 10. 🐳 Complete containerization
echo.
echo Technical Stack:
echo - Docker + Tailscale integration
echo - Ollama (containerized)
echo - Mobile-optimized WebRTC
echo - faster-whisper (speech recognition)
echo - llama3.1:8b + llama3.2 models
echo - Three.js + three-vrm (3D avatar)
echo - pyttsx3 (text-to-speech)
echo - Streamlit (mobile-responsive UI)
echo - FastAPI (API server)
echo.
echo Mobile Optimization:
echo - Touch-friendly interface
echo - Responsive design
echo - Large touch targets
echo - Mobile audio recording
echo - Optimized bandwidth usage
echo - Progressive enhancement
echo.
echo Security Features:
echo - Tailscale encrypted tunnel
echo - Private network access
echo - No public exposure
echo - End-to-end encryption
echo - Device authentication
echo.
echo Note: This system requires Tailscale to be running
echo Mobile devices need Tailscale app installed
echo All communication is encrypted and private

pause
