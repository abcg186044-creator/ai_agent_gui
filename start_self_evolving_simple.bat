@echo off
REM 自己進化型マルチエージェントシステム起動スクリプト（シンプル版）

echo 🧬 自己進化型AIエージェントシステム（シンプル版）を起動します...

REM 環境変数設定
set STREAMLIT_SERVER_PORT=8503
set STREAMLIT_SERVER_HEADLESS=false
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo 📁 シンプル版GUIを起動します...
echo 🚀 ブラウザで http://localhost:8503 を開きます...

REM シンプル版GUIを起動
streamlit run simple_evolving_gui.py --server.port=8503

pause
