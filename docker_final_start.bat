@echo off
chcp 65001 >nul
title AI Agent System - Final Start

echo.
echo ========================================
echo 🚀 AI Agent System Final Start
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

REM GPUサポートの確認
echo 🎮 GPUサポートを確認中...
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ❌ GPUサポートが利用できません
    echo 💡 CPU版を使用します
    set COMPOSE_FILE=docker-compose.final.yml
    set GPU_MODE=CPU
) else (
    echo ✅ GPUサポートが利用可能です
    set COMPOSE_FILE=docker-compose.final.yml
    set GPU_MODE=GPU
)

REM データディレクトリの作成
echo 💾 データディレクトリを作成中...
if not exist "data" mkdir data
if not exist "data\ollama" mkdir data\ollama
if not exist "data\chroma" mkdir data\chroma
if not exist "data\voicevox" mkdir data\voicevox
if not exist "data\redis" mkdir data\redis

REM 既存コンテナの停止
echo 🛑 既存のコンテナを停止中...
docker-compose -f docker-compose.final.yml down >nul 2>&1

REM イメージのビルド
echo 🔨 Dockerイメージをビルド中...
docker-compose -f docker-compose.final.yml build --no-cache
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
docker-compose -f docker-compose.final.yml up -d

REM 起動待機
echo ⏳ サービス起動を待機中...
timeout /t 60 /nobreak

REM Ollamaの状態確認
echo.
echo 🔍 Ollamaの状態を確認中...
echo ========================================

echo 📊 コンテナ状態:
docker-compose -f docker-compose.final.yml ps

echo.
echo 📋 Ollamaログ:
echo ========================================
docker-compose -f docker-compose.final.yml logs ollama --tail=20

echo.
echo 🔍 Ollamaヘルスチェック:
echo ========================================
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama: 起動していません
    echo 💡 詳細なログを確認:
    echo    docker logs ai-ollama
    echo.
    echo 💡 デバッグ手順:
    echo    1. docker logs ai-ollama --tail=50
    echo    2. docker exec -it ai-ollama bash
    echo    3. curl -f http://localhost:11434/api/tags
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Ollama: 正常に起動しています
    echo    アクセス: http://localhost:11434
    
    echo 📋 利用可能なモデル:
    curl -s http://localhost:11434/api/tags | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for model in data.get('models', []):
        print(f'   - {model[\"name\"]}')
except:
    print('   モデル情報の取得に失敗しました')
" 2>nul || echo "   モデル情報の取得に失敗しました"
)

REM 他のサービスの確認
echo.
echo 🔍 他のサービスの状態:
echo ========================================

REM Streamlit
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose.final.yml logs ai-app
) else (
    echo ✅ Streamlit: 正常に起動しています
    echo    アクセス: http://localhost:8501
)

REM VOICEVOX
curl -s http://localhost:50021/docs >nul 2>&1
if errorlevel 1 (
    echo ❌ VOICEVOX: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose.final.yml logs voicevox
) else (
    echo ✅ VOICEVOX: 正常に起動しています
    echo    アクセス: http://localhost:50021
)

REM Redis
redis-cli -h localhost -p 6379 ping >nul 2>&1
if errorlevel 1 (
    echo ❌ Redis: 起動していません
    echo 💡 コンテナログを確認: docker-compose -f docker-compose.final.yml logs redis
) else (
    echo ✅ Redis: 正常に起動しています
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
echo 💾 データ永続化:
echo    Ollamaモデル: ./data/ollama
echo    ChromaDB: ./data/chroma
echo    VOICEVOX: ./data/voicevox
echo    Redis: ./data/redis
echo.
echo 🔧 管理コマンド:
echo    ログ確認: docker-compose -f docker-compose.final.yml logs -f
echo    停止: docker-compose -f docker-compose.final.yml down
echo    再起動: docker-compose -f docker-compose.final.yml restart
echo.
echo 🐛 デバッグコマンド:
echo    Ollamaログ: docker logs ai-ollama --tail=50
echo    コンテナ内部: docker exec -it ai-ollama bash
echo    ヘルスチェック: curl -f http://localhost:11434/api/tags
echo.
echo 📥 モデル管理:
echo    モデル一覧: curl -s http://localhost:11434/api/tags
echo    モデルプル: docker exec -it ai-ollama ollama pull llama3.2
echo    モデル削除: docker exec -it ai-ollama ollama rm llama3.2
echo.

pause
