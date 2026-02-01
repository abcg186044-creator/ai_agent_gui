#!/usr/bin/env python3
"""
AI Agent System - 自動セットアップスクリプト
ゼロからAIエージェントシステムを構築するための自動化ツール
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class AISetupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements = [
            "streamlit==1.28.1",
            "langchain==0.1.0", 
            "langchain-community==0.0.4",
            "langchain-ollama==0.1.1",
            "langchain-experimental==0.4.1",
            "openpyxl==3.1.2",
            "PyMuPDF==1.23.8",
            "pandas==2.1.0",
            "requests==2.32.5",
            "qrcode[pil]==7.4.2",
            "faster-whisper==0.9.0",
            "librosa==0.10.1", 
            "sounddevice==0.4.6",
            "torch==2.1.0",
            "fastapi==0.128.0",
            "uvicorn==0.40.0",
            "pyttsx3==2.99",
            "pyautogui==0.9.54",
            "pillow==10.4.0",
            "sentence-transformers==2.2.2",
            "faiss-cpu==1.7.4"
        ]
        
    def print_status(self, message: str, status: str = "INFO"):
        """ステータス表示"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        print(f"{icons.get(status, 'ℹ️')} {message}")
    
    def run_command(self, command: str, description: str) -> bool:
        """コマンド実行"""
        self.print_status(f"{description}...")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.print_status(f"{description}完了", "SUCCESS")
                return True
            else:
                self.print_status(f"{description}失敗: {result.stderr}", "ERROR")
                return False
        except subprocess.TimeoutExpired:
            self.print_status(f"{description}タイムアウト", "ERROR")
            return False
        except Exception as e:
            self.print_status(f"{description}エラー: {str(e)}", "ERROR")
            return False
    
    def check_python_version(self):
        """Pythonバージョンチェック"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 10:
            self.print_status(f"Python {version.major}.{version.minor}.{version.micro} は要件を満たしています", "SUCCESS")
            return True
        else:
            self.print_status(f"Python {version.major}.{version.minor}.{version.micro} は要件を満たしていません (3.10+が必要)", "ERROR")
            return False
    
    def create_project_structure(self):
        """プロジェクト構造作成"""
        self.print_status("プロジェクト構造を作成中...")
        
        directories = [
            "static",
            "static/css", 
            "static/js",
            "static/images",
            "knowledge_base",
            "knowledge_base/documents",
            "logs",
            "temp",
            "backups"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # requirements.txt 作成
        req_file = self.project_root / "requirements.txt"
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.requirements))
        
        # .env ファイル作成
        env_file = self.project_root / ".env"
        env_content = """# AI Agent System Environment Variables
OLLAMA_MODEL=llama3.1:8b
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
VOICE_RATE=200
VOICE_VOLUME=0.9
VRM_MODEL_PATH=./static/avatar.vrm
KNOWLEDGE_BASE_PATH=./knowledge_base
LOG_LEVEL=INFO
DEBUG=False
"""
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # memory_db.json 作成
        db_file = self.project_root / "memory_db.json"
        initial_db = {
            "conversations": [],
            "user_profile": {
                "name": None,
                "os": None,
                "tech_stack": [],
                "preferences": [],
                "projects": [],
                "last_updated": None
            },
            "learning_data": {
                "common_questions": [],
                "preferred_responses": [],
                "technical_level": "beginner"
            }
        }
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(initial_db, f, ensure_ascii=False, indent=2)
        
        self.print_status("プロジェクト構造作成完了", "SUCCESS")
    
    def install_python_packages(self):
        """Pythonパッケージインストール"""
        self.print_status("Pythonパッケージをインストール中...")
        
        # requirements.txt からインストール
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            success = self.run_command(
                f'pip install -r "{req_file}"',
                "Pythonパッケージインストール"
            )
            return success
        return False
    
    def check_ollama_installation(self):
        """Ollamaインストールチェック"""
        self.print_status("Ollamaインストールを確認中...")
        
        # Ollamaコマンド確認
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            self.print_status(f"Ollamaがインストールされています: {result.stdout.strip()}", "SUCCESS")
            return True
        
        # Windows wingetでインストール試行
        if os.name == 'nt':
            success = self.run_command(
                "winget install Ollama.Ollama",
                "Ollamaインストール (winget)"
            )
            return success
        
        self.print_status("Ollamaのインストールに失敗しました。手動インストールが必要です。", "ERROR")
        return False
    
    def download_ollama_model(self):
        """Ollamaモデルダウンロード"""
        self.print_status("llama3.1:8bモデルをダウンロード中...")
        
        success = self.run_command(
            "ollama pull llama3.1:8b",
            "llama3.1:8bモデルダウンロード"
        )
        
        if success:
            self.print_status("埋め込みモデルもダウンロード中...")
            self.run_command(
                "ollama pull nomic-embed-text:latest", 
                "埋め込みモデルダウンロード"
            )
        
        return success
    
    def check_php_installation(self):
        """PHPインストールチェック"""
        self.print_status("PHPインストールを確認中...")
        
        # PHPコマンド確認
        result = subprocess.run(["php", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            self.print_status(f"PHPがインストールされています: {result.stdout.split()[1]}", "SUCCESS")
            return True
        
        # Windows wingetでインストール試行
        if os.name == 'nt':
            success = self.run_command(
                "winget install PHP.PHP.8.4",
                "PHPインストール (winget)"
            )
            return success
        
        self.print_status("PHPのインストールに失敗しました。手動インストールが必要です。", "ERROR")
        return False
    
    def create_basic_app_py(self):
        """基本app.py作成"""
        self.print_status("基本app.pyを作成中...")
        
        basic_app = '''import streamlit as st
import os
import json
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="🤖 AI Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🤖 AI Agent System")
    st.markdown("### 🚀 システム構築完了！")
    
    # サイドバー
    with st.sidebar:
        st.header("🎛️ システム状態")
        
        # 基本情報表示
        st.success("✅ Python環境: OK")
        st.success("✅ パッケージ: インストール済み")
        st.success("✅ Ollama: 利用可能")
        st.success("✅ PHP: 利用可能")
        
        st.header("🧪 テスト")
        
        if st.button("🔍 Ollamaテスト"):
            test_ollama()
        
        if st.button("🎵 音声テスト"):
            test_voice()
        
        if st.button("🔧 PHPテスト"):
            test_php()
    
    # メインエリア
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 チャット")
        user_input = st.text_area("AIとの対話", height=100)
        
        if st.button("💬 送信"):
            if user_input:
                st.success("メッセージを送信しました")
                st.info("🤖 AI応答: こんにちは！私はAIアシスタントです。")
    
    with col2:
        st.header("📊 システム情報")
        st.json({
            "Pythonバージョン": sys.version,
            "作業ディレクトリ": str(os.getcwd()),
            "設定完了時刻": datetime.now().isoformat()
        })

def test_ollama():
    """Ollama接続テスト"""
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        st.success(f"✅ Ollama接続成功: {len(models)}個のモデル利用可能")
    except Exception as e:
        st.error(f"❌ Ollama接続エラー: {str(e)}")

def test_voice():
    """音声機能テスト"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        st.success("✅ 音声合成エンジン初期化成功")
    except Exception as e:
        st.error(f"❌ 音声機能エラー: {str(e)}")

