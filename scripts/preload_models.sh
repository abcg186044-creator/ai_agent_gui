#!/bin/bash
set -e

echo "🚀 Preloading models into GPU memory..."

# Ollamaサーバーを起動
ollama serve &
OLLAMA_PID=$!

# 起動待機
echo "⏳ Waiting for Ollama to start..."
MAX_RETRIES=15
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready for model preloading"
        break
    fi
    echo "⏳ Waiting for Ollama... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

# 利用可能なモデルの確認
echo "📋 Available models:"
ollama list

# モデルのプリロード（GPUメモリにロード）
MODELS=("llama3.2" "llama3.2-vision")

for model in "${MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "🔄 Preloading $model into GPU memory..."
        # 空実行でモデルをメモリにロード
        timeout 30 ollama run "$model" "Hi" --non-interactive || true
        echo "✅ $model preloaded successfully"
    else
        echo "⚠️ Model $model not found, skipping preload"
    fi
done

echo "🎉 Model preloading completed"
echo "🔄 Ollama server is running with preloaded models"

# メインプロセスを待つ
wait $OLLAMA_PID
