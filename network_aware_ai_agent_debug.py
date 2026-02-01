#!/usr/bin/env python3
"""
Network-Aware AI Agent - デバッグ版
"""

import streamlit as st
import time
import threading
import numpy as np
import requests
import json
import queue
import tempfile
import wave
import os
import sys
import importlib
import socket
from urllib.parse import urlparse

# 修正版動的インストーラーのインポート
sys.path.append('/app/scripts')
try:
    from dynamic_installer_fixed import install_package, auto_install_missing_packages, DynamicInstallerFixed
except ImportError:
    st.error("❌ 修正版動的インストーラーが見つかりません")
    sys.exit(1)

# 必要なライブラリの動的インストール（バージョン互換性考慮）
def install_required_packages_fixed():
    """必要なライブラリを動的にインストール（バージョン互換性考慮）"""
    # PyTorch関連パッケージの互換性バージョン
    pytorch_packages = {
        'torch': '2.1.0',
        'torchaudio': '2.1.0',
        'torchvision': '0.16.0'
    }
    
    # その他のパッケージ
    other_packages = [
        'sounddevice',
        'faster-whisper',
        'pyttsx3'
    ]
    
    installer = DynamicInstallerFixed()
    
    # まずPyTorch関連パッケージをインストール
    st.info("🔧 Installing PyTorch packages with compatible versions...")
    for package, version in pytorch_packages.items():
        try:
            import_name = package.replace('-', '_')
            importlib.import_module(import_name)
            st.success(f"✅ {package} is already installed")
        except ImportError:
            st.info(f"📦 Installing {package}=={version}...")
            success, message = install_package(package, version)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                return False
    
    # 次にその他のパッケージをインストール
    st.info("🔧 Installing other required packages...")
    for package in other_packages:
        try:
            import_name = package.replace('-', '_')
            importlib.import_module(import_name)
            st.success(f"✅ {package} is already installed")
        except ImportError:
            st.info(f"📦 Installing {package}...")
            success, message = install_package(package)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                return False
    
    return True

# ライブラリのインストールを試行
if not install_required_packages_fixed():
    st.error("❌ 必要なライブラリのインストールに失敗しました")
    st.stop()

