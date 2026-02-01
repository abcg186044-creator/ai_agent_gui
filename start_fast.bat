@echo off
chcp 932 >nul
title AI Agent System - Fast Start

echo.
echo ========================================
echo 蟻 AI Agent System Fast Start
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
if not exist "data\chroma" mkdir data\chroma
if not exist "data\voicevox" mkdir data\voicevox
if not exist "data\redis" mkdir data\redis
echo ✅ データディレクトリの作成完了

REM 既存コンテナの停止
echo 🛑 既存のコンテナを停止中...
docker-compose -f docker-compose.fast.yml down >nul 2>&1

REM イメージのビルド
echo 🔨 Dockerイメージをビルド中...
echo 📥 モデルをダウンロード中（初回のみ時間がかかります）...
docker-compose -f docker-compose.fast.yml build --no-cache
if errorlevel 1 (
    echo ❌ イメージビルドに失敗しました
    echo 💡 以下を確認してください:
    echo    1. Docker Desktopが正常に起動しているか
    echo    2. インターネット接続が正常か
    echo    3. GPUドライバーが正しくインストールされているか
    echo.
    pause
    exit /b 1
)

echo ✅ イメージビルド完了

REM コンテナの起動
echo 🚀 コンテナを起動中...
docker-compose -f docker-compose.fast.yml up -d

if errorlevel 1 (
    echo ❌ コンテナの起動に失敗しました
    echo.
    pause
    exit /b 1
)

echo ✅ コンテナを起動しました

REM 起動待機（短縮）
echo ⏳ サービス起動を待機中...
timeout /t 30 /nobreak

REM 状態確認
echo.
echo 🔍 サービス状態を確認中...
echo ========================================

echo 📊 コンテナ状態:
docker-compose -f docker-compose.fast.yml ps

echo.
echo 🌐 アクセス情報:
echo    Streamlit: http://localhost:8501
echo    Ollama: http://localhost:11434
echo    VOICEVOX: http://localhost:50021

echo.
echo ========================================
echo 🎉 AI Agent System 高速起動完了！
echo ========================================
echo.
echo 🌐 ブラウザでアクセス:
echo    http://localhost:8501
echo.
echo 📱 モバイルからもアクセス可能
echo.
echo 💾 データ永続化:
echo    ChromaDB: ./data/chroma
echo    VOICEVOX: ./data/voicevox
echo    Redis: ./data/redis
echo.
echo 🎯 特徴:
echo    ✅ モデルはイメージ内に組み込み済み
echo    ✅ ダウンロード不要で即座に応答
echo    ✅ GPUメモリにプリロード済み
echo.
echo 🔧 管理コマンド:
echo    ログ確認: docker-compose -f docker-compose.fast.yml logs -f
echo    停止: docker-compose -f docker-compose.fast.yml down
echo    再起動: docker-compose -f docker-compose.fast.yml restart
echo.

pause
