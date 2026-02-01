# AI Agent System Docker Start (Simple PowerShell)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AI Agent System Docker Start" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Docker Desktopの確認
Write-Host "🔄 Checking Docker Desktop..." -ForegroundColor Yellow
docker version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "💡 Please start Docker Desktop" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press any key to continue"
    exit 1
}
Write-Host "✅ Docker Desktop is running" -ForegroundColor Green

# プロジェクトディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "📁 Project directory: $PWD" -ForegroundColor Blue
Write-Host ""

# 改行コードの修正
Write-Host "🔧 Fixing line endings..." -ForegroundColor Yellow
try {
    python scripts/fix_line_endings.py 2>$null | Out-Null
    Write-Host "✅ Line endings fixed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Skipping line endings fix" -ForegroundColor Yellow
}
Write-Host ""

# データディレクトリの作成
Write-Host "💾 Creating data directories..." -ForegroundColor Yellow
$directories = @("data", "data\ollama", "data\chroma", "data\voicevox", "data\redis")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Data directories created" -ForegroundColor Green
Write-Host ""

# 既存コンテナの停止
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.final.yml down 2>$null | Out-Null

# イメージのビルド
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker-compose -f docker-compose.final.yml build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    Write-Host "💡 Please check Docker Desktop" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press any key to continue"
    exit 1
}

Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# コンテナの起動
Write-Host "🚀 Starting containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.final.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start containers" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press any key to continue"
    exit 1
}

Write-Host "✅ Containers started successfully" -ForegroundColor Green

# 起動待機
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# 状態確認
Write-Host ""
Write-Host "🔍 Checking service status..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "📊 Container status:" -ForegroundColor Blue
docker-compose -f docker-compose.final.yml ps

Write-Host ""
Write-Host "🌐 Access information:" -ForegroundColor Blue
Write-Host "   Streamlit: http://localhost:8501" -ForegroundColor White
Write-Host "   Ollama: http://localhost:11434" -ForegroundColor White
Write-Host "   VOICEVOX: http://localhost:50021" -ForegroundColor White

Write-Host ""
Write-Host "🎉 AI Agent System started successfully!" -ForegroundColor Green
Write-Host ""

Read-Host "Press any key to continue"