# ライブラリのインポート（安全なインポート）
def safe_import_with_retry(package_name, import_name=None, max_retries=3):
    """安全なインポートとリトライ"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    for attempt in range(max_retries):
        try:
            module = importlib.import_module(import_name)
            print(f"✅ {package_name} imported successfully")
            return module
        except ImportError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ {package_name} import failed, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(1)
                importlib.invalidate_caches()
            else:
                st.error(f"❌ {package_name}のインポートに失敗しました: {e}")
                return None

# 各ライブラリを安全にインポート
try:
    sounddevice = safe_import_with_retry('sounddevice', 'sd')
    if sounddevice is None:
        st.error("❌ sounddeviceのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ sounddeviceのインポートエラー: {e}")
    sys.exit(1)

try:
    faster_whisper = safe_import_with_retry('faster-whisper', 'faster_whisper')
    if faster_whisper is None:
        st.error("❌ faster-whisperのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ faster-whisperのインポートエラー: {e}")
    sys.exit(1)

try:
    torch = safe_import_with_retry('torch', 'torch')
    if torch is None:
        st.error("❌ torchのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ torchのインポートエラー: {e}")
    sys.exit(1)

try:
    torchaudio = safe_import_with_retry('torchaudio', 'torchaudio')
    if torchaudio is None:
        st.error("❌ torchaudioのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ torchaudioのインポートエラー: {e}")
    sys.exit(1)

# 設定
class Config:
    MAIN_MODEL = "llama3.2"
    WHISPER_MODEL = "large-v3"
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_FORMAT = "int16"
    
    # スマートバッファリング設定
    VAD_SILENCE_THRESHOLD = 0.5
    MIN_SPEECH_DURATION = 2.0  # 最小発話時間（秒）
    MAX_PAUSE_DURATION = 2.0   # 最大休止時間（秒）
    BUFFER_TIMEOUT = 5.0       # バッファタイムアウト（秒）
    
    # UI設定
    NODDING_INTERVAL = 1.0  # 相槌間隔（秒）

class NetworkAwareAIAgent:
    """ネットワーク対応AIエージェント - デバッグ版"""
    
    def __init__(self):
        self.base_urls = []
        self.current_url_index = 0
        self.timeout = 30
        self.max_retries = 3
        self._initialize_urls()
    
    def _initialize_urls(self):
        """Ollama接続URLを初期化"""
        # コンテナ内通信（優先）
        self.base_urls.append("http://ollama:11434")
        
        # 外部アクセス用
        host_ip = os.getenv('HOST_IP', 'localhost')
        self.base_urls.append(f"http://{host_ip}:11434")
        
        # ローカルホスト（フォールバック）
        self.base_urls.append("http://localhost:11434")
        
        # ホストIPの自動検出
        try:
            host_ip = self._get_host_ip()
            if host_ip and host_ip not in [url.split('//')[1].split(':')[0] for url in self.base_urls]:
                self.base_urls.append(f"http://{host_ip}:11434")
        except:
            pass
        
        # デバッグ情報
        print(f"🔍 Initialized URLs: {self.base_urls}")
    
    def _get_host_ip(self):
        """ホストIPを自動検出"""
        try:
            # コンテナ内からホストIPを取得
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            host_ip = s.getsockname()[0]
            s.close()
            print(f"🔍 Detected host IP: {host_ip}")
            return host_ip
        except Exception as e:
            print(f"🔍 Error detecting host IP: {e}")
            return None
    
    def _test_connection(self, url):
        """接続テスト"""
        try:
            print(f"🔍 Testing connection to: {url}")
            response = requests.get(f"{url}/api/tags", timeout=5)
            success = response.status_code == 200
            print(f"🔍 Connection test result: {success} (status: {response.status_code})")
            return success
        except Exception as e:
            print(f"🔍 Connection test error: {e}")
            return False
    
    def _get_working_url(self):
        """動作中のURLを取得"""
        # 既知の動作URLを優先
        if hasattr(self, '_last_working_url') and self._test_connection(self._last_working_url):
            print(f"🔍 Using last working URL: {self._last_working_url}")
            return self._last_working_url
        
        # 全URLをテスト
        for url in self.base_urls:
            if self._test_connection(url):
                self._last_working_url = url
                print(f"🔍 Found working URL: {url}")
                return url
        
        print("🔍 No working URL found")
        return None
    
    def generate_response(self, prompt, model="llama3.2"):
        """AI応答を生成（ネットワーク対応）"""
        print(f"🔍 Generating response with prompt: {prompt[:50]}...")
        
        working_url = self._get_working_url()
        
        if not working_url:
            error_msg = "❌ Ollamaサーバーに接続できません。サーバーが起動しているか確認してください。"
            print(f"🔍 Error: {error_msg}")
            return error_msg
        
        print(f"🔍 Using URL: {working_url}")
        
        for attempt in range(self.max_retries):
            try:
                print(f"🔍 Attempt {attempt + 1}/{self.max_retries}")
                
                data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                
                print(f"🔍 Sending request to: {working_url}/api/generate")
                print(f"🔍 Request data: {data}")
                
                response = requests.post(
                    f"{working_url}/api/generate",
                    json=data,
                    timeout=self.timeout
                )
                
                print(f"🔍 Response status: {response.status_code}")
                print(f"🔍 Response text: {response.text[:200]}...")
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    print(f"🔍 Generated response: {response_text[:50]}...")
                    return response_text
                else:
                    if attempt < self.max_retries - 1:
                        # 次のURLを試す
                        working_url = self._get_working_url()
                        if not working_url:
                            break
                        time.sleep(1)
                    else:
                        error_msg = f"❌ 応答生成エラー: HTTP {response.status_code}"
                        print(f"🔍 Error: {error_msg}")
                        return error_msg
                        
            except requests.exceptions.ConnectionError as e:
                print(f"🔍 Connection error: {e}")
                if attempt < self.max_retries - 1:
                    # 次のURLを試す
                    working_url = self._get_working_url()
                    if not working_url:
                        break
                    time.sleep(1)
                else:
                    error_msg = "❌ Ollamaサーバーへの接続に失敗しました。"
                    print(f"🔍 Error: {error_msg}")
                    return error_msg
            except requests.exceptions.Timeout as e:
                print(f"🔍 Timeout error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                else:
                    error_msg = "❌ 応答生成タイムアウト"
                    print(f"🔍 Error: {error_msg}")
                    return error_msg
            except Exception as e:
                error_msg = f"❌ 応答生成エラー: {str(e)}"
                print(f"🔍 Error: {error_msg}")
                return error_msg
        
        error_msg = "❌ すべての接続試行が失敗しました。"
        print(f"🔍 Error: {error_msg}")
        return error_msg
    
    def get_connection_status(self):
        """接続状態を取得"""
        status = {
            "working_url": None,
            "all_urls": self.base_urls,
            "url_status": {}
        }
        
        for url in self.base_urls:
            status["url_status"][url] = self._test_connection(url)
            if status["url_status"][url] and not status["working_url"]:
                status["working_url"] = url
        
        return status
    
    def get_available_models(self):
        """利用可能なモデルを取得"""
        working_url = self._get_working_url()
        
        if not working_url:
            print("🔍 No working URL for models")
            return []
        
        try:
            print(f"🔍 Getting models from: {working_url}/api/tags")
            response = requests.get(f"{working_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                print(f"🔍 Available models: {models}")
                return models
        except Exception as e:
            print(f"🔍 Error getting models: {e}")
        
        return []

class SimpleAIAgent:
    """シンプルAIエージェント - デバッグ用"""
    
    def __init__(self):
        self.ai_agent = NetworkAwareAIAgent()
        
    def generate_response(self, transcription_text):
        """AI応答生成"""
        try:
            if not transcription_text:
                return "音声が認識できませんでした。もう一度お試しください。"
            
            # llama3.2で応答生成
            prompt = f"""あなたはスマート音声AIアシスタントです。ユーザーの音声入力に基づいて、自然で丁寧な応答を生成してください。

