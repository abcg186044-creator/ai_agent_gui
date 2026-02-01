@echo off
chcp 65001 >nul
title AI Agent System - Debug Start

echo.
echo ========================================
echo 🐛 AI Agent System Debug Start
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

REM Docker情報の表示
echo 📊 Docker情報:
echo ========================================
docker info
echo.

REM Dockerシステムのクリーンアップ
echo 🧹 Dockerシステムのクリーンアップ...
docker system df
docker system prune -f
echo.

REM requirements.txtの内容確認
echo 📋 requirements.txtの内容確認:
echo ========================================
if exist requirements-docker-minimal.txt (
    echo 📄 使用: requirements-docker-minimal.txt
    type requirements-docker-minimal.txt
) else if exist requirements-docker-clean.txt (
    echo 📄 使用: requirements-docker-clean.txt
    type requirements-docker-clean.txt
) else (
    echo 📄 使用: requirements.txt
    type requirements.txt
)
echo.

REM ミニマルなテストビルド
echo 🧪 ミニマルなテストビルドを実行します...
echo FROM python:3.10-slim > Dockerfile.test
echo RUN pip install --upgrade pip >> Dockerfile.test
echo RUN pip install streamlit==1.29.0 requests==2.31.0 >> Dockerfile.test
echo CMD ["echo", "Test build successful"] >> Dockerfile.test

echo 🔨 テストビルド中...
docker build -f Dockerfile.test -t ai-agent-test .
if errorlevel 1 (
    echo ❌ テストビルドに失敗しました
    echo 💡 Docker環境に問題がある可能性があります
    pause
    exit /b 1
)

echo ✅ テストビルド成功
docker rmi ai-agent-test >nul 2>&1
del Dockerfile.test >nul 2>&1

REM 本番ビルド
echo 🔨 本番イメージをビルド中...
copy requirements-docker-minimal.txt requirements-docker.txt >nul 2>&1
docker-compose -f docker-compose.yml -f docker-compose.override.yml build --no-cache
if errorlevel 1 (
    echo ❌ 本番ビルドに失敗しました
    echo 💡 詳細なログを確認してください
    echo.
    echo 🔧 デバッグ情報:
    docker-compose config
    echo.
    pause
    exit /b 1
)

echo ✅ 本番ビルド完了

REM コンテナの起動
echo 🚀 コンテナを起動中...
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

REM 起動待機
echo ⏳ サービス起動を待機中...
timeout /t 60 /nobreak

REM 詳細な状態確認
echo.
echo 🔍 詳細なサービス状態を確認中...
echo ========================================

REM コンテナ一覧
echo 📦 コンテナ一覧:
docker-compose ps
echo.

REM 個別サービスの確認
echo 🤖 Ollama 詳細:
docker-compose logs ollama | tail -10
curl -s http://localhost:11434/api/tags | python3 -m json.tool 2>nul || echo "API接続失敗"
echo.

echo 🌐 Streamlit 詳細:
docker-compose logs ai-app | tail -10
curl -s http://localhost:8501 >nul && echo "Web接続成功" || echo "Web接続失敗"
echo.

echo 🗣️ VOICEVOX 詳細:
docker-compose logs voicevox | tail -10
curl -s http://localhost:50021/docs >nul && echo "API接続成功" || echo "API接続失敗"
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
echo 🔧 デバッグコマンド:
echo    詳細ログ: docker-compose logs -f --tail=100
echo    リアルタイム監視: docker stats
echo    コンテナ内部: docker-compose exec ai-app bash
echo.

pause
