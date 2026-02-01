#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スクリーンショット分析・デバッグ・自己進化システム
"""

import sys
import json
import datetime
import os
import re
import base64
from pathlib import Path

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import OllamaClient, ConversationalEvolutionAgent

class ScreenDebugSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.debug_sessions = []
        self.debug_count = 0
        
        # データファイル
        self.sessions_file = Path("data/screen_debug_sessions.json")
        self.sessions_file.parent.mkdir(exist_ok=True)
        
        print("🔍 スクリーンショット分析・デバッグ・自己進化システム")
        print("=" * 60)
    
    def analyze_image_with_ai(self, image_path):
        """AIで画像を分析"""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            prompt = "このスクリーンショットを分析し、エラーと解決策を教えてください"
            
            response = self.ollama_client.generate_response(prompt)
            return response
        
        except Exception as e:
            return f"画像分析エラー: {e}"
    
    def debug_session(self, image_path):
        """デバッグセッションを実行"""
        print(f"🔍 画像分析中: {image_path}")
        
        analysis = self.analyze_image_with_ai(image_path)
        print(f"📊 分析結果: {analysis}")
        
        session = {
            "id": self.debug_count + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "image_path": str(image_path),
            "analysis": analysis,
            "consciousness_before": self.conversational_agent.consciousness_level
        }
        
        evolution_result = self.check_evolution(analysis)
        if evolution_result:
            session["evolution"] = evolution_result
        
        self.debug_sessions.append(session)
        self.debug_count += 1
        self.save_sessions()
        
        return session
    
    def check_evolution(self, analysis):
        """進化をチェック"""
        try:
            conversation = [{"user": "デバッグ分析", "assistant": analysis}]
            result = self.conversational_agent.check_and_evolve_automatically(conversation)
            
            if result and result.get("success"):
                print(f"🧠 進化発生！意識レベル: {result['new_consciousness_level']:.3f}")
                return result
        
        except Exception as e:
            print(f"❌ 進化チェックエラー: {e}")
        
        return None
    
    def save_sessions(self):
        """セッションを保存"""
        try:
            data = {
                'sessions': self.debug_sessions,
                'debug_count': self.debug_count,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存エラー: {e}")

def main():
    debug_system = ScreenDebugSystem()
    print("📸 スクリーンショットファイルパスを入力:")
    image_path = input("📁 パス: ").strip()
    
    if os.path.exists(image_path):
        debug_system.debug_session(image_path)
        print("✅ デバッグ完了")
    else:
        print("❌ ファイルが見つかりません")

if __name__ == "__main__":
    main()
