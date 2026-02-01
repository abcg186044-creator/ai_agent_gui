#!/bin/bash

# 自己進化型マルチエージェントシステム起動スクリプト（シンプル版）

echo "🧬 自己進化型AIエージェントシステム（シンプル版）を起動します..."

# 環境変数設定
export STREAMLIT_SERVER_PORT=8503
export STREAMLIT_SERVER_HEADLESS=false
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo "📁 シンプル版GUIを起動します..."
echo "🚀 ブラウザで http://localhost:8503 を開きます..."

# シンプル版GUIを起動
streamlit run simple_evolving_gui.py --server.port=8503
