@echo off
chcp 65001 >nul
title AI Agent System - Production Start

echo.
echo ========================================
echo 🚀 AI Agent System Production Start
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

REM データディレクトリの作成
echo 💾 データディレクトリを作成中...
if not exist "data" mkdir data
if not exist "data\ollama" mkdir data\ollama
if not exist "data\chroma" mkdir data\chroma
if not exist "data\voicevox" mkdir data\voicevox
if not exist "data\redis" mkdir data\redis
if not exist "data\models" mkdir data\models

REM 既存コンテナの停止
echo 🛑 既存のコンテナを停止中...
docker-compose -f docker-compose.production.yml down >nul 2>&1

REM イメージのビルド
echo 🔨 最適化されたDockerイメージをビルド中...
docker-compose -f docker-compose.production.yml build --no-cache
if errorlevel 1 (
    echo ❌ イメージビルドに失敗しました
    echo 💡 以下を確認してください:
    echo    1. Docker Desktopが正常に起動しているか
    echo    2. インターネット接続が正常か
    echo    3. Dockerfile.production の内容
    echo.
    pause
    exit /b 1
)

echo ✅ イメージビルド完了

REM コンテナの起動
echo 🚀 コンテナを起動中...
docker-compose -f docker-compose.production.yml up -d

REM 起動待機
echo ⏳ サービス起動を待機中...
echo 💡 初回起動時はモデルのダウンロードに時間がかかります
timeout /t 120 /nobreak

REM サービスの状態確認
echo.
echo 🔍 サービス状態を確認中...
echo ========================================

REM Ollamaの確認
echo 🤖 Ollama:
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose.production.yml logs ollama
) else (
    echo ✅ Ollama: 正常に起動しています
    echo    アクセス: http://localhost:11434
    echo    データ保存先: ./data/ollama
)

REM Streamlitの確認
echo 🌐 Streamlit:
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose.production.yml logs ai-app
) else (
    echo ✅ Streamlit: 正常に起動しています
    echo    アクセス: http://localhost:8501
)

REM VOICEVOXの確認
echo 🗣️ VOICEVOX:
curl -s http://localhost:50021/docs >nul 2>&1
if errorlevel 1 (
    echo ❌ VOICEVOX: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose.production.yml logs voicevox
) else (
    echo ✅ VOICEVOX: 正常に起動しています
    echo    アクセス: http://localhost:50021
)

REM Redisの確認
echo 💾 Redis:
redis-cli -h localhost -p 6379 ping >nul 2>&1
if errorlevel 1 (
    echo ❌ Redis: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose.production.yml logs redis
) else (
    echo ✅ Redis: 正常に起動しています
    echo    データ保存先: ./data/redis
)

echo.
echo ========================================
echo 🎉 AI Agent System Production 起動完了！
echo ========================================
echo.
echo 🌐 ブラウザでアクセス:
echo    http://localhost:8501
echo.
echo 📱 モバイルからもアクセス可能
echo.
echo 💾 データ永続化:
echo    Ollamaモデル: ./data/ollama
echo    ChromaDB: ./data/chroma
echo    VOICEVOX: ./data/voicevox
echo    Redis: ./data/redis
echo.
echo 🔧 管理コマンド:
echo    ログ確認: docker-compose -f docker-compose.production.yml logs -f
echo    停止: docker-compose -f docker-compose.production.yml down
echo    再起動: docker-compose -f docker-compose.production.yml restart
echo.
echo 🎯 特徴:
echo    ✅ マルチステージビルド: 軽量イメージ
echo    ✅ データ永続化: 再起動時もデータ保持
echo    ✅ モデルプリロード: 即座に利用可能
echo    ✅ 自動最適化: キャッシュ機能付き
echo.
echo 💡 次回以降の起動は高速です:
echo    モデルが永続化されているため、ダウンロード不要
echo.

pause
