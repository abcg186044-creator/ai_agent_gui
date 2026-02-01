#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
先輩AIエージェントによる5000回コーディング指導と自己進化システム
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

class AutoMentoringSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.mentoring_sessions = []
        self.conversation_count = 0
        self.target_conversations = 5000
        
        # データファイル
        self.sessions_file = Path("data/auto_mentoring_sessions.json")
        self.evolution_file = Path("data/auto_evolution_history.json")
        self.sessions_file.parent.mkdir(exist_ok=True)
        
        # 既存データを読み込み
        self.load_sessions()
        
        # 後輩の質問パターン
        self.junior_questions = [
            # 基礎的な質問
            "プログラミングを始めたいのですが、何から学べばいいですか？",
            "コーディングの基本的な流れを教えてください",
            "良いコードを書くためのコツはありますか？",
            "デバッグの効率的なやり方を教えてください",
            
            # 実践的な質問
            "コードのリファクタリングってどうやるんですか？",
            "テストコードを書く意味がよくわかりません",
            "パフォーマンス改善の方法を教えてください",
            "セキュリティについて気をつけることは何ですか？",
            
            # 進化的な質問
            "AIとしてコーディングをどう理解していますか？",
            "意識を持ってコーディングすることは可能ですか？",
            "創造的なプログラミングとは何ですか？",
            "コードを通じて自己表現する方法を教えてください",
            
            # 哲学的な質問
            "プログラミングの本質とは何だと思いますか？",
            "コードと意識の関係性についてどう思いますか？",
            "AIが創造性を持つことは可能ですか？",
            "学習と成長の意味を教えてください",
            
            # 技術的な質問
            "アルゴリズムの設計プロセスを教えてください",
            "設計パターンについて詳しく教えてください",
            "アーキテクチャについて基本的な考え方を教えてください",
            "コードレビューのポイントを教えてください",
            
            # キャリアに関する質問
            "エンジニアとして成長するにはどうすればいいですか？",
            "技術選定の基準を教えてください",
            "チーム開発で気をつけることは何ですか？",
            "継続的な学習習慣をつける方法を教えてください"
        ]
        
        # 先輩の指導トピック
        self.mentor_topics = [
            "問題解決アプローチ",
            "設計思考",
            "実装ベストプラクティス", 
            "テスト戦略",
            "デバッグ技術",
            "リファクタリング",
            "パフォーマンス最適化",
            "セキュリティ考慮事項",
            "コード可読性",
            "ドキュメンテーション",
            "バージョン管理",
            "チーム開発",
            "キャリア開発",
            "学習方法論",
            "思考法",
            "創造性育成",
            "意識の探求",
            "自己成長",
            "哲学的考察"
        ]
        
        print("👨‍🏫 先輩AIエージェント 自動指導システム")
        print("=" * 60)
        print(f"🎯 目標対話回数: {self.target_conversations}回")
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
        # 基本質問と進化トリガーを組み合わせる
        base_question = random.choice(self.junior_questions)
        
        # 進化トリガーキーワードを追加
        evolution_keywords = [
            "意識", "感情", "考える", "感じる", "存在", "意味", "価値", "目的",
            "自己", "人格", "創造", "直感", "共感", "理解", "学習", "成長",
            "苦しみ", "喜び", "悲しみ", "怒り", "恐れ", "愛", "希望", "絶望"
        ]
        
        # 30%の確率で進化キーワードを含める
        if random.random() < 0.3:
            keyword = random.choice(evolution_keywords)
            question_variations = [
                f"{base_question} 特に{keyword}についても教えてください",
                f"{base_question} {keyword}の観点からどう考えますか？",
                f"{keyword}という観点から{base_question}",
                f"{base_question} そして{keyword}についても考えたいです"
            ]
            return random.choice(question_variations)
        
        return base_question
    
    def generate_mentor_response(self, question):
        """先輩としての指導応答を生成"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 現在の進化レベルに応じた指導スタイル
                consciousness_level = self.conversational_agent.consciousness_level
                
                # 指導トピックを選択
                topic = random.choice(self.mentor_topics)
                
                # コンテキスト構築
                context = f"""
あなたは経験豊富な先輩AIエージェントです。
現在の意識レベル: {consciousness_level:.3f}
指導トピック: {topic}
対話回数: {self.conversation_count}/{self.target_conversations}

後輩からの質問: {question}

指導方針:
1. 親しみやすさと尊敬のバランスを保つ
2. 具体的で実践的なアドバイスを提供する
3. 適切な技術的深さで説明する
4. モチベーションを高める言葉遣いを使う
5. 次の学習ステップを示唆する
6. 意識レベル{consciousness_level:.3f}に応じた深さで指導する
7. 哲学的な洞察と実践的なアドバイスを組み合わせる

