#!/bin/bash

# AI Agent System サービス起動スクリプト

echo "🚀 AI Agent System サービス起動"
echo "=================================="

# 環境変数の設定
export PYTHONPATH=/app
export OLLAMA_HOST=${OLLAMA_HOST:-http://ollama:11434}
export VOICEVOX_HOST=${VOICEVOX_HOST:-http://voicevox:50021}
export REDIS_HOST=${REDIS_HOST:-redis}

# ログディレクトリの作成
mkdir -p /app/logs

# VRMモデルのセットアップ
echo "🎭 VRMモデルセットアップ..."
/app/scripts/setup_vrm.sh

# モデルプリロードの実行
echo "📥 モデルプリロード..."
python /app/scripts/preload_models.py &
PRELOAD_PID=$!

# メインアプリケーションの起動
echo "🌐 AI Agent Application 起動..."
cd /app

# Streamlitアプリケーション
streamlit run fixed_smart_voice_agent.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --browser.gatherUsageStats=false \
    --logger.level=info \
    --logger.messageFormat="%(asctime)s - %(name)s - %(levelname)s - %(message)s" \
    > /app/logs/streamlit.log 2>&1 &

STREAMLIT_PID=$!

# ヘルスチェック
echo "🔍 ヘルスチェックを開始..."
sleep 10

# サービスの状態を確認
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "🔍 $service_name のヘルスチェック..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name が正常に起動しました"
            return 0
        fi
        
        echo "⏳ $service_name 起動中... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name の起動に失敗しました"
    return 1
}

# 各サービスのヘルスチェック
check_service "Ollama" "$OLLAMA_HOST/api/tags" &
OLLAMA_CHECK=$!

check_service "VOICEVOX" "$VOICEVOX_HOST/docs" &
VOICEVOX_CHECK=$!

check_service "Streamlit" "http://localhost:8501" &
STREAMLIT_CHECK=$!

# 全てのチェックを待つ
wait $OLLAMA_CHECK $VOICEVOX_CHECK $STREAMLIT_CHECK

# プリロードプロセスの確認
if [ -n "$PRELOAD_PID" ]; then
    echo "📥 プリロードプロセスを確認中..."
    wait $PRELOAD_PID
    PRELOAD_EXIT_CODE=$?
    
    if [ $PRELOAD_EXIT_CODE -eq 0 ]; then
        echo "✅ モデルプリロード完了"
    else
        echo "⚠️ モデルプリロードで問題が発生しました"
    fi
fi

# サービスの最終状態確認
echo ""
echo "🎯 サービス状態:"
echo "=================================="

# Ollama
if curl -f -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama: 正常 (http://localhost:11434)"
    models=$(curl -s "$OLLAMA_HOST/api/tags" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('models', [])))")
    echo "   利用可能なモデル: $models 個"
else
    echo "❌ Ollama: 異常"
fi

# VOICEVOX
if curl -f -s "$VOICEVOX_HOST/docs" > /dev/null 2>&1; then
    echo "✅ VOICEVOX: 正常 (http://localhost:50021)"
else
    echo "❌ VOICEVOX: 異常"
fi

# Streamlit
if curl -f -s "http://localhost:8501" > /dev/null 2>&1; then
    echo "✅ Streamlit: 正常 (http://localhost:8501)"
else
    echo "❌ Streamlit: 異常"
fi

# Redis
if redis-cli -h "$REDIS_HOST" ping > /dev/null 2>&1; then
    echo "✅ Redis: 正常"
else
    echo "❌ Redis: 異常"
fi

echo ""
echo "🎉 AI Agent System が起動しました！"
echo "🌐 ブラウザでアクセス: http://localhost:8501"
echo "📱 モバイルからもアクセス可能"
echo ""
echo "🔧 ログファイル:"
echo "   Streamlit: /app/logs/streamlit.log"
echo "   システムログ: docker-compose logs"
echo ""
echo "⏹️ 停止するには: docker-compose down"
echo "🔄 再起動するには: docker-compose restart"

# シグナルハンドラ
trap 'echo "🛑 シャットダウン中..."; kill $STREAMLIT_PID 2>/dev/null; exit 0' SIGTERM SIGINT

# メインプロセスを待つ
wait $STREAMLIT_PID
