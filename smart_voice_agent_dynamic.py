import streamlit as st
import requests
import json
import time
import os
import sys
import logging
import traceback
import importlib
from datetime import datetime
import uuid
import subprocess

# 動的インストーラーのインポート
sys.path.append('/app/scripts')
try:
    from dynamic_installer import install_package, auto_install_missing_packages, DynamicInstaller
except ImportError:
    st.error("❌ 動的インストーラーが見つかりません")
    sys.exit(1)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfContainedAIAgent:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.wait_timeout = int(os.getenv('OLLAMA_WAIT_TIMEOUT', '30'))
        self.memory_enabled = os.getenv('MEMORY_ENABLED', 'true').lower() == 'true'
        self.dynamic_install_enabled = os.getenv('DYNAMIC_INSTALL_ENABLED', 'true').lower() == 'true'
        self.chroma_path = os.getenv('CHROMA_DB_PATH', '/app/data/chroma')
        
        # 記憶関連のパス
        self.memory_path = os.path.join(self.chroma_path, 'memory')
        self.conversation_path = os.path.join(self.chroma_path, 'conversations')
        
        # 動的インストーラーの初期化
        self.installer = DynamicInstaller()
        
        # セッションIDの生成
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = str(uuid.uuid4())
        
        # 記憶読み込み済みフラグ
        if 'memory_loaded' not in st.session_state:
            st.session_state.memory_loaded = False
        
        # 会話履歴の初期化
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # 記憶コンテキストの初期化
        if 'memory_context' not in st.session_state:
            st.session_state.memory_context = []
        
        # インストール通知の初期化
        if 'install_notifications' not in st.session_state:
            st.session_state.install_notifications = []
    
    def wait_for_ollama(self):
        """Ollamaが起動するのを待つ"""
        logger.info("🔄 Waiting for Ollama to start...")
        
        start_time = time.time()
        while time.time() - start_time < self.wait_timeout:
            try:
                response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollama is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info("⏳ Waiting for Ollama...")
            time.sleep(3)
        
        logger.error("❌ Ollama startup timeout")
        return False
    
    def check_model(self):
        """モデルが存在するか確認"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                available_models = [model['name'] for model in data.get('models', [])]
                return self.model in available_models
            return False
        except:
            return False
    
    def load_memory_context(self):
        """記憶コンテキストを読み込む"""
        if not self.memory_enabled or st.session_state.memory_loaded:
            return
        
        memory_file = os.path.join(self.memory_path, 'memory_summary.json')
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                
                # 記憶コンテキストの作成
                context_parts = []
                
                if memory_data.get('user_preferences'):
                    context_parts.append("## User Preferences:")
                    for key, value in memory_data['user_preferences'].items():
                        context_parts.append(f"- {key}: {value}")
                
                if memory_data.get('important_topics'):
                    context_parts.append("\n## Important Topics:")
                    for topic in memory_data['important_topics']:
                        context_parts.append(f"- {topic}")
                
                if memory_data.get('last_updated'):
                    context_parts.append(f"\n## Memory Last Updated: {memory_data['last_updated']}")
                
                st.session_state.memory_context = context_parts
                st.session_state.memory_loaded = True
                
                logger.info("📚 Memory context loaded")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to load memory context: {e}")
        
        st.session_state.memory_loaded = True
        return False
    
    def execute_code_with_auto_install(self, code):
        """コードを実行し、必要なライブラリを自動インストール"""
        if not self.dynamic_install_enabled:
            # 動的インストールが無効な場合は通常実行
            return self.execute_code_safely(code)
        
        try:
            # まず通常実行を試行
            logger.info("🔄 Executing code...")
            result = self.execute_code_safely(code)
            return result, None
            
        except Exception as e:
            error_message = str(e)
            
            # ModuleNotFoundErrorを検出
            if "ModuleNotFoundError" in error_message:
                logger.info("🔍 ModuleNotFoundError detected, attempting auto-install...")
                
                # 自動インストールを試行
                success, install_message, package_name = auto_install_missing_packages(error_message)
                
                if success:
                    # インストール成功通知
                    notification = {
                        "type": "install_success",
                        "package": package_name,
                        "message": f"✅ {package_name} をインストールしました！",
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.install_notifications.append(notification)
                    
                    # 再度実行を試行
                    logger.info("🔄 Retrying code execution after installation...")
                    try:
                        result = self.execute_code_safely(code)
                        return result, notification
                    except Exception as retry_error:
                        return f"❌ インストール後もエラーが発生: {str(retry_error)}", notification
                else:
                    # インストール失敗通知
                    notification = {
                        "type": "install_failed",
                        "package": package_name or "unknown",
                        "message": f"❌ {package_name or 'ライブラリ'} のインストールに失敗しました",
                        "error": install_message,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.install_notifications.append(notification)
                    return f"❌ ライブラリの自動インストールに失敗: {install_message}", notification
            else:
                # ModuleNotFoundError以外のエラー
                return f"❌ コード実行エラー: {error_message}", None
    
    def execute_code_safely(self, code):
        """安全なコード実行"""
        try:
            # 安全な実行環境の準備
            exec_globals = {
                '__builtins__': __builtins__,
                'st': st,
                'pd': None,  # pandasのプレースホルダー
                'np': None,  # numpyのプレースホルダー
                'plt': None, # matplotlibのプレースホルダー
                'requests': requests,
                'json': json,
                'datetime': datetime,
                'time': time,
                'os': os,
                'sys': sys,
                'logger': logger,
                'traceback': traceback,
            }
            
            # よく使うライブラリを動的にインポート
            common_libraries = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy', 'sklearn']
            for lib in common_libraries:
                try:
                    exec_globals[lib.split('.')[0]] = importlib.import_module(lib)
                except ImportError:
                    pass
            
            # コード実行
            exec(code, exec_globals)
            
            # 結果の収集
            result_vars = {}
            for name, value in exec_globals.items():
                if not name.startswith('__') and name not in ['st', 'logger', 'traceback']:
                    try:
                        # 大きなオブジェクトは文字列化しない
                        if hasattr(value, '__len__') and len(str(value)) > 1000:
                            result_vars[name] = f"<{type(value).__name__} object (too large to display)>"
                        else:
                            result_vars[name] = str(value)
                    except:
                        result_vars[name] = f"<{type(value).__name__} object>"
            
            return f"✅ コードが正常に実行されました\n\n結果:\n{json.dumps(result_vars, indent=2, ensure_ascii=False)}"
            
        except Exception as e:
            error_msg = f"❌ 実行エラー: {str(e)}\n\n詳細:\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def generate_response(self, prompt):
        """AI応答を生成"""
        try:
            # 記憶コンテキストをプロンプトに追加
            full_prompt = prompt
            if st.session_state.memory_context:
                memory_context_str = "\n".join(st.session_state.memory_context)
                full_prompt = f"""You are an AI assistant with long-term memory and dynamic package installation capabilities. Here is your memory context about the user:

