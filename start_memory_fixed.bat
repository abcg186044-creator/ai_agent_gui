@echo off
chcp 932 >nul
title AI Agent System - Memory Start

echo.
echo ========================================
echo 蟻 AI Agent System Memory Start
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

REM 記憶用のNamed Volumesを作成
echo 💾 記憶用ボリュームを作成中...
docker volume create ai_chroma_data 2>nul
docker volume create ai_conversation_history 2>nul
docker volume create ai_user_settings 2>nul
docker volume create ai_logs 2>nul
docker volume create ai_voicevox_data 2>nul
docker volume create ai_redis_data 2>nul
echo ✅ 記憶用ボリュームの作成完了

REM 既存コンテナの停止
echo 🛑 既存のコンテナを停止中...
docker-compose -f docker-compose.memory.yml down >nul 2>&1

REM イメージのビルド
echo 🔨 Dockerイメージをビルド中...
echo 📥 モデルをダウンロード中（初回のみ時間がかかります）...
echo 🧠 記憶機能を有効化中...
docker-compose -f docker-compose.memory.yml build --no-cache
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
docker-compose -f docker-compose.memory.yml up -d

if errorlevel 1 (
    echo ❌ コンテナの起動に失敗しました
    echo.
    pause
    exit /b 1
)

echo ✅ コンテナを起動しました

REM 起動待機
echo ⏳ サービス起動を待機中...
timeout /t 30 /nobreak

REM 状態確認
echo.
echo 🔍 サービス状態を確認中...
echo ========================================

echo 📊 コンテナ状態:
docker-compose -f docker-compose.memory.yml ps

echo.
echo 🌐 アクセス情報:
echo    Streamlit: http://localhost:8501
echo    Ollama: http://localhost:11434
echo    VOICEVOX: http://localhost:50021

echo.
echo ========================================
echo 🧠 AI Agent System 記憶対応版 起動完了！
echo ========================================
echo.
echo 🌐 ブラウザでアクセス:
echo    http://localhost:8501
echo.
echo 📱 モバイルからもアクセス可能
echo.
echo 💾 記憶データ永続化:
echo    ChromaDB: ai_chroma_data (Named Volume)
echo    会話履歴: ai_conversation_history (Named Volume)
echo    ユーザー設定: ai_user_settings (Named Volume)
echo    ログ: ai_logs (Named Volume)
echo    VOICEVOX: ai_voicevox_data (Named Volume)
echo    Redis: ai_redis_data (Named Volume)
echo.
echo 🎯 特徴:
echo    ✅ モデルはイメージ内に組み込み済み
echo    ✅ 記憶は外部ボリュームに永続化
echo    ✅ 脳と経験を分離して管理
echo    ✅ 使えば使うほど進化するAI
echo.
echo 🔧 記憶管理コマンド:
echo    記憶確認: docker volume ls
echo    記憶バックアップ: docker run --rm -v ai_chroma_data:/data -v %%CD%%:/backup alpine tar czf /backup/memory_backup.tar.gz -C /data .
echo    記憶リストア: docker run --rm -v ai_chroma_data:/data -v %%CD%%:/backup alpine tar xzf /backup/memory_backup.tar.gz -C /data
echo.
echo 🔧 管理コマンド:
echo    ログ確認: docker-compose -f docker-compose.memory.yml logs -f
echo    停止: docker-compose -f docker-compose.memory.yml down
echo    再起動: docker-compose -f docker-compose.memory.yml restart
echo.

pause
