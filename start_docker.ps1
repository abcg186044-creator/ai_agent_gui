# AI Agent System Docker Start (PowerShell)
# 簡易版PowerShell起動スクリプト

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AI Agent System Docker Start" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# プロジェクトディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "📁 プロジェクトディレクトリ: $PWD" -ForegroundColor Blue
Write-Host ""

# Docker Desktopの確認
Write-Host "🔄 Docker Desktopの状態を確認中..." -ForegroundColor Yellow
try {
    docker version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Desktopが起動していません"
    }
    Write-Host "✅ Docker Desktopが起動しています" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktopが起動していません" -ForegroundColor Red
    Write-Host "💡 Docker Desktopを起動してください" -ForegroundColor Yellow
    Write-Host "💡 https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

# 改行コードの修正
Write-Host "🔧 改行コードを修正中..." -ForegroundColor Yellow
try {
    python scripts/fix_line_endings.py 2>$null | Out-Null
    Write-Host "✅ 改行コードの修正完了" -ForegroundColor Green
} catch {
    Write-Host "⚠️ 改行コードの修正をスキップします" -ForegroundColor Yellow
}

# データディレクトリの作成
Write-Host "💾 データディレクトリを作成中..." -ForegroundColor Yellow
$directories = @("data", "data\ollama", "data\chroma", "data\voicevox", "data\redis")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# コンテナの停止
Write-Host "🛑 既存のコンテナを停止中..." -ForegroundColor Yellow
docker-compose -f docker-compose.final.yml down 2>$null | Out-Null

# イメージのビルド
Write-Host "🔨 Dockerイメージをビルド中..." -ForegroundColor Yellow
docker-compose -f docker-compose.final.yml build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ イメージビルドに失敗しました" -ForegroundColor Red
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

Write-Host "✅ イメージビルド完了" -ForegroundColor Green

# コンテナの起動
Write-Host "🚀 コンテナを起動中..." -ForegroundColor Yellow
docker-compose -f docker-compose.final.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ コンテナの起動に失敗しました" -ForegroundColor Red
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

Write-Host "✅ コンテナを起動しました" -ForegroundColor Green

# 起動待機
Write-Host "⏳ サービス起動を待機中..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# 状態確認
Write-Host ""
Write-Host "🔍 サービス状態を確認中..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "📊 コンテナ状態:" -ForegroundColor Blue
docker-compose -f docker-compose.final.yml ps

Write-Host ""
Write-Host "🌐 アクセス情報:" -ForegroundColor Blue
Write-Host "   Streamlit: http://localhost:8501" -ForegroundColor White
Write-Host "   Ollama: http://localhost:11434" -ForegroundColor White
Write-Host "   VOICEVOX: http://localhost:50021" -ForegroundColor White

Write-Host ""
Write-Host "🎉 AI Agent System 起動完了！" -ForegroundColor Green
Write-Host ""

Read-Host "続行するには何かキーを押してください"
