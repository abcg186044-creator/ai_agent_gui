@echo off
chcp 65001 >nul
title AI Agent System - Quick Start

echo.
echo ========================================
echo 🚀 AI Agent System Quick Start
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

REM クリーンな環境でビルド
echo 🧹 クリーンな環境でビルドします...
docker-compose down >nul 2>&1
docker system prune -f >nul 2>&1

REM イメージのビルド（クリーンなrequirements.txt使用）
echo 🔨 Dockerイメージをビルド中...
docker-compose -f docker-compose.yml -f docker-compose.override.yml build --no-cache
if errorlevel 1 (
    echo ❌ イメージビルドに失敗しました
    echo 💡 以下を確認してください:
    echo    1. Docker Desktopが正常に起動しているか
    echo    2. インターネット接続が正常か
    echo    3. requirements-docker-clean.txt の内容
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
echo 💡 最初の起動には時間がかかる場合があります（モデルダウンロード）
echo.

REM 起動進捗の表示
echo 📊 起動進捗を監視中...
timeout /t 30 /nobreak >nul

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
echo 📋 トラブルシューティング:
echo    起動しない場合: docker-compose logs
echo    再ビルド: docker-compose build --no-cache
echo    完全リセット: docker-compose down -v && docker system prune -a
echo.
echo 💡 自動起動設定:
echo    管理者権限で: python setup_autostart.py
echo.

pause
