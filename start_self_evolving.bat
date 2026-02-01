@echo off
REM 自己進化型マルチエージェントシステム起動スクリプト（Windows）

echo 🧬 自己進化型AIエージェントシステムを起動します...

REM 必要なディレクトリを作成
if not exist backups mkdir backups
if not exist logs mkdir logs
if not exist data mkdir data

REM 環境変数設定
set STREAMLIT_SERVER_PORT=8502
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_SERVER_RUN_ON_SAVE=true

echo 📁 ディレクトリ構造を準備しました...
echo 🚀 Streamlitアプリケーションを起動します...

REM 自己進化GUIを起動
streamlit run self_evolving_gui.py --server.port=8502 --server.headless=true --server.runOnSave=true

pause
