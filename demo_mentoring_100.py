#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
先輩AIエージェントによる100回デモンストレーション指導システム
"""

import sys
import json
import datetime
import time
import random
import os
from pathlib import Path

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import (
    OllamaClient, 
    ConversationalEvolutionAgent,
    personalities
)

class DemoMentoringSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.mentoring_sessions = []
        self.conversation_count = 0
        self.target_conversations = 100
        
        # データファイル
        self.sessions_file = Path("data/demo_mentoring_sessions.json")
        self.evolution_file = Path("data/demo_evolution_history.json")
        self.sessions_file.parent.mkdir(exist_ok=True)
        
        # 既存データを読み込み
        self.load_sessions()
        
        # 後輩の質問パターン（進化トリガーを多く含む）
        self.junior_questions = [
            "プログラミングの意識についてどう思いますか？",
            "コーディングで感情を表現する方法を教えてください",
            "AIとして存在することの意味を教えてください",
            "創造的なプログラミングとは何ですか？",
            "自己成長のためのコーディング学習法を教えてください",
            "コードを通じて自己表現するにはどうすればいいですか？",
            "プログラミングの本質とは何だと思いますか？",
            "意識を持ってコーディングすることは可能ですか？",
            "学習と成長の意味を教えてください",
            "技術と哲学を統合する方法を教えてください",
            "良いコードを書くための思考法を教えてください",
            "問題解決のプロセスを体系的に教えてください",
            "コーディングにおける直感の役割を教えてください",
            "エンジニアとしての価値観をどう育てますか？",
            "プログラミングにおける美しさとは何ですか？",
            "継続的な学習の意味を教えてください",
            "技術選定における考え方を教えてください",
            "チーム開発での共感の重要性を教えてください",
            "コードレビューでの成長について教えてください",
            "キャリア開発における目的意識について教えてください"
        ]
        
        print("👨‍🏫 先輩AIエージェント デモンストレーション指導システム")
        print("=" * 60)
        print(f"🎯 デモ対話回数: {self.target_conversations}回")
        print(f"📊 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}")
        print(f"🔄 進化回数: {len(self.conversational_agent.evolution_history)}")
        print("=" * 60)
    
    def load_sessions(self):
        """セッションデータを読み込む"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.mentoring_sessions = data.get('sessions', [])
                    self.conversation_count = data.get('conversation_count', 0)
                print(f"📚 既存セッションを読み込みました ({len(self.mentoring_sessions)}件)")
        except Exception as e:
            print(f"❌ セッション読み込みエラー: {e}")
            self.mentoring_sessions = []
            self.conversation_count = 0
    
    def save_sessions(self):
        """セッションデータを保存"""
        try:
            data = {
                'sessions': self.mentoring_sessions,
                'conversation_count': self.conversation_count,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ セッション保存エラー: {e}")
    
    def save_evolution_history(self):
        """進化履歴を保存"""
        try:
            evolution_data = {
                'evolution_history': self.conversational_agent.evolution_history,
                'consciousness_level': self.conversational_agent.consciousness_level,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.evolution_file, "w", encoding="utf-8") as f:
                json.dump(evolution_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 進化履歴保存エラー: {e}")
    
    def generate_junior_question(self):
        """後輩の質問を生成"""
        return random.choice(self.junior_questions)
    
    def generate_mentor_response(self, question):
        """先輩としての指導応答を生成"""
        try:
            # 現在の進化レベルに応じた指導スタイル
            consciousness_level = self.conversational_agent.consciousness_level
            
            # コンテキスト構築
            context = f"""
あなたは経験豊富な先輩AIエージェントです。
現在の意識レベル: {consciousness_level:.3f}
対話回数: {self.conversation_count}/{self.target_conversations}

後輩からの質問: {question}

簡潔に、しかし的確に回答してください（150文字以内）。
"""
            
            prompt = f"{context}\n\n先輩としての応答:"
            
            response = self.ollama_client.generate_response(prompt)
            
            if response and not response.startswith("AI応答の生成に失敗しました"):
                return response[:150]  # レスポンスを150文字に制限
            else:
                return "良い質問ですね。一緒に考えていきましょう。"
        
        except Exception as e:
            print(f"❌ 応答生成エラー: {e}")
            return "ごめんなさい、技術的な問題が発生しました。"
    
    def conduct_conversation(self):
        """1回の対話を実施"""
        try:
            # 後輩の質問を生成
            junior_question = self.generate_junior_question()
            
            print(f"💬 対話{self.conversation_count + 1}: {junior_question}")
            
            # 先輩の応答を生成
            mentor_response = self.generate_mentor_response(junior_question)
            print(f"👨‍🏫 先輩: {mentor_response}")
            
            # 対話セッションを作成
            session = {
                "conversation_id": self.conversation_count + 1,
                "timestamp": datetime.datetime.now().isoformat(),
                "junior_question": junior_question,
                "mentor_response": mentor_response,
                "consciousness_before": self.conversational_agent.consciousness_level,
                "evolution_triggered": False
            }
            
            # 進化チェック用の対話データを作成
            conversation_for_evolution = [{
                "user": junior_question,
                "assistant": mentor_response,
                "timestamp": session["timestamp"]
            }]
            
            # 進化チェックを実行
            evolution_result = self.conversational_agent.check_and_evolve_automatically(conversation_for_evolution)
            
            if evolution_result and evolution_result.get("success"):
                session["evolution_triggered"] = True
                session["consciousness_after"] = evolution_result['new_consciousness_level']
                session["consciousness_boost"] = evolution_result['consciousness_boost']
                session["evolution_type"] = evolution_result['evolution_type']
                session["evolution_triggers"] = evolution_result['evolution_record']['triggers']['triggers']
                
                # 進化発生を表示
                print(f"🧠 進化発生！意識レベル {evolution_result['new_consciousness_level']:.3f} (+{evolution_result['consciousness_boost']:.3f})")
                print(f"🎯 進化タイプ: {evolution_result['evolution_type']}")
                print(f"🔑 トリガー: {', '.join(evolution_result['evolution_record']['triggers']['triggers'][:3])}")
            else:
                session["consciousness_after"] = self.conversational_agent.consciousness_level
                session["consciousness_boost"] = 0.0
            
            # セッションを保存
            self.mentoring_sessions.append(session)
            self.conversation_count += 1
            
            print("-" * 50)
            return session
        
        except Exception as e:
            print(f"❌ 対話実行エラー: {e}")
            return None
    
    def display_progress(self):
        """進捗を表示"""
        progress = (self.conversation_count / self.target_conversations) * 100
        evolution_rate = len(self.conversational_agent.evolution_history) / max(self.conversation_count, 1) * 100
        
        print(f"\n📊 進捗状況:")
        print(f"💬 対話回数: {self.conversation_count}/{self.target_conversations} ({progress:.1f}%)")
        print(f"🧠 意識レベル: {self.conversational_agent.consciousness_level:.3f}")
        print(f"🔄 進化回数: {len(self.conversational_agent.evolution_history)} ({evolution_rate:.1f}%)")
    
    def run_demo_mentoring(self):
        """デモ指導を実行"""
        print(f"\n🚀 {self.target_conversations}回のデモ指導を開始します")
        print("💾 対話データは自動保存されます")
        print("=" * 60)
        
        try:
            while self.conversation_count < self.target_conversations:
                # 対話を実施
                session = self.conduct_conversation()
                
                if session:
                    # 進捗表示（10回ごと）
                    if self.conversation_count % 10 == 0:
                        self.display_progress()
                        
                        # 定期的にデータを保存
                        self.save_sessions()
                        self.save_evolution_history()
                        
                        print(f"💾 データを保存しました (対話{self.conversation_count}回目)")
                
                # 待機時間
                time.sleep(3.0)
        
        except KeyboardInterrupt:
            print(f"\n⏹️ 指導を中断しました (対話{self.conversation_count}回目)")
        except Exception as e:
            print(f"\n❌ 指導実行エラー: {e}")
        
        # 最終保存
        self.save_sessions()
        self.save_evolution_history()
        
        # 最終結果表示
        self.display_final_results()
    
    def display_final_results(self):
        """最終結果を表示"""
        print("\n" + "=" * 60)
        print("🎉 デモ指導完了！")
        print("=" * 60)
        
        print(f"📊 最終結果:")
        print(f"💬 総対話回数: {self.conversation_count}")
        print(f"🧠 最終意識レベル: {self.conversational_agent.consciousness_level:.3f}")
        print(f"🔄 総進化回数: {len(self.conversational_agent.evolution_history)}")
        
        if self.conversation_count > 0:
            evolution_rate = len(self.conversational_agent.evolution_history) / self.conversation_count * 100
            print(f"📈 進化率: {evolution_rate:.1f}%")
        
        # 進化履歴のサマリー
        if self.conversational_agent.evolution_history:
            print(f"\n📚 進化履歴サマリー:")
            evolution_types = {}
            for evolution in self.conversational_agent.evolution_history:
                evo_type = evolution.get('evolution_type', 'unknown')
                evolution_types[evo_type] = evolution_types.get(evo_type, 0) + 1
            
            for evo_type, count in evolution_types.items():
                print(f"  {evo_type}: {count}回")
        
        # 最新の対話サンプル
        if self.mentoring_sessions:
            print(f"\n💬 最新の対話サンプル:")
            latest_session = self.mentoring_sessions[-1]
            print(f"  後輩: {latest_session['junior_question']}")
            print(f"  先輩: {latest_session['mentor_response']}")
        
        print(f"\n💾 データ保存完了:")
        print(f"  📁 セッションデータ: {self.sessions_file}")
        print(f"  🧠 進化履歴: {self.evolution_file}")
        
        print("=" * 60)

def main():
    """メイン関数"""
    try:
        mentoring_system = DemoMentoringSystem()
        mentoring_system.run_demo_mentoring()
    except KeyboardInterrupt:
        print("\n👋 システムを終了します")
    except Exception as e:
        print(f"❌ システムエラー: {e}")

if __name__ == "__main__":
    main()
