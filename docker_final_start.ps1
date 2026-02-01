# AI Agent System Final Start (PowerShell)
param(
    [switch]$SkipLineEndingsFix,
    [switch]$UseSjis
)

# エンコーディング設定
if ($UseSjis) {
    [Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding("shift_jis")
    $OutputEncoding = [System.Text.Encoding]::GetEncoding("shift_jis")
} else {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AI Agent System Final Start" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Docker Desktopが起動しているか確認
Write-Host "🔄 Docker Desktopの状態を確認中..." -ForegroundColor Yellow
try {
    $dockerVersion = docker version 2>$null
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

# プロジェクトディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "📁 プロジェクトディレクトリ: $PWD" -ForegroundColor Blue
Write-Host ""

# 改行コードの修正
if (-not $SkipLineEndingsFix) {
    Write-Host "🔧 改行コードを修正中..." -ForegroundColor Yellow
    try {
        python scripts/fix_line_endings.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 改行コードの修正完了" -ForegroundColor Green
        } else {
            Write-Host "⚠️ 改行コードの修正で警告が発生しました" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ 改行コードの修正をスキップします" -ForegroundColor Yellow
    }
    Write-Host ""
}

# GPUサポートの確認
Write-Host "🎮 GPUサポートを確認中..." -ForegroundColor Yellow
try {
    $gpuTest = docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GPUサポートが利用可能です" -ForegroundColor Green
        $gpuMode = "GPU"
    } else {
        throw "GPUなし"
    }
} catch {
    Write-Host "❌ GPUサポートが利用できません" -ForegroundColor Red
    Write-Host "💡 CPU版を使用します" -ForegroundColor Yellow
    $gpuMode = "CPU"
}
Write-Host ""

# データディレクトリの作成
Write-Host "💾 データディレクトリを作成中..." -ForegroundColor Yellow
$directories = @("data", "data\ollama", "data\chroma", "data\voicevox", "data\redis")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ データディレクトリの作成完了" -ForegroundColor Green
Write-Host ""

# 既存コンテナの停止
Write-Host "🛑 既存のコンテナを停止中..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.final.yml down 2>$null | Out-Null
    Write-Host "✅ 既存コンテナを停止しました" -ForegroundColor Green
} catch {
    Write-Host "⚠️ 既存コンテナの停止で警告が発生しました" -ForegroundColor Yellow
}
Write-Host ""

# イメージのビルド
Write-Host "🔨 Dockerイメージをビルド中..." -ForegroundColor Yellow
try {
    $buildResult = docker-compose -f docker-compose.final.yml build --no-cache
    if ($LASTEXITCODE -ne 0) {
        throw "ビルド失敗"
    }
    Write-Host "✅ イメージビルド完了" -ForegroundColor Green
} catch {
    Write-Host "❌ イメージビルドに失敗しました" -ForegroundColor Red
    Write-Host "💡 以下を確認してください:" -ForegroundColor Yellow
    Write-Host "   1. Docker Desktopが正常に起動しているか" -ForegroundColor White
    Write-Host "   2. インターネット接続が正常か" -ForegroundColor White
    Write-Host "   3. GPUドライバーが正しくインストールされているか" -ForegroundColor White
    Write-Host ""
    Read-Host "続行するには何かキーを押してください"
    exit 1
}
Write-Host ""

# コンテナの起動
Write-Host "🚀 コンテナを起動中..." -ForegroundColor Yellow
try {
    $upResult = docker-compose -f docker-compose.final.yml up -d
    if ($LASTEXITCODE -ne 0) {
        throw "起動失敗"
    }
    Write-Host "✅ コンテナを起動しました" -ForegroundColor Green
} catch {
    Write-Host "❌ コンテナの起動に失敗しました" -ForegroundColor Red
    Write-Host ""
    Read-Host "続行するには何かキーを押してください"
    exit 1
}
Write-Host ""

# 起動待機
Write-Host "⏳ サービス起動を待機中..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Ollamaの状態確認
Write-Host ""
Write-Host "🔍 Ollamaの状態を確認中..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "📊 コンテナ状態:" -ForegroundColor Blue
$psResult = docker-compose -f docker-compose.final.yml ps
Write-Host $psResult

Write-Host ""
Write-Host "📋 Ollamaログ:" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Cyan
$logsResult = docker-compose -f docker-compose.final.yml logs ollama --tail=20
Write-Host $logsResult

Write-Host ""
Write-Host "🔍 Ollamaヘルスチェック:" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Cyan
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Ollama: 正常に起動しています" -ForegroundColor Green
    Write-Host "   アクセス: http://localhost:11434" -ForegroundColor White
    
    Write-Host ""
    Write-Host "📋 利用可能なモデル:" -ForegroundColor Blue
    try {
        $models = $healthCheck.models | ForEach-Object { "   - $($_.name)" }
        Write-Host ($models -join "`n") -ForegroundColor White
    } catch {
        Write-Host "   モデル情報の取得に失敗しました" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ollama: 起動していません" -ForegroundColor Red
    Write-Host "💡 詳細なログを確認:" -ForegroundColor Yellow
    Write-Host "   docker logs ai-ollama" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 デバッグ手順:" -ForegroundColor Yellow
    Write-Host "   1. docker logs ai-ollama --tail=50" -ForegroundColor White
    Write-Host "   2. docker exec -it ai-ollama bash" -ForegroundColor White
    Write-Host "   3. curl -f http://localhost:11434/api/tags" -ForegroundColor White
    Write-Host ""
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

# 他のサービスの確認
Write-Host ""
Write-Host "🔍 他のサービスの状態:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Streamlit
try {
    $streamlitCheck = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Streamlit: 正常に起動しています" -ForegroundColor Green
    Write-Host "   アクセス: http://localhost:8501" -ForegroundColor White
} catch {
    Write-Host "❌ Streamlit: 起動していません" -ForegroundColor Red
    Write-Host "💡 コンテナログを確認: docker-compose -f docker-compose.final.yml logs ai-app" -ForegroundColor Yellow
}

# VOICEVOX
try {
    $voicevoxCheck = Invoke-WebRequest -Uri "http://localhost:50021/docs" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ VOICEVOX: 正常に起動しています" -ForegroundColor Green
    Write-Host "   アクセス: http://localhost:50021" -ForegroundColor White
} catch {
    Write-Host "❌ VOICEVOX: 起動していません" -ForegroundColor Red
    Write-Host "💡 コンテナログを確認: docker-compose -f docker-compose.final.yml logs voicevox" -ForegroundColor Yellow
}

# Redis
try {
    $redisCheck = & redis-cli -h localhost -p 6379 ping 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Redis: 正常に起動しています" -ForegroundColor Green
    } else {
        throw "Redis起動失敗"
    }
} catch {
    Write-Host "❌ Redis: 起動していません" -ForegroundColor Red
    Write-Host "💡 コンテナログを確認: docker-compose -f docker-compose.final.yml logs redis" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🎉 AI Agent System 起動完了！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 ブラウザでアクセス:" -ForegroundColor Blue
Write-Host "   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "📱 モバイルからもアクセス可能" -ForegroundColor Blue
Write-Host ""
Write-Host "💾 データ永続化:" -ForegroundColor Blue
Write-Host "   Ollamaモデル: ./data/ollama" -ForegroundColor White
Write-Host "   ChromaDB: ./data/chroma" -ForegroundColor White
Write-Host "   VOICEVOX: ./data/voicevox" -ForegroundColor White
Write-Host "   Redis: ./data/redis" -ForegroundColor White
Write-Host ""
Write-Host "🔧 管理コマンド:" -ForegroundColor Blue
Write-Host "   ログ確認: docker-compose -f docker-compose.final.yml logs -f" -ForegroundColor White
Write-Host "   停止: docker-compose -f docker-compose.final.yml down" -ForegroundColor White
Write-Host "   再起動: docker-compose -f docker-compose.final.yml restart" -ForegroundColor White
Write-Host ""
Write-Host "🐛 デバッグコマンド:" -ForegroundColor Blue
Write-Host "   Ollamaログ: docker logs ai-ollama --tail=50" -ForegroundColor White
Write-Host "   コンテナ内部: docker exec -it ai-ollama bash" -ForegroundColor White
Write-Host "   ヘルスチェック: curl -f http://localhost:11434/api/tags" -ForegroundColor White
Write-Host ""
Write-Host "📥 モデル管理:" -ForegroundColor Blue
Write-Host "   モデル一覧: curl -s http://localhost:11434/api/tags" -ForegroundColor White
Write-Host "   モデルプル: docker exec -it ai-ollama ollama pull llama3.2" -ForegroundColor White
Write-Host "   モデル削除: docker exec -it ai-ollama ollama rm llama3.2" -ForegroundColor White
Write-Host ""

Read-Host "続行するには何かキーを押してください"
