@echo off
chcp 65001 >nul
title AI Agent System - Minimal Start

echo.
echo ========================================
echo 🚀 AI Agent System Minimal Start
echo ========================================
echo.

REM Docker Desktopが起動しているか確認
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

REM プロジェクトディレクトリに移動
cd /d "%~dp0"
echo 📁 プロジェクトディレクトリ: %CD%
echo.

REM クリーンアップ
echo 🧹 クリーンアップ中...
docker-compose down >nul 2>&1
docker system prune -f >nul 2>&1

REM ミニマルrequirements.txtを使用
echo 📋 ミニマルなrequirements.txtを使用します...
copy requirements-docker-minimal.txt requirements-docker.txt >nul 2>&1

REM イメージのビルド
echo 🔨 Dockerイメージをビルド中...
docker-compose -f docker-compose.yml -f docker-compose.override.yml build --no-cache
if errorlevel 1 (
    echo ❌ イメージビルドに失敗しました
    echo 💡 以下を確認してください:
    echo    1. Docker Desktopが正常に起動しているか
    echo    2. インターネット接続が正常か
    echo    3. requirements-docker-minimal.txt の内容
    echo.
    pause
    exit /b 1
)

echo ✅ イメージビルド完了

REM コンテナの起動
echo 🚀 コンテナを起動中...
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

REM 起動待機
echo ⏳ サービス起動を待機中...
timeout /t 30 /nobreak

REM サービスの状態確認
echo.
echo 🔍 サービス状態を確認中...
echo ========================================

REM Ollamaの確認
echo 🤖 Ollama:
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama: 起動していません
    echo 💡 コンテナログを確認: docker-compose logs ollama
) else (
    echo ✅ Ollama: 正常に起動しています
    echo    アクセス: http://localhost:11434
)

REM Streamlitの確認
echo 🌐 Streamlit:
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit: 起動していません
    echo 💡 コンテナログを確認: docker-compose logs ai-app
) else (
    echo ✅ Streamlit: 正常に起動しています
    echo    アクセス: http://localhost:8501
)

REM VOICEVOXの確認
echo 🗣️ VOICEVOX:
curl -s http://localhost:50021/docs >nul 2>&1
if errorlevel 1 (
    echo ❌ VOICEVOX: 起動していません
    echo 💡 コンテナログを確認: docker-compose logs voicevox
) else (
    echo ✅ VOICEVOX: 正常に起動しています
    echo    アクセス: http://localhost:50021
)

echo.
echo ========================================
echo 🎉 AI Agent System 起動完了！
echo ========================================
echo.
echo 🌐 ブラウザでアクセス:
echo    http://localhost:8501
echo.
echo 📱 モバイルからもアクセス可能
echo.
echo 🔧 管理コマンド:
echo    ログ確認: docker-compose logs -f
echo    停止: docker-compose down
echo    再起動: docker-compose restart
echo.
echo 💡 追加ライブラリが必要な場合:
echo    requirements-docker-clean.txt を使用して再ビルド
echo.

pause