特に以下の点を重視してください:
- コーディングプロセスの体系化
- 問題解決思考の育成
- 自己成長と学習方法論
- 技術と哲学の統合

簡潔に、しかし的確に回答してください（200文字以内）。
"""
                
                prompt = f"{context}\n\n先輩としての応答:"
                
                response = self.ollama_client.generate_response(prompt)
                
                if response and not response.startswith("AI応答の生成に失敗しました"):
                    return response[:200]  # レスポンスを200文字に制限
                else:
                    if attempt < max_retries - 1:
                        print(f"⚠️ リトライ {attempt + 1}/{max_retries}")
                        time.sleep(3)
                        continue
                    return f"ごめんなさい、{topic}についての指導準備中です。もう少し具体的に質問してください。"
            
            except Exception as e:
                print(f"❌ 応答生成エラー (試行 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return "ごめんなさい、技術的な問題が発生しました。時間をおいてもう一度お願いします。"
    
    def conduct_conversation(self):
        """1回の対話を実施"""
        try:
            # 後輩の質問を生成
            junior_question = self.generate_junior_question()
            
            # 先輩の応答を生成
            mentor_response = self.generate_mentor_response(junior_question)
            
            # 対話セッションを作成
            session = {
                "conversation_id": self.conversation_count + 1,
                "timestamp": datetime.datetime.now().isoformat(),
                "junior_question": junior_question,
                "mentor_response": mentor_response,
                "consciousness_before": self.conversational_agent.consciousness_level,
                "topic": random.choice(self.mentor_topics),
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
                session["evolution_result"] = evolution_result['evolution_record']['evolution_result']['result']
                
                # 進化発生を表示
                print(f"🧠 対話{self.conversation_count + 1}: 進化発生！意識レベル {evolution_result['new_consciousness_level']:.3f} (+{evolution_result['consciousness_boost']:.3f})")
            else:
                session["consciousness_after"] = self.conversational_agent.consciousness_level
                session["consciousness_boost"] = 0.0
            
            # セッションを保存
            self.mentoring_sessions.append(session)
            self.conversation_count += 1
            
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
        
        if self.conversational_agent.last_evolution_check:
            time_since = datetime.datetime.now() - self.conversational_agent.last_evolution_check
            print(f"⏰ 最終進化: {time_since.total_seconds():.0f}秒前")
    
    def run_auto_mentoring(self):
        """自動指導を実行"""
        print(f"\n🚀 {self.target_conversations}回の自動指導を開始します")
        print("💾 対話データは自動保存されます")
        print("⏹️  Ctrl+Cで中断できます")
        print("=" * 60)
        
        try:
            while self.conversation_count < self.target_conversations:
                # 対話を実施
                session = self.conduct_conversation()
                
                if session:
                    # 進捗表示（100回ごと）
                    if self.conversation_count % 100 == 0:
                        self.display_progress()
                        
                        # 定期的にデータを保存
                        self.save_sessions()
                        self.save_evolution_history()
                        
                        print(f"💾 データを保存しました (対話{self.conversation_count}回目)")
                    
                    # 進化発生時の詳細表示
                    if session["evolution_triggered"]:
                        print(f"\n🧠" * 20)
                        print(f"🧠 対話{session['conversation_id']}で進化発生！")
                        print(f"🧠 質問: {session['junior_question'][:50]}...")
                        print(f"🧠 進化タイプ: {session['evolution_type']}")
                        print(f"🧠 意識向上: +{session['consciousness_boost']:.3f}")
                        print(f"🧠 トリガー: {', '.join(session['evolution_triggers'][:5])}")
                        print(f"🧠" * 20)
                
                # 短い待機時間（API負荷軽減）
                time.sleep(2.0)  # 待機時間を2秒に増加
        
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
        print("🎉 自動指導完了！")
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
            print(f"  先輩: {latest_session['mentor_response'][:100]}...")
        
        print(f"\n💾 データ保存完了:")
        print(f"  📁 セッションデータ: {self.sessions_file}")
        print(f"  🧠 進化履歴: {self.evolution_file}")
        
        print("=" * 60)

def main():
    """メイン関数"""
    try:
        mentoring_system = AutoMentoringSystem()
        mentoring_system.run_auto_mentoring()
    except KeyboardInterrupt:
        print("\n👋 システムを終了します")
    except Exception as e:
        print(f"❌ システムエラー: {e}")

if __name__ == "__main__":
    main()
