@echo off
chcp 437 >nul
title AI Agent System - Dynamic Self Contained

echo.
echo ========================================
echo AI Agent System Dynamic Self Contained
echo ========================================
echo.

REM Check if Docker Desktop is running
echo Checking Docker Desktop...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Desktop is not running
    echo Please start Docker Desktop
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Docker Desktop is running

REM Change to project directory
cd /d "%~dp0"
echo Project directory: %CD%
echo.

REM Clean up existing containers and images
echo Cleaning up existing containers and images...
docker-compose -f docker-compose.memory.yml down >nul 2>&1
docker-compose -f docker-compose.memory.fixed.yml down >nul 2>&1
docker-compose -f docker-compose.dynamic.yml down >nul 2>&1
docker system prune -f >nul 2>&1

REM Create memory and library volumes
echo Creating memory and library volumes...
docker volume create ai_chroma_data 2>nul
docker volume create ai_conversation_history 2>nul
docker volume create ai_user_settings 2>nul
docker volume create ai_logs 2>nul
docker volume create ai_voicevox_data 2>nul
docker volume create ai_redis_data 2>nul
docker volume create python_libs 2>nul
docker volume create python_cache 2>nul
echo SUCCESS: Volumes created

REM Build Docker image
echo Building Docker image...
echo Downloading models (first time only)...
echo Enabling memory features...
echo Enabling dynamic package installation...
docker-compose -f docker-compose.dynamic.yml build --no-cache --parallel
if errorlevel 1 (
    echo ERROR: Image build failed
    echo Please check:
    echo    1. Docker Desktop is running properly
    echo    2. Internet connection is working
    echo    3. GPU drivers are installed correctly
    echo    4. Disk space is sufficient
    echo.
    echo Troubleshooting:
    echo    - Try: docker system prune -a
    echo    - Try: docker builder prune -a
    echo    - Restart Docker Desktop
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Image build completed

REM Start containers
echo Starting containers...
docker-compose -f docker-compose.dynamic.yml up -d

if errorlevel 1 (
    echo ERROR: Failed to start containers
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Containers started successfully

REM Wait for services to start
echo Waiting for services to start...
timeout /t 45 /nobreak

REM Check service status
echo.
echo Checking service status...
echo ========================================

echo Container status:
docker-compose -f docker-compose.dynamic.yml ps

echo.
echo Access information:
echo    Streamlit: http://localhost:8501
echo    Ollama: http://localhost:11434
echo    VOICEVOX: http://localhost:50021

echo.
echo ========================================
echo AI Agent System Dynamic Self Contained Complete!
echo ========================================
echo.
echo Browser access:
echo    http://localhost:8501
echo.
echo Mobile access available
echo.
echo Data persistence:
echo    ChromaDB: ai_chroma_data (Named Volume)
echo    Conversation history: ai_conversation_history (Named Volume)
echo    User settings: ai_user_settings (Named Volume)
echo    Logs: ai_logs (Named Volume)
echo    VOICEVOX: ai_voicevox_data (Named Volume)
echo    Redis: ai_redis_data (Named Volume)
echo.
echo Library persistence:
echo    Python libraries: python_libs (Named Volume)
echo    Pip cache: python_cache (Named Volume)
echo.
echo Features:
echo    [OK] Models preloaded in image
echo    [OK] Memory persisted in external volumes
echo    [OK] Libraries dynamically installed and persisted
echo    [OK] Self-healing and auto-installation
echo    [OK] Brain, experience, and tools separated
echo    [OK] AI that grows and adapts autonomously
echo.
echo Dynamic capabilities:
echo    [AI] Detects missing packages automatically
echo    [INSTALL] Installs libraries without user intervention
echo    [RETRY] Retries code execution after installation
echo    [PERSIST] Persists libraries across container restarts
echo    [NOTIFY] Notifies user of installation status
echo.
echo Management commands:
echo    View logs: docker-compose -f docker-compose.dynamic.yml logs -f
echo    Stop: docker-compose -f docker-compose.dynamic.yml down
echo    Restart: docker-compose -f docker-compose.dynamic.yml restart
echo.
echo Library management:
echo    Check installed: docker exec ai-agent-app pip list
echo    Install manually: docker exec ai-agent-app pip install package_name
echo    Check volumes: docker volume ls | grep python
echo.
echo Troubleshooting:
echo    Clean system: docker system prune -a
echo    Clean builder: docker builder prune -a
echo    Check disk: docker system df
echo.

pause
