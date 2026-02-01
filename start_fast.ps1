# AI Agent System Fast Start (PowerShell)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AI Agent System Fast Start" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Docker Desktopの確認
Write-Host "🔄 Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Desktop is not running"
    }
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "💡 Please start Docker Desktop" -ForegroundColor Yellow
    Write-Host "💡 https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press any key to continue"
    exit 1
}

# プロジェクトディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "📁 Project directory: $PWD" -ForegroundColor Blue
Write-Host ""

# データディレクトリの作成
Write-Host "💾 Creating data directories..." -ForegroundColor Yellow
$directories = @("data", "data\chroma", "data\voicevox", "data\redis")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Data directories created" -ForegroundColor Green

# 既存コンテナの停止
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.fast.yml down 2>$null | Out-Null

# イメージのビルド
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
Write-Host "📥 Downloading models (first time only)..." -ForegroundColor Yellow
docker-compose -f docker-compose.fast.yml build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    Write-Host "💡 Please check:" -ForegroundColor Yellow
    Write-Host "   1. Docker Desktop is running" -ForegroundColor White
    Write-Host "   2. Internet connection is working" -ForegroundColor White
    Write-Host "   3. GPU drivers are installed" -ForegroundColor White
    Write-Host ""
    Read-Host "Press any key to continue"
    exit 1
}

Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# コンテナの起動
Write-Host "🚀 Starting containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.fast.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start containers" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press any key to continue"
    exit 1
}

Write-Host "✅ Containers started successfully" -ForegroundColor Green

# 起動待機（短縮）
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 状態確認
Write-Host ""
Write-Host "🔍 Checking service status..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "📊 Container status:" -ForegroundColor Blue
docker-compose -f docker-compose.fast.yml ps

Write-Host ""
Write-Host "🌐 Access information:" -ForegroundColor Blue
Write-Host "   Streamlit: http://localhost:8501" -ForegroundColor White
Write-Host "   Ollama: http://localhost:11434" -ForegroundColor White
Write-Host "   VOICEVOX: http://localhost:50021" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🎉 AI Agent System Fast Start Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Browser access:" -ForegroundColor Blue
Write-Host "   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "📱 Mobile access available" -ForegroundColor Blue
Write-Host ""
Write-Host "💾 Data persistence:" -ForegroundColor Blue
Write-Host "   ChromaDB: ./data/chroma" -ForegroundColor White
Write-Host "   VOICEVOX: ./data/voicevox" -ForegroundColor White
Write-Host "   Redis: ./data/redis" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Features:" -ForegroundColor Blue
Write-Host "   ✅ Models preloaded in image" -ForegroundColor Green
Write-Host "   ✅ No download required" -ForegroundColor Green
Write-Host "   ✅ GPU memory preloaded" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Management commands:" -ForegroundColor Blue
Write-Host "   Logs: docker-compose -f docker-compose.fast.yml logs -f" -ForegroundColor White
Write-Host "   Stop: docker-compose -f docker-compose.fast.yml down" -ForegroundColor White
Write-Host "   Restart: docker-compose -f docker-compose.fast.yml restart" -ForegroundColor White
Write-Host ""

Read-Host "Press any key to continue"