ユーザーの音声入力: {transcription_text}

ユーザーのペースを尊重し、適切なタイミングで応答してください。自然な対話を心がけてください。"""
            
            response = self.ai_agent.generate_response(prompt)
            
            return response
            
        except Exception as e:
            return f"❌ 応答生成エラー: {str(e)}"

def render_debug_info(ai_agent):
    """デバッグ情報表示"""
    st.subheader("🔍 デバッグ情報")
    
    # 接続状態
    connection_status = ai_agent.ai_agent.get_connection_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**接続状態**:")
        if connection_status["working_url"]:
            st.success(f"✅ 現在のURL: {connection_status['working_url']}")
        else:
            st.error("❌ 接続できません")
        
        st.write("**全URLの状態**:")
        for url, status in connection_status["url_status"].items():
            if status:
                st.success(f"✅ {url}")
            else:
                st.error(f"❌ {url}")
    
    with col2:
        st.write("**利用可能なモデル**:")
        models = ai_agent.ai_agent.get_available_models()
        if models:
            for model in models:
                st.write(f"📦 {model}")
        else:
            st.warning("⚠️ モデルが見つかりません")
        
        # 環境変数
        st.write("**環境変数**:")
        st.write(f"HOST_IP: {os.getenv('HOST_IP', 'Not set')}")
        st.write(f"OLLAMA_HOST: {os.getenv('OLLAMA_HOST', 'Not set')}")
        st.write(f"EXTERNAL_ACCESS: {os.getenv('EXTERNAL_ACCESS', 'Not set')}")

def render_simple_interface(ai_agent):
    """シンプルインターフェース"""
    st.header("🎤️ デバッグ版AIエージェント")
    
    # テキスト入力のみ
    st.subheader("⌨️ テキスト入力")
    
    user_input = st.text_area(
        "💬 メッセージを入力してください",
        key="text_input",
        height=100,
        placeholder="ここにメッセージを入力..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 送信", key="send_text", type="primary"):
            if user_input.strip():
                with st.spinner("🤖 AI応答生成中..."):
                    ai_response = ai_agent.generate_response(user_input)
                    st.session_state.text_ai_response = ai_response
                    st.session_state.last_text_input = user_input
                    st.success("✅ AI応答生成完了")
            else:
                st.warning("⚠️ メッセージを入力してください")
    
    with col2:
        if st.button("🗑️ クリア", key="clear_text"):
            st.session_state.text_input = ""
            st.session_state.text_ai_response = ""
            st.success("✅ 入力をクリアしました")
    
    # AI応答表示
    if st.session_state.get("text_ai_response"):
        st.subheader("🤖 AI応答")
        st.write(st.session_state.text_ai_response)
    
    # デバッグ情報
    render_debug_info(ai_agent)

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🔍 Debug AI Agent",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 Debug AI Agent")
    st.markdown("### デバッグ版 - ネットワーク接続の詳細確認")
    
    # セッション状態初期化
    if 'agent' not in st.session_state:
        st.session_state.agent = SimpleAIAgent()
        st.success("✅ デバッグAIエージェント初期化完了")
    
    # メインインターフェース
    render_simple_interface(st.session_state.agent)

if __name__ == "__main__":
    main()
