@echo off
chcp 65001 >nul
title AI Agent System - CPU Start

echo.
echo ========================================
echo 🚀 AI Agent System CPU Start
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

REM 既存コンテナの停止
echo 🛑 既存のコンテナを停止中...
docker-compose -f docker-compose.yml down >nul 2>&1
docker-compose -f docker-compose-gpu.yml down >nul 2>&1

REM ウルトラミニマルrequirements.txtを使用
echo 📋 ウルトラミニマルなrequirements.txtを使用します...
copy requirements-docker-ultra-minimal.txt requirements-docker.txt >nul 2>&1

REM CPU版docker-composeを使用
echo 🖥️ CPU版docker-composeを使用します...
copy docker-compose-gpu.yml docker-compose-cpu.yml >nul 2>&1

REM イメージのビルド
echo 🔨 Dockerイメージをビルド中...
docker-compose -f docker-compose-cpu.yml build --no-cache
if errorlevel 1 (
    echo ❌ イメージビルドに失敗しました
    echo 💡 以下を確認してください:
    echo    1. Docker Desktopが正常に起動しているか
    echo    2. インターネット接続が正常か
    echo    3. requirements-docker-ultra-minimal.txt の内容
    echo.
    pause
    exit /b 1
)

echo ✅ イメージビルド完了

REM コンテナの起動
echo 🚀 コンテナを起動中...
docker-compose -f docker-compose-cpu.yml up -d

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
    echo 💡 コンテナログを確認: docker-compose -f docker-compose-cpu.yml logs ollama
) else (
    echo ✅ Ollama: 正常に起動しています
    echo    アクセス: http://localhost:11434
)

REM Streamlitの確認
echo 🌐 Streamlit:
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose-cpu.yml logs ai-app
) else (
    echo ✅ Streamlit: 正常に起動しています
    echo    アクセス: http://localhost:8501
)

REM VOICEVOXの確認
echo 🗣️ VOICEVOX:
curl -s http://localhost:50021/docs >nul 2>&1
if errorlevel 1 (
    echo ❌ VOICEVOX: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose-cpu.yml logs voicevox
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
echo    ログ確認: docker-compose -f docker-compose-cpu.yml logs -f
echo    停止: docker-compose -f docker-compose-cpu.yml down
echo    再起動: docker-compose -f docker-compose-cpu.yml restart
echo.
echo 💡 CPU版の特徴:
echo    ✅ GPU不要で動作
echo    ✅ 互換性が高い
echo    ⚠️ 処理速度はGPU版より遅い
echo.

pause
