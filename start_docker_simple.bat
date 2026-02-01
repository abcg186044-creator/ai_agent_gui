@echo off
chcp 65001 >nul
title AI Agent System - Simple Start

echo.
echo ========================================
echo 🚀 AI Agent System Simple Start
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

REM 改行コードの修正
echo 🔧 Fixing line endings...
python scripts/fix_line_endings.py 2>nul
if errorlevel 1 (
    echo ⚠️ Skipping line endings fix
) else (
    echo ✅ Line endings fixed
)
echo.

REM データディレクトリの作成
echo 💾 Creating data directories...
if not exist "data" mkdir data
if not exist "data\ollama" mkdir data\ollama
if not exist "data\chroma" mkdir data\chroma
if not exist "data\voicevox" mkdir data\voicevox
if not exist "data\redis" mkdir data\redis
echo ✅ Data directories created
echo.

REM 既存コンテナの停止
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.final.yml down >nul 2>&1

REM イメージのビルド
echo 🔨 Building Docker image...
docker-compose -f docker-compose.final.yml build --no-cache
if errorlevel 1 (
    echo ❌ Docker build failed
    echo 💡 Please check Docker Desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Docker image built successfully

REM コンテナの起動
echo 🚀 Starting containers...
docker-compose -f docker-compose.final.yml up -d
if errorlevel 1 (
    echo ❌ Failed to start containers
    echo.
    pause
    exit /b 1
)

echo ✅ Containers started successfully

REM 起動待機
echo ⏳ Waiting for services to start...
timeout /t 60 /nobreak

REM 状態確認
echo.
echo 🔍 Checking service status...
echo ========================================

echo 📊 Container status:
docker-compose -f docker-compose.final.yml ps

echo.
echo 🌐 Access information:
echo    Streamlit: http://localhost:8501
echo    Ollama: http://localhost:11434
echo    VOICEVOX: http://localhost:50021

echo.
echo 🎉 AI Agent System started successfully!
echo.

pause
