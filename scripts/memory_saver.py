#!/usr/bin/env python3
"""
記憶保存スクリプト
会話内容を外部記憶データベースに保存
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import requests
import hashlib

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemorySaver:
    def __init__(self):
        self.chroma_path = os.getenv('CHROMA_DB_PATH', '/app/data/chroma')
        self.memory_path = os.path.join(self.chroma_path, 'memory')
        self.conversation_path = os.path.join(self.chroma_path, 'conversations')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        # 記憶ディレクトリの作成
        Path(self.memory_path).mkdir(parents=True, exist_ok=True)
        Path(self.conversation_path).mkdir(parents=True, exist_ok=True)
    
    def summarize_conversation(self, messages):
        """会話を要約する"""
        if not messages:
            return ""
        
        # 会話テキストを作成
        conversation_text = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in messages[-10:]  # 最新10メッセージ
        ])
        
        summary_prompt = f"""Please summarize the following conversation in 2-3 sentences, focusing on key topics and user preferences:

{conversation_text}

Summary:"""
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": summary_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "max_tokens": 150
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"❌ Failed to summarize conversation: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error summarizing conversation: {e}")
            return ""
    
    def extract_user_preferences(self, messages):
        """ユーザー設定を抽出"""
        preferences = {}
        
        # 簡単なキーワードベースの抽出
        preference_keywords = {
            'name': ['name is', 'call me', 'my name is'],
            'language': ['speak in', 'language', '日本語', 'english'],
            'style': ['formal', 'casual', 'friendly', 'professional'],
            'topics': ['interested in', 'like', 'prefer', 'enjoy']
        }
        
        conversation_text = " ".join([msg.get('content', '') for msg in messages])
        
        for pref_type, keywords in preference_keywords.items():
            for keyword in keywords:
                if keyword.lower() in conversation_text.lower():
                    # 簡単な抽出ロジック（実際はもっと複雑に）
                    preferences[pref_type] = f"Detected from keyword: {keyword}"
        
        return preferences
    
    def save_conversation(self, conversation_id, messages, title=None):
        """会話を保存"""
        if not messages:
            return False
        
        # 会話データの作成
        conversation_data = {
            'id': conversation_id,
            'title': title or f"Conversation {conversation_id}",
            'timestamp': datetime.now().isoformat(),
            'messages': messages,
            'summary': self.summarize_conversation(messages),
            'message_count': len(messages)
        }
        
        # ファイルに保存
        file_name = f"conversation_{conversation_id}.json"
        file_path = os.path.join(self.conversation_path, file_name)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Conversation saved: {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save conversation: {e}")
            return False
    
    def update_memory_summary(self, messages, preferences):
        """記憶の要約を更新"""
        memory_file = os.path.join(self.memory_path, 'memory_summary.json')
        
        # 既存の記憶を読み込む
        memory_data = {
            'user_preferences': {},
            'important_topics': [],
            'conversation_style': {},
            'last_updated': None
        }
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load existing memory: {e}")
        
        # ユーザー設定を更新
        if preferences:
            memory_data['user_preferences'].update(preferences)
            logger.info("📝 User preferences updated")
        
        # 重要なトピックを抽出
        if messages:
            summary = self.summarize_conversation(messages)
            if summary:
                # 簡単なトピック抽出
                topics = self.extract_topics_from_summary(summary)
                for topic in topics:
                    if topic not in memory_data['important_topics']:
                        memory_data['important_topics'].append(topic)
                
                # トピック数を制限
                memory_data['important_topics'] = memory_data['important_topics'][-20:]
        
        # 更新日時を記録
        memory_data['last_updated'] = datetime.now().isoformat()
        
        # 保存
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            logger.info("📝 Memory summary updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update memory summary: {e}")
            return False
    
    def extract_topics_from_summary(self, summary):
        """要約からトピックを抽出"""
        # 簡単なキーワードベースの抽出
        topics = []
        
        # 一般的なトピックキーワード
        topic_keywords = [
            'programming', 'code', 'development', 'software',
            'business', 'work', 'project',
            'learning', 'study', 'education',
            'health', 'fitness', 'exercise',
            'travel', 'vacation', 'trip',
            'food', 'cooking', 'recipe',
            'music', 'movie', 'book',
            'technology', 'AI', 'machine learning'
        ]
        
        summary_lower = summary.lower()
        
        for keyword in topic_keywords:
            if keyword in summary_lower:
                topics.append(keyword)
        
        return topics[:5]  # 最大5件
    
    def save_memory(self, conversation_id, messages, title=None):
        """記憶を保存するメイン処理"""
        logger.info(f"💾 Saving memory for conversation {conversation_id}...")
        
        # 1. 会話を保存
        if not self.save_conversation(conversation_id, messages, title):
            return False
        
        # 2. ユーザー設定を抽出
        preferences = self.extract_user_preferences(messages)
        
        # 3. 記憶の要約を更新
        if not self.update_memory_summary(messages, preferences):
            return False
        
        logger.info("🎉 Memory saving completed")
        return True

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        logger.error("Usage: python memory_saver.py <conversation_id> [title]")
        return 1
    
    conversation_id = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    # サンプルメッセージ（実際はStreamlitから渡す）
    sample_messages = [
        {"role": "user", "content": "Hello, my name is John and I prefer casual conversation"},
        {"role": "assistant", "content": "Hello John! I'll remember that you prefer casual conversation. How can I help you today?"},
        {"role": "user", "content": "I'm interested in learning about AI and machine learning"},
        {"role": "assistant", "content": "That's great! AI and machine learning are fascinating topics. What specific aspect would you like to explore?"}
    ]
    
    saver = MemorySaver()
    
    try:
        success = saver.save_memory(conversation_id, sample_messages, title)
        if success:
            logger.info("🎉 Memory saving completed")
            return 0
        else:
            logger.error("❌ Memory saving failed")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
