@echo off
chcp 932 >nul
title AI Agent System - Memory Ultimate Fix

echo.
echo ========================================
echo 蟻 AI Agent System Memory Ultimate Fix
echo ========================================
echo.

REM Docker Desktopが起動しているか確認
echo 🔄 Checking Docker Desktop...
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop is not running
    echo 💡 Please start Docker Desktop
    echo 💡 https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Desktop is running

REM プロジェクトディレクトリに移動
cd /d "%~dp0"
echo 📁 Project directory: %CD%
echo.

REM 既存のコンテナとイメージをクリーンアップ
echo 🧹 Cleaning up existing containers and images...
docker-compose -f docker-compose.memory.yml down >nul 2>&1
docker-compose -f docker-compose.memory.fixed.yml down >nul 2>&1
docker system prune -f >nul 2>&1

REM 記憶用のNamed Volumesを作成
echo 💾 Creating memory volumes...
docker volume create ai_chroma_data 2>nul
docker volume create ai_conversation_history 2>nul
docker volume create ai_user_settings 2>nul
docker volume create ai_logs 2>nul
docker volume create ai_voicevox_data 2>nul
docker volume create ai_redis_data 2>nul
echo ✅ Memory volumes created

REM イメージのビルド
echo 🔨 Building Docker image...
echo 📥 Downloading models (first time only)...
echo 🧠 Enabling memory features...
docker-compose -f docker-compose.memory.fixed.yml build --no-cache --parallel
if errorlevel 1 (
    echo ❌ Image build failed
    echo 💡 Please check:
    echo    1. Docker Desktop is running properly
    echo    2. Internet connection is working
    echo    3. GPU drivers are installed correctly
    echo    4. Disk space is sufficient
    echo.
    echo 🔧 Troubleshooting:
    echo    - Try: docker system prune -a
    echo    - Try: docker builder prune -a
    echo    - Restart Docker Desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Image build completed

REM コンテナの起動
echo 🚀 Starting containers...
docker-compose -f docker-compose.memory.fixed.yml up -d

if errorlevel 1 (
    echo ❌ Failed to start containers
    echo.
    pause
    exit /b 1
)

echo ✅ Containers started successfully

REM 起動待機
echo ⏳ Waiting for services to start...
timeout /t 45 /nobreak

REM 状態確認
echo.
echo 🔍 Checking service status...
echo ========================================

echo 📊 Container status:
docker-compose -f docker-compose.memory.fixed.yml ps

echo.
echo 🌐 Access information:
echo    Streamlit: http://localhost:8501
echo    Ollama: http://localhost:11434
echo    VOICEVOX: http://localhost:50021

echo.
echo ========================================
echo 🧠 AI Agent System Memory Ultimate Complete!
echo ========================================
echo.
echo 🌐 Browser access:
echo    http://localhost:8501
echo.
echo 📱 Mobile access available
echo.
echo 💾 Memory persistence:
echo    ChromaDB: ai_chroma_data (Named Volume)
echo    Conversation history: ai_conversation_history (Named Volume)
echo    User settings: ai_user_settings (Named Volume)
echo    Logs: ai_logs (Named Volume)
echo    VOICEVOX: ai_voicevox_data (Named Volume)
echo    Redis: ai_redis_data (Named Volume)
echo.
echo 🎯 Features:
echo    ✅ Models preloaded in image
echo    ✅ Memory persisted in external volumes
echo    ✅ Brain and experience separated
echo    ✅ AI that evolves with use
echo.
echo 🔧 Memory management:
echo    Check memory: docker volume ls
echo    Backup memory: docker run --rm -v ai_chroma_data:/data -v %%CD%%:/backup alpine tar czf /backup/memory_backup.tar.gz -C /data .
echo    Restore memory: docker run --rm -v ai_chroma_data:/data -v %%CD%%:/backup alpine tar xzf /backup/memory_backup.tar.gz -C /data
echo.
echo 🔧 Management commands:
echo    View logs: docker-compose -f docker-compose.memory.fixed.yml logs -f
echo    Stop: docker-compose -f docker-compose.memory.fixed.yml down
echo    Restart: docker-compose -f docker-compose.memory.fixed.yml restart
echo.
echo 🔧 Troubleshooting:
echo    Clean system: docker system prune -a
echo    Clean builder: docker builder prune -a
echo    Check disk: docker system df
echo.

pause
