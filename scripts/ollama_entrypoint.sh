#!/bin/bash

# Ollama Entrypoint Script with Enhanced Health Check
echo "🚀 Ollama Enhanced Entrypoint"
echo "================================"

# 環境変数の設定
export OLLAMA_HOST=${OLLAMA_HOST:-0.0.0.0}
export OLLAMA_PORT=${OLLAMA_PORT:-11434}
export OLLAMA_ORIGINS=${OLLAMA_ORIGINS:-*}

# 起動前の準備
echo "📁 モデルディレクトリを確認..."
mkdir -p /root/.ollama/models
ls -la /root/.ollama/

echo "🔧 Ollama設定:"
echo "   Host: $OLLAMA_HOST"
echo "   Port: $OLLAMA_PORT"
echo "   Origins: $OLLAMA_ORIGINS"

# GPUの確認
echo "🎮 GPUの確認..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
    echo "✅ GPUが利用可能です"
else
    echo "⚠️ GPUが利用できません。CPUモードで実行します"
fi

# Ollamaサーバーをバックグラウンドで起動
echo "🚀 Ollamaサーバーを起動します..."
ollama serve &
OLLAMA_PID=$!

# 起動待機
echo "⏳ Ollamaサーバーの起動を待機中..."
sleep 10

# ヘルスチェックループ
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "🔍 ヘルスチェック ($RETRY_COUNT/$MAX_RETRIES)..."
    
    if curl -f -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollamaサーバーが正常に起動しました"
        
        # 利用可能なモデルを表示
        echo "📋 利用可能なモデル:"
        curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for model in data.get('models', []):
        print(f'   - {model[\"name\"]}')
except:
    print('   モデル情報の取得に失敗しました')
" 2>/dev/null || echo "   モデル情報の取得に失敗しました"
        
        break
    fi
    
    echo "⏳ Ollamaサーバー起動中... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Ollamaサーバーの起動に失敗しました"
    echo "🔍 デバッグ情報:"
    echo "   プロセスID: $OLLAMA_PID"
    echo "   ポート確認:"
    netstat -tlnp | grep :11434 || echo "   ポート11434が使用されていません"
    echo "   ログ:"
    tail -20 /var/log/ollama.log 2>/dev/null || echo "   ログファイルが見つかりません"
    exit 1
fi

# モデルの自動プル（オプション）
if [ "${AUTO_PULL_MODELS:-true}" = "true" ]; then
    echo "📥 必要なモデルの自動プルを開始します..."
    
    # 必要なモデルリスト
    MODELS_TO_PULL=("llama3.2" "llama3.2-vision")
    
    for model in "${MODELS_TO_PULL[@]}"; do
        echo "📥 モデル $model の存在を確認..."
        
        if curl -s http://localhost:11434/api/tags | grep -q "\"name\":\"$model\""; then
            echo "✅ モデル $model は既に存在します"
        else
            echo "📥 モデル $model をダウンロード中..."
            ollama pull "$model" &
            PULL_PID=$!
            
            # プルの進捗を監視
            while kill -0 $PULL_PID 2>/dev/null; do
                echo "⏳ モデル $model ダウンロード中..."
                sleep 10
            done
            
            wait $PULL_PID
            if [ $? -eq 0 ]; then
                echo "✅ モデル $model のダウンロード完了"
            else
                echo "❌ モデル $model のダウンロード失敗"
            fi
        fi
    done
fi

# サーバーの継続実行
echo "🔄 Ollamaサーバーを実行中..."
echo "📊 サーバー情報:"
echo "   アクセスURL: http://localhost:11434"
echo "   APIエンドポイント: http://localhost:11434/api"
echo "   プロセスID: $OLLAMA_PID"
echo ""
echo "🛑 停止するには: Ctrl+C"

# シグナルハンドラ
trap 'echo "🛑 Ollamaサーバーを停止中..."; kill $OLLAMA_PID 2>/dev/null; exit 0' SIGTERM SIGINT

# メインプロセスを待つ
wait $OLLAMA_PID
