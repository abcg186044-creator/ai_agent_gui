#!/bin/bash
set -e

echo "🚀 Starting Ollama for model download..."
ollama serve &
OLLAMA_PID=$!

# Ollamaが起動するのを待つ
echo "⏳ Waiting for Ollama to start..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready for model download"
        break
    fi
    echo "⏳ Waiting for Ollama... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Ollama failed to start for model download"
    exit 1
fi

# モデルのダウンロード
echo "📥 Downloading models..."
MODELS=("llama3.2" "llama3.2-vision")

for model in "${MODELS[@]}"; do
    echo "📥 Downloading $model..."
    ollama pull "$model"
    echo "✅ $model downloaded successfully"
done

echo "🎉 All models downloaded successfully"

# Ollamaを停止
echo "🛑 Stopping Ollama..."
kill $OLLAMA_PID
wait $OLLAMA_PID 2>/dev/null || true

echo "✅ Model download completed"
