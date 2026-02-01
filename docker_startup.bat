@echo off
chcp 65001 >nul
title AI Agent System - Docker起動

echo.
echo ========================================
echo 🐳 AI Agent System Docker起動
echo ========================================
echo.

REM Docker Desktopが起動しているか確認
echo 🔄 Docker Desktopの状態を確認中...
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktopが起動していません
    echo 💡 Docker Desktopを起動してください
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Desktopが起動しています

REM プロジェクトディレクトリに移動
cd /d "%~dp0"
echo 📁 プロジェクトディレクトリ: %CD%
echo.

REM Dockerネットワークの確認
echo 🌐 Dockerネットワークを確認中...
docker network inspect ai-agent_gui_ai-network >nul 2>&1
if errorlevel 1 (
    echo 🔄 ネットワークを作成します...
    docker network create ai-agent_gui_ai-network --driver bridge --subnet=172.20.0.0/16
)

REM コンテナの停止・削除
echo 🛑 既存のコンテナを停止中...
docker-compose down >nul 2>&1

REM クリーンなrequirements.txtを使用
echo 📋 Docker用のクリーンなrequirements.txtを使用します...
copy requirements-docker-clean.txt requirements-docker.txt >nul 2>&1

REM イメージのビルド
echo 🔨 Dockerイメージをビルド中...
docker-compose -f docker-compose.yml -f docker-compose.override.yml build --no-cache
if errorlevel 1 (
    echo ❌ イメージビルドに失敗しました
    echo 💡 Dockerfileやrequirements.txtを確認してください
    pause
    exit /b 1
)

echo ✅ イメージビルド完了

REM コンテナの起動
echo 🚀 コンテナを起動中...
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

REM 起動待機
echo ⏳ サービス起動を待機中...
timeout /t 60 /nobreak

REM サービスの状態確認
echo.
echo 🔍 サービス状態を確認中...
echo ========================================

REM Ollamaの確認
echo 🤖 Ollama:
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama: 起動していません
) else (
    echo ✅ Ollama: 正常に起動しています
    echo    アクセス: http://localhost:11434
)

REM Streamlitの確認
echo 🌐 Streamlit:
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit: 起動していません
) else (
    echo ✅ Streamlit: 正常に起動しています
    echo    アクセス: http://localhost:8501
)

REM VOICEVOXの確認
echo 🗣️ VOICEVOX:
curl -s http://localhost:50021/docs >nul 2>&1
if errorlevel 1 (
    echo ❌ VOICEVOX: 起動していません
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
echo 💡 PC起動時に自動で起動するには:
echo    1. タスクスケジューラでこのバッチファイルを登録
echo    2. またはDocker Desktopの「Start Docker Desktop when you log in」を有効化
echo.

pause
