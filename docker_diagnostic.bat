@echo off
chcp 65001 >nul
title AI Agent System - Diagnostic

echo.
echo ========================================
echo 🩺 AI Agent System Diagnostic
echo ========================================
echo.

REM Docker Desktopの状態確認
echo 🔄 Docker Desktopの状態を確認中...
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktopが起動していません
    echo 💡 Docker Desktopを起動してください
    echo 💡 https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Desktopが起動しています

REM Docker情報の表示
echo.
echo 📊 Dockerシステム情報:
echo ========================================
docker info
echo.

REM 既存コンテナの状態確認
echo 📦 既存コンテナの状態:
echo ========================================
docker ps -a
echo.

REM 既存イメージの確認
echo 🖼️ 既存イメージ:
echo ========================================
docker images
echo.

REM 既存ボリュームの確認
echo 💾 既存ボリューム:
echo ========================================
docker volume ls
echo.

REM 既存ネットワークの確認
echo 🌐 既存ネットワーク:
echo ========================================
docker network ls
echo.

REM GPUサポートの確認
echo 🎮 GPUサポートの確認:
echo ========================================
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ❌ GPUサポートが利用できません
    echo 💡 CPU版を使用してください: docker_cpu_start.bat
) else (
    echo ✅ GPUサポートが利用可能です
    echo 💡 GPU版を使用してください: docker_ultra_minimal_start.bat
)
echo.

REM プロジェクトディレクトリに移動
cd /d "%~dp0"
echo 📁 プロジェクトディレクトリ: %CD%
echo.

REM ファイルの存在確認
echo 📋 ファイルの存在確認:
echo ========================================
if exist docker-compose.yml (
    echo ✅ docker-compose.yml: 存在します
) else (
    echo ❌ docker-compose.yml: 存在しません
)

if exist docker-compose-gpu.yml (
    echo ✅ docker-compose-gpu.yml: 存在します
) else (
    echo ❌ docker-compose-gpu.yml: 存在しません
)

if exist requirements-docker-ultra-minimal.txt (
    echo ✅ requirements-docker-ultra-minimal.txt: 存在します
) else (
    echo ❌ requirements-docker-ultra-minimal.txt: 存在しません
)

if exist Dockerfile (
    echo ✅ Dockerfile: 存在します
) else (
    echo ❌ Dockerfile: 存在しません
)
echo.

REM ネットワークポートの確認
echo 🔌 ネットワークポートの確認:
echo ========================================
netstat -an | findstr ":11434"
netstat -an | findstr ":8501"
netstat -an | findstr ":50021"
netstat -an | findstr ":6379"
echo.

REM 推奨起動方法の表示
echo 💡 推奨起動方法:
echo ========================================
echo.
echo 🎮 GPUが利用可能な場合:
echo    docker_ultra_minimal_start.bat
echo.
echo 🖥️ GPUが利用できない場合:
echo    docker_cpu_start.bat
echo.
echo 🐛 問題が発生した場合:
echo    docker_diagnostic.bat
echo.

pause
