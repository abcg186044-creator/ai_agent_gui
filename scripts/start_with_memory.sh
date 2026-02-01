#!/bin/bash
set -e

echo "🧠 AI Agent System with Memory Start"
echo "=================================="

# 環境変数の設定
export CHROMA_DB_PATH=${CHROMA_DB_PATH:-/app/data/chroma}
export MEMORY_ENABLED=${MEMORY_ENABLED:-true}

# 記憶ディレクトリの作成
echo "📁 Creating memory directories..."
mkdir -p "$CHROMA_DB_PATH/memory"
mkdir -p "$CHROMA_DB_PATH/conversations"
mkdir -p "$CHROMA_DB_PATH/settings"
mkdir -p "$CHROMA_DB_PATH/logs"

# 記憶読み込みの実行
if [ "$MEMORY_ENABLED" = "true" ]; then
    echo "🧠 Loading memory..."
    python /app/scripts/memory_loader.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Memory loaded successfully"
    else
        echo "⚠️ Memory loading failed, continuing without memory"
    fi
else
    echo "⚠️ Memory is disabled"
fi

# Streamlitの起動
echo "🚀 Starting Streamlit application..."
exec streamlit run /app/smart_voice_agent_fixed.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
