#!/bin/bash

# 自己進化型マルチエージェントシステム起動スクリプト

echo "🧬 自己進化型AIエージェントシステムを起動します..."

# 必要なディレクトリを作成
mkdir -p backups
mkdir -p logs
mkdir -p data

# 環境変数設定
export STREAMLIT_SERVER_PORT=8502
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ホットリロード有効化
export STREAMLIT_SERVER_RUN_ON_SAVE=true

echo "📁 ディレクトリ構造を準備しました..."
echo "🚀 Streamlitアプリケーションを起動します..."

# 自己進化GUIを起動
streamlit run self_evolving_gui.py --server.port=8502 --server.headless=true --server.runOnSave=true
