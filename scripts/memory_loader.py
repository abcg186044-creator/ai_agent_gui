#!/usr/bin/env python3
"""
記憶読み込みスクリプト
起動時に外部記憶データベースを読み込み、AIにコンテキストを提供
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
import requests

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryLoader:
    def __init__(self):
        self.chroma_path = os.getenv('CHROMA_DB_PATH', '/app/data/chroma')
        self.memory_path = os.path.join(self.chroma_path, 'memory')
        self.conversation_path = os.path.join(self.chroma_path, 'conversations')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        # 記憶ディレクトリの作成
        Path(self.memory_path).mkdir(parents=True, exist_ok=True)
        Path(self.conversation_path).mkdir(parents=True, exist_ok=True)
    
    def wait_for_ollama(self, timeout=60):
        """Ollamaが起動するのを待つ"""
        logger.info("🔄 Waiting for Ollama to start...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
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
    
    def load_memory_summary(self):
        """記憶の要約を読み込む"""
        memory_file = os.path.join(self.memory_path, 'memory_summary.json')
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                
                logger.info("📚 Memory summary loaded")
                return memory_data
            except Exception as e:
                logger.error(f"❌ Failed to load memory summary: {e}")
        
        return {
            'user_preferences': {},
            'important_topics': [],
            'conversation_style': {},
            'last_updated': None
        }
    
    def load_recent_conversations(self, limit=5):
        """最近の会話を読み込む"""
        conversations = []
        
        if os.path.exists(self.conversation_path):
            try:
                for file_name in sorted(os.listdir(self.conversation_path))[-limit:]:
                    if file_name.endswith('.json'):
                        file_path = os.path.join(self.conversation_path, file_name)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            conversation = json.load(f)
                            conversations.append(conversation)
                
                logger.info(f"💬 Loaded {len(conversations)} recent conversations")
            except Exception as e:
                logger.error(f"❌ Failed to load conversations: {e}")
        
        return conversations
    
    def create_memory_context(self, memory_data, conversations):
        """記憶からコンテキストを作成"""
        context_parts = []
        
        # ユーザー設定の追加
        if memory_data.get('user_preferences'):
            context_parts.append("## User Preferences:")
            for key, value in memory_data['user_preferences'].items():
                context_parts.append(f"- {key}: {value}")
        
        # 重要なトピックの追加
        if memory_data.get('important_topics'):
            context_parts.append("\n## Important Topics:")
            for topic in memory_data['important_topics']:
                context_parts.append(f"- {topic}")
        
        # 最近の会話の追加
        if conversations:
            context_parts.append("\n## Recent Conversations:")
            for conv in conversations[-3:]:  # 最新3件
                context_parts.append(f"- {conv.get('title', 'Untitled')}: {conv.get('summary', 'No summary')}")
        
        # 最終更新日時の追加
        if memory_data.get('last_updated'):
            context_parts.append(f"\n## Memory Last Updated: {memory_data['last_updated']}")
        
        return "\n".join(context_parts)
    
    def warm_up_model_with_memory(self, context):
        """記憶コンテキストでモデルをウォームアップ"""
        logger.info("🧠 Warming up model with memory context...")
        
        warmup_prompt = f"""You are an AI assistant with long-term memory. Here is your memory context about the user:

{context}

Please acknowledge that you have loaded this memory and are ready to continue the conversation. Keep this context in mind for future responses."""

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": warmup_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "max_tokens": 200
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                logger.info("✅ Model warmed up with memory context")
                logger.info(f"🤖 AI Response: {ai_response[:100]}...")
                return True
            else:
                logger.error(f"❌ Failed to warm up model: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error warming up model: {e}")
            return False
    
    def load_and_apply_memory(self):
        """記憶を読み込み、モデルに適用"""
        logger.info("🧠 Starting memory loading process...")
        
        # 1. Ollamaの起動を待つ
        if not self.wait_for_ollama():
            return False
        
        # 2. 記憶データを読み込む
        memory_data = self.load_memory_summary()
        conversations = self.load_recent_conversations()
        
        # 3. コンテキストを作成
        context = self.create_memory_context(memory_data, conversations)
        
        if not context.strip():
            logger.info("📝 No memory data found, starting fresh")
            return True
        
        # 4. モデルをウォームアップ
        success = self.warm_up_model_with_memory(context)
        
        if success:
            logger.info("🎉 Memory loading completed successfully")
            logger.info("🧠 AI now has access to previous conversations and user preferences")
        else:
            logger.error("❌ Memory loading failed")
        
        return success

def main():
    """メイン処理"""
    logger.info("🧠 Memory Loader Starting...")
    
    loader = MemoryLoader()
    
    try:
        success = loader.load_and_apply_memory()
        if success:
            logger.info("🎉 Memory loading completed")
            return 0
        else:
            logger.error("❌ Memory loading failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("👋 Memory loading interrupted")
        return 0
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
