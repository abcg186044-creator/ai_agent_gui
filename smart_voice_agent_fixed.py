import streamlit as st
import requests
import json
import time
import os
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedAIAgent:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.wait_timeout = int(os.getenv('OLLAMA_WAIT_TIMEOUT', '120'))
        
    def wait_for_ollama(self):
        """Ollamaが起動するのを待つ"""
        logger.info("🔄 Ollamaの起動を待っています...")
        
        start_time = time.time()
        while time.time() - start_time < self.wait_timeout:
            try:
                response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollamaが起動しました")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info("⏳ Ollama起動中...")
            time.sleep(5)
        
        logger.error("❌ Ollamaの起動タイムアウト")
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
    
    def generate_response(self, prompt):
        """AI応答を生成"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
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

def main():
    st.set_page_config(
        page_title="AI Agent System - Fixed",
        page_icon="🤖",
        layout="centered"
    )
    
    st.title("🤖 AI Agent System - Fixed")
    st.markdown("---")
    
    # AIエージェントの初期化
    if 'ai_agent' not in st.session_state:
        st.session_state.ai_agent = FixedAIAgent()
    
    ai_agent = st.session_state.ai_agent
    
    # Ollamaの状態確認
    with st.spinner("🔄 Ollamaの状態を確認中..."):
        if not ai_agent.wait_for_ollama():
            st.error("❌ Ollamaが起動していません")
            st.stop()
    
    # モデルの確認
    if not ai_agent.check_model():
        st.warning(f"⚠️ モデル '{ai_agent.model}' が見つかりません")
        st.info("💡 モデルをダウンロードしてください:")
        st.code(f"docker exec -it ai-ollama ollama pull {ai_agent.model}")
        st.stop()
    
    # 成功メッセージ
    st.success(f"✅ Ollamaが正常に起動しました (モデル: {ai_agent.model})")
    
    # チャット履歴
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
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
        
        # モデル一覧
        try:
            response = requests.get(f"{ai_agent.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                st.subheader("📋 利用可能なモデル")
                for model in models:
                    st.code(f"• {model}")
        except:
            st.error("モデル情報の取得に失敗しました")
        
        # システムコマンド
        st.subheader("🔧 管理コマンド")
        st.code("docker logs ai-ollama --tail=20")
        st.code("docker exec -it ai-ollama bash")
        st.code("curl -f http://localhost:11434/api/tags")

if __name__ == "__main__":
    main()
