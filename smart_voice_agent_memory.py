import streamlit as st
import requests
import json
import time
import os
import logging
from datetime import datetime
import uuid

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryAwareAIAgent:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.wait_timeout = int(os.getenv('OLLAMA_WAIT_TIMEOUT', '30'))
        self.memory_enabled = os.getenv('MEMORY_ENABLED', 'true').lower() == 'true'
        self.chroma_path = os.getenv('CHROMA_DB_PATH', '/app/data/chroma')
        
        # 記憶関連のパス
        self.memory_path = os.path.join(self.chroma_path, 'memory')
        self.conversation_path = os.path.join(self.chroma_path, 'conversations')
        
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
            st.session_state.memory_context = ""
    
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
                
                st.session_state.memory_context = "\n".join(context_parts)
                st.session_state.memory_loaded = True
                
                logger.info("📚 Memory context loaded")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to load memory context: {e}")
        
        st.session_state.memory_loaded = True
        return False
    
    def save_conversation(self, title=None):
        """会話を保存"""
        if not self.memory_enabled or not st.session_state.messages:
            return False
        
        try:
            # 会話データの作成
            conversation_data = {
                'id': st.session_state.conversation_id,
                'title': title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'timestamp': datetime.now().isoformat(),
                'messages': st.session_state.messages,
                'message_count': len(st.session_state.messages)
            }
            
            # 保存先ディレクトリの作成
            os.makedirs(self.conversation_path, exist_ok=True)
            
            # ファイルに保存
            file_name = f"conversation_{st.session_state.conversation_id}.json"
            file_path = os.path.join(self.conversation_path, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Conversation saved: {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save conversation: {e}")
            return False
    
    def generate_response(self, prompt):
        """AI応答を生成"""
        try:
            # 記憶コンテキストをプロンプトに追加
            full_prompt = prompt
            if st.session_state.memory_context:
                full_prompt = f"""You are an AI assistant with long-term memory. Here is your memory context about the user:

{st.session_state.memory_context}

Current conversation:
{prompt}

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
    
    def display_memory_status(self):
        """記憶状態を表示"""
        if not self.memory_enabled:
            st.warning("⚠️ 記憶機能が無効になっています")
            return
        
        if st.session_state.memory_loaded:
            st.success("✅ 記憶が読み込まれました")
            if st.session_state.memory_context:
                with st.expander("📚 記憶コンテキスト"):
                    st.text(st.session_state.memory_context)
        else:
            st.info("📚 記憶を読み込み中...")
    
    def display_conversation_controls(self):
        """会話制御を表示"""
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("💾 会話を保存", help="現在の会話を記憶に保存します"):
                if self.save_conversation():
                    st.success("✅ 会話を保存しました")
                else:
                    st.error("❌ 会話の保存に失敗しました")
        
        with col2:
            if st.button("🗑️ 会話をクリア", help="現在の会話をクリアします"):
                st.session_state.messages = []
                st.session_state.conversation_id = str(uuid.uuid4())
                st.rerun()
        
        with col3:
            title = st.text_input("会話タイトル", help="会話のタイトルを入力してください", key="conversation_title")
    
    def run(self):
        """メイン実行"""
        st.set_page_config(
            page_title="AI Agent System - Memory Enabled",
            page_icon="🧠",
            layout="centered"
        )
        
        st.title("🧠 AI Agent System - Memory Enabled")
        st.markdown("---")
        
        # AIエージェントの初期化
        if 'ai_agent' not in st.session_state:
            st.session_state.ai_agent = self
        
        ai_agent = st.session_state.ai_agent
        
        # 記憶コンテキストの読み込み
        ai_agent.load_memory_context()
        
        # 記憶状態の表示
        ai_agent.display_memory_status()
        
        # 会話制御の表示
        ai_agent.display_conversation_controls()
        
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
            
            # 自動保存（10メッセージごと）
            if len(st.session_state.messages) % 10 == 0:
                ai_agent.save_conversation()
        
        # サイドバー情報
        with st.sidebar:
            st.header("🔧 システム情報")
            
            # Ollama情報
            st.subheader("🤖 Ollama")
            st.code(f"Host: {ai_agent.ollama_host}")
            st.code(f"Model: {ai_agent.model}")
            
            # 記憶情報
            st.subheader("🧠 記憶")
            st.code(f"Memory Enabled: {ai_agent.memory_enabled}")
            st.code(f"Conversation ID: {st.session_state.conversation_id}")
            st.code(f"Messages: {len(st.session_state.messages)}")
            
            # 記憶統計
            if ai_agent.memory_enabled:
                try:
                    memory_file = os.path.join(ai_agent.memory_path, 'memory_summary.json')
                    if os.path.exists(memory_file):
                        with open(memory_file, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                        
                        st.subheader("📊 記憶統計")
                        st.code(f"Preferences: {len(memory_data.get('user_preferences', {}))}")
                        st.code(f"Topics: {len(memory_data.get('important_topics', []))}")
                        st.code(f"Last Updated: {memory_data.get('last_updated', 'Never')}")
                except:
                    st.error("記憶統計の取得に失敗しました")
            
            # システムコマンド
            st.subheader("🔧 管理コマンド")
            st.code("docker logs ai-ollama --tail=20")
            st.code("docker exec -it ai-ollama bash")
            st.code("curl -f http://localhost:11434/api/tags")

def main():
    """メイン処理"""
    agent = MemoryAwareAIAgent()
    agent.run()

if __name__ == "__main__":
    main()