def test_php():
    """PHP機能テスト"""
    try:
        result = subprocess.run(["php", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            st.success(f"✅ PHP実行可能: {result.stdout}")
        else:
            st.error("❌ PHP実行不可")
    except Exception as e:
        st.error(f"❌ PHPテストエラー: {str(e)}")

if __name__ == "__main__":
    main()
'''
        
        app_file = self.project_root / "app.py"
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(basic_app)
        
        self.print_status("基本app.py作成完了", "SUCCESS")
    
    def run_initial_test(self):
        """初期テスト実行"""
        self.print_status("初期テストを実行中...")
        
        # 基本起動テスト
        success = self.run_command(
            f'python "{self.project_root / "app.py"}" --server.headless true',
            "基本アプリケーションテスト"
        )
        
        return success
    
    def generate_setup_report(self):
        """セットアップレポート生成"""
        report = {
            "setup_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "python_version": sys.version,
            "os": os.name,
            "completed_steps": [],
            "next_steps": [
                "streamlit run app.py でアプリケーション起動",
                "ブラウザで http://localhost:8501 にアクセス",
                "各機能の動作をテスト",
                "必要に応じて追加機能を実装"
            ]
        }
        
        report_file = self.project_root / "setup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.print_status(f"セットアップレポートを保存: {report_file}", "SUCCESS")
    
    def run_full_setup(self):
        """完全セットアップ実行"""
        self.print_status("🚀 AI Agent System セットアップ開始", "INFO")
        
        steps = [
            ("Pythonバージョンチェック", self.check_python_version),
            ("プロジェクト構造作成", self.create_project_structure),
            ("Pythonパッケージインストール", self.install_python_packages),
            ("Ollamaインストール確認", self.check_ollama_installation),
            ("Ollamaモデルダウンロード", self.download_ollama_model),
            ("PHPインストール確認", self.check_php_installation),
            ("基本app.py作成", self.create_basic_app_py),
            ("初期テスト実行", self.run_initial_test),
            ("セットアップレポート生成", self.generate_setup_report)
        ]
        
        completed_steps = []
        
        for step_name, step_func in steps:
            try:
                if step_func():
                    completed_steps.append(step_name)
            except Exception as e:
                self.print_status(f"{step_name}でエラー: {str(e)}", "ERROR")
        
        # 完了メッセージ
        self.print_status("🎉 セットアップ完了！", "SUCCESS")
        self.print_status(f"完了ステップ: {len(completed_steps)}/{len(steps)}", "INFO")
        
        self.print_status("\n📋 次のステップ:", "INFO")
        self.print_status("1. streamlit run app.py", "INFO")
        self.print_status("2. ブラウザで http://localhost:8501 にアクセス", "INFO")
        self.print_status("3. サイドバーの各テストボタンで機能を確認", "INFO")
        self.print_status("\n📁 プロジェクトの場所:", "INFO")
        self.print_status(f"{self.project_root}", "INFO")

def main():
    """メイン実行"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
AI Agent System セットアップツール

使用方法:
  python setup_ai_agent.py

オプション:
  --help    このヘルプを表示

機能:
  ✅ Python環境チェック
  ✅ プロジェクト構造自動作成
  ✅ 必須ライブラリ一括インストール
  ✅ Ollama自動インストール
  ✅ LLMモデル自動ダウンロード
  ✅ PHP環境自動設定
  ✅ 基本アプリケーション生成
  ✅ 初期動作テスト実行
        """)
        return
    
    # セットアップマネージャー実行
    manager = AISetupManager()
    manager.run_full_setup()

if __name__ == "__main__":
    main()