{memory_context_str}

Current conversation:
{prompt}

You can:
1. Remember user preferences and conversations
2. Automatically install missing Python packages when needed
3. Execute Python code and handle errors gracefully
4. Learn and adapt from interactions

Please respond naturally while keeping the memory context in mind."""
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '応答がありません')
            else:
                return f"エラー: {response.status_code}"
                
        except Exception as e:
            return f"エラー: {str(e)}"
    
    def display_install_notifications(self):
        """インストール通知を表示"""
        if st.session_state.install_notifications:
            with st.expander("🔧 ライブラリインストール通知", expanded=True):
                for notification in st.session_state.install_notifications[-5:]:  # 最新5件
                    if notification['type'] == 'install_success':
                        st.success(notification['message'])
                    else:
                        st.error(f"{notification['message']}\n詳細: {notification.get('error', 'Unknown error')}")
                    
                    st.caption(f"時刻: {notification['timestamp']}")
    
    def display_dynamic_status(self):
        """動的機能の状態を表示"""
        col1, col2 = st.columns(2)
        
        with col1:
            if self.dynamic_install_enabled:
                st.success("🔧 動的インストール: 有効")
            else:
                st.warning("🔧 動的インストール: 無効")
        
        with col2:
            # インストール済みパッケージ数
            installed_count = len(self.installer.list_installed_packages())
            st.info(f"📦 インストール済み: {installed_count}個")
    
    def display_package_manager(self):
        """パッケージ管理インターフェース"""
        with st.expander("🔧 パッケージ管理"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                package_name = st.text_input("パッケージ名", key="package_input")
                version = st.text_input("バージョン（任意）", key="version_input")
            
            with col2:
                st.write("")  # スペース
                st.write("")  # スペース
                if st.button("📦 インストール", key="install_button"):
                    if package_name:
                        with st.spinner(f"{package_name} をインストール中..."):
                            success, message = install_package(package_name, version if version else None)
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("パッケージ名を入力してください")
            
            # インストール済みパッケージ一覧
            st.subheader("📋 インストール済みパッケージ")
            installed_packages = self.installer.list_installed_packages()
            
            if installed_packages:
                for package in installed_packages[-10:]:  # 最新10件
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.code(package)
                    with col2:
                        if st.button("ℹ️", key=f"info_{package}"):
                            info = self.installer.get_package_info(package)
                            st.text(info)
            else:
                st.info("インストール済みパッケージはありません")
    
    def run(self):
        """メイン実行"""
        st.set_page_config(
            page_title="AI Agent System - Self Contained",
            page_icon="🤖",
            layout="centered"
        )
        
        st.title("🤖 AI Agent System - Self Contained")
        st.markdown("---")
        
        # AIエージェントの初期化
        if 'ai_agent' not in st.session_state:
            st.session_state.ai_agent = self
        
        ai_agent = st.session_state.ai_agent
        
        # 記憶コンテキストの読み込み
        ai_agent.load_memory_context()
        
        # 動的機能の状態表示
        ai_agent.display_dynamic_status()
        
        # インストール通知の表示
        ai_agent.display_install_notifications()
        
        # パッケージ管理インターフェース
        ai_agent.display_package_manager()
        
        # Ollamaの状態確認
        with st.spinner("🔄 Ollamaの状態を確認中..."):
            if not ai_agent.wait_for_ollama():
                st.error("❌ Ollamaが起動していません")
                st.stop()
        
        # モデルの確認
        if not ai_agent.check_model():
            st.warning(f"⚠️ モデル '{ai_agent.model}' が見つかりません")
            st.info("💡 モデルはイメージ内に組み込まれているはずです")
            st.stop()
        
        # 成功メッセージ
        st.success(f"✅ Ollamaが正常に起動しました (モデル: {ai_agent.model})")
        
        # メッセージ表示
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # ユーザー入力
        if prompt := st.chat_input("メッセージを入力してください..."):
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # AI応答
            with st.chat_message("assistant"):
                with st.spinner("🤖 考え中..."):
                    response = ai_agent.generate_response(prompt)
                st.markdown(response)
            
            # AI応答を追加
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # サイドバー情報
        with st.sidebar:
            st.header("🔧 システム情報")
            
            # Ollama情報
            st.subheader("🤖 Ollama")
            st.code(f"Host: {ai_agent.ollama_host}")
            st.code(f"Model: {ai_agent.model}")
            
            # 動的機能情報
            st.subheader("🔧 動的機能")
            st.code(f"Dynamic Install: {ai_agent.dynamic_install_enabled}")
            st.code(f"Memory Enabled: {ai_agent.memory_enabled}")
            
            # インストール統計
            if ai_agent.dynamic_install_enabled:
                summary = ai_agent.installer.get_install_summary()
                st.subheader("📊 インストール統計")
                st.code(f"Total: {summary['total_packages']}")
                st.code(f"Success: {summary['successful']}")
                st.code(f"Failed: {summary['failed']}")
            
            # システムコマンド
            st.subheader("🔧 管理コマンド")
            st.code("docker logs ai-ollama --tail=20")
            st.code("docker exec -it ai-agent-app bash")
            st.code("curl -f http://localhost:11434/api/tags")

def main():
    """メイン処理"""
    agent = SelfContainedAIAgent()
    agent.run()

if __name__ == "__main__":
    main()
