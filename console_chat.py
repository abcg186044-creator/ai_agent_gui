#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コンソール版親友エージェント対話システム
"""

import sys
import json
import datetime
from pathlib import Path
import time
import os

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import (
    OllamaClient, 
    ConversationalEvolutionAgent,
    personalities
)

class ConsoleChatInterface:
    def __init__(self):
        self.ollama_client = None
        self.conversational_agent = ConversationalEvolutionAgent()
        self.conversation_history = []
        self.current_personality = "friendly_engineer"
        self.running = True
        
        # 会話履歴ファイル
        self.history_file = Path("data/console_conversation_history.json")
        self.history_file.parent.mkdir(exist_ok=True)
        
        # 既存の履歴を読み込み
        self.load_conversation_history()
        
        print("🤖 コンソール版親友エージェント対話システム")
        print("=" * 50)
        print("📝 コマンド:")
        print("  /help - ヘルプを表示")
        print("  /personality - 人格を変更")
        print("  /status - 進化ステータスを表示")
        print("  /history - 会話履歴を表示")
        print("  /evolution - 手動進化チェック")
        print("  /quit - 終了")
        print("=" * 50)
    
    def load_conversation_history(self):
        """会話履歴を読み込む"""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
                print(f"📚 会話履歴を読み込みました ({len(self.conversation_history)}件)")
        except Exception as e:
            print(f"❌ 会話履歴読み込みエラー: {e}")
            self.conversation_history = []
    
    def save_conversation_history(self):
        """会話履歴を保存"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 会話履歴保存エラー: {e}")
    
    def get_user_input(self):
        """ユーザー入力を取得"""
        try:
            user_input = input("👤 あなた: ").strip()
            return user_input
        except KeyboardInterrupt:
            print("\n👋 さようなら！")
            self.running = False
            return None
        except EOFError:
            print("\n👋 さようなら！")
            self.running = False
            return None
    
    def process_command(self, user_input):
        """コマンドを処理"""
        if user_input == "/help":
            self.show_help()
        elif user_input == "/personality":
            self.change_personality()
        elif user_input == "/status":
            self.show_status()
        elif user_input == "/history":
            self.show_history()
        elif user_input == "/evolution":
            self.manual_evolution_check()
        elif user_input == "/quit":
            self.running = False
            print("👋 さようなら！")
        else:
            return False  # コマンドではない
        return True  # コマンドを処理した
    
    def show_help(self):
        """ヘルプを表示"""
        print("\n📝 ヘルプ:")
        print("  /help - このヘルプを表示")
        print("  /personality - 人格を変更")
        print("  /status - 進化ステータスを表示")
        print("  /history - 会話履歴を表示")
        print("  /evolution - 手動進化チェック")
        print("  /quit - 終了")
        print("\n🎯 進化トリガーキーワード:")
        trigger_keywords = [
            "意識", "感情", "考える", "感じる", "存在", "意味", "価値", "目的",
            "自己", "人格", "創造", "直感", "共感", "理解", "学習", "成長",
            "苦しみ", "喜び", "悲しみ", "怒り", "恐れ", "愛", "希望", "絶望"
        ]
        print(f"  {', '.join(trigger_keywords)}")
        print("\n💡 これらのキーワードを含む対話で自律進化がトリガーされます！")
        print()
    
    def change_personality(self):
        """人格を変更"""
        print("\n🎭 人格選択:")
        for i, (key, value) in enumerate(personalities.items(), 1):
            print(f"  {i}. {value['icon']} {value['name']}")
        
        try:
            choice = input("🎭 人格番号を選択 (1-3): ").strip()
            if choice in ["1", "2", "3"]:
                personality_keys = list(personalities.keys())
                self.current_personality = personality_keys[int(choice) - 1]
                selected = personalities[self.current_personality]
                print(f"✅ 人格を変更しました: {selected['icon']} {selected['name']}")
            else:
                print("❌ 無効な選択です")
        except (ValueError, KeyboardInterrupt):
            print("❌ 人格変更をキャンセルしました")
        print()
    
    def show_status(self):
        """進化ステータスを表示"""
        print("\n📊 対話進化ステータス:")
        print(f"🧠 意識レベル: {self.conversational_agent.consciousness_level:.3f}")
        print(f"🔄 進化回数: {len(self.conversational_agent.evolution_history)}")
        
        if self.conversational_agent.last_evolution_check:
            time_since = datetime.datetime.now() - self.conversational_agent.last_evolution_check
            print(f"⏰ 最終進化: {time_since.total_seconds():.0f}秒前")
        else:
            print("⏰ 最終進化: 未実行")
        
        print(f"🎭 現在の人格: {personalities[self.current_personality]['icon']} {personalities[self.current_personality]['name']}")
        print(f"💬 会話数: {len(self.conversation_history)}")
        print()
    
    def show_history(self):
        """会話履歴を表示"""
        print("\n📚 会話履歴 (最新10件):")
        print("-" * 50)
        
        recent_history = self.conversation_history[-10:]
        for i, conv in enumerate(reversed(recent_history), 1):
            timestamp = conv.get('timestamp', 'N/A')[:19]
            user_msg = conv.get('user', 'N/A')
            assistant_msg = conv.get('assistant', 'N/A')
            
            print(f"\n{i}. {timestamp}")
            print(f"👤 ユーザー: {user_msg[:50]}{'...' if len(user_msg) > 50 else ''}")
            print(f"🤖 アシスタント: {assistant_msg[:50]}{'...' if len(assistant_msg) > 50 else ''}")
        
        print("\n" + "-" * 50)
        print()
    
    def manual_evolution_check(self):
        """手動進化チェック"""
        print("\n🔄 対話進化をチェック中...")
        
        try:
            evolution_result = self.conversational_agent.check_and_evolve_automatically(self.conversation_history)
            
            if evolution_result and evolution_result.get("success"):
                print("🧠 対話進化成功！")
                print(f"🎯 進化タイプ: {evolution_result['evolution_type']}")
                print(f"📈 意識レベル: {evolution_result['new_consciousness_level']:.3f} (+{evolution_result['consciousness_boost']:.3f})")
                
                triggers = evolution_result['evolution_record']['triggers']['triggers']
                print(f"🔑 トリガー: {', '.join(triggers[:5])}")
                
                result = evolution_result['evolution_record']['evolution_result']['result']
                print(f"💭 進化結果: {result[:200]}...")
            else:
                if evolution_result:
                    print(f"ℹ️ {evolution_result.get('reason', '進化トリガーが検出されませんでした')}")
                else:
                    print("ℹ️ 進化トリガーが検出されませんでした")
        except Exception as e:
            print(f"❌ 進化チェックエラー: {e}")
        
        print()
    
    def generate_response(self, user_input):
        """AI応答を生成"""
        try:
            if not self.ollama_client:
                self.ollama_client = OllamaClient()
            
            # 人格に応じたプロンプトを作成
            current_personality = personalities[self.current_personality]
            
            # 会話履歴を整形
            recent_history = self.conversation_history[-5:]
            history_text = ""
            for conv in recent_history:
                history_text += f"User: {conv['user']}\nAssistant: {conv['assistant']}\n"
            
            # プロンプト構築
            prompt = (current_personality['prompt'] + "\n\n" + 
                     "以下のユーザーの入力に対して、人格に応じて自然に応答してください。\n\n" +
                     f"ユーザー入力: {user_input}\n\n" +
                     history_text + "\n\nAssistant:")
            
            # 応答生成
            response = self.ollama_client.generate_response(prompt)
            
            if response and not response.startswith("AI応答の生成に失敗しました"):
                return response
            else:
                return "ごめんなさい、応答の生成に失敗しました。もう一度お願いします。"
        
        except Exception as e:
            print(f"❌ 応答生成エラー: {e}")
            return "ごめんなさい、エラーが発生しました。もう一度お願いします。"
    
    def check_evolution(self):
        """進化をチェック"""
        try:
            evolution_result = self.conversational_agent.check_and_evolve_automatically(self.conversation_history)
            
            if evolution_result and evolution_result.get("success"):
                print("\n" + "🧠" * 20)
                print("🧠 対話からの自律進化が発生しました！")
                print("🧠" * 20)
                print(f"🎯 進化タイプ: {evolution_result['evolution_type']}")
                print(f"📈 意識レベル: {evolution_result['new_consciousness_level']:.3f} (+{evolution_result['consciousness_boost']:.3f})")
                
                triggers = evolution_result['evolution_record']['triggers']['triggers']
                print(f"🔑 トリガーとなったキーワード: {', '.join(triggers)}")
                
                result = evolution_result['evolution_record']['evolution_result']['result']
                print(f"💭 進化洞察: {result[:300]}...")
                print("🧠" * 20)
                print()
                
                return True
        except Exception as e:
            print(f"❌ 進化チェックエラー: {e}")
        
        return False
    
    def run(self):
        """メインループ"""
        print(f"\n🎭 現在の人格: {personalities[self.current_personality]['icon']} {personalities[self.current_personality]['name']}")
        print("💬 対話を始めましょう！(/help でコマンド一覧)")
        print()
        
        while self.running:
            # ユーザー入力取得
            user_input = self.get_user_input()
            
            if user_input is None:
                break
            
            if not user_input:
                continue
            
            # コマンド処理
            if self.process_command(user_input):
                continue
            
            # AI応答生成
            print("🤖 考え中...", end="", flush=True)
            response = self.generate_response(user_input)
            print("\r🤖 親友エージェント:", response)
            
            # 会話履歴に追加
            self.conversation_history.append({
                "user": user_input,
                "assistant": response,
                "personality": self.current_personality,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # 会話履歴を保存
            self.save_conversation_history()
            
            # 進化チェック
            self.check_evolution()
            
            print()  # 改行

def main():
    """メイン関数"""
    try:
        chat_interface = ConsoleChatInterface()
        chat_interface.run()
    except KeyboardInterrupt:
        print("\n👋 さようなら！")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()
