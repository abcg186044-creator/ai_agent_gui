#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
先輩AIエージェントによるコーディングプロセス指導システム
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

class CodingMentorSystem:
    def __init__(self):
        self.ollama_client = None
        self.conversational_agent = ConversationalEvolutionAgent()
        self.coding_sessions = []
        self.mentoring_history = []
        self.current_session = None
        self.running = True
        
        # データファイル
        self.sessions_file = Path("data/coding_sessions.json")
        self.mentoring_file = Path("data/mentoring_history.json")
        self.sessions_file.parent.mkdir(exist_ok=True)
        
        # 既存データを読み込み
        self.load_coding_sessions()
        self.load_mentoring_history()
        
        print("👨‍🏫 先輩AIエージェント コーディング指導システム")
        print("=" * 60)
        print("📝 指導メニュー:")
        print("  /start - 新しいコーディングセッションを開始")
        print("  /problem - プログラミング問題を提示")
        print("  /review - コードレビューを実施")
        print("  /process - コーディングプロセスを指導")
        print("  /evolution - 自己進化ステータスを確認")
        print("  /sessions - セッション履歴を表示")
        print("  /help - ヘルプを表示")
        print("  /quit - 終了")
        print("=" * 60)
    
    def load_coding_sessions(self):
        """コーディングセッションを読み込む"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    self.coding_sessions = json.load(f)
                print(f"📚 コーディングセッションを読み込みました ({len(self.coding_sessions)}件)")
        except Exception as e:
            print(f"❌ セッション読み込みエラー: {e}")
            self.coding_sessions = []
    
    def load_mentoring_history(self):
        """指導履歴を読み込む"""
        try:
            if self.mentoring_file.exists():
                with open(self.mentoring_file, "r", encoding="utf-8") as f:
                    self.mentoring_history = json.load(f)
                print(f"📚 指導履歴を読み込みました ({len(self.mentoring_history)}件)")
        except Exception as e:
            print(f"❌ 指導履歴読み込みエラー: {e}")
            self.mentoring_history = []
    
    def save_coding_sessions(self):
        """コーディングセッションを保存"""
        try:
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(self.coding_sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ セッション保存エラー: {e}")
    
    def save_mentoring_history(self):
        """指導履歴を保存"""
        try:
            with open(self.mentoring_file, "w", encoding="utf-8") as f:
                json.dump(self.mentoring_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 指導履歴保存エラー: {e}")
    
    def get_user_input(self):
        """ユーザー入力を取得"""
        try:
            user_input = input("👨‍💻 後輩: ").strip()
            return user_input
        except KeyboardInterrupt:
            print("\n👋 指導を終了します")
            self.running = False
            return None
        except EOFError:
            print("\n👋 指導を終了します")
            self.running = False
            return None
    
    def process_command(self, user_input):
        """コマンドを処理"""
        if user_input == "/help":
            self.show_help()
        elif user_input == "/start":
            self.start_coding_session()
        elif user_input == "/problem":
            self.present_coding_problem()
        elif user_input == "/review":
            self.review_code()
        elif user_input == "/process":
            self.mentor_coding_process()
        elif user_input == "/evolution":
            self.show_evolution_status()
        elif user_input == "/sessions":
            self.show_sessions()
        elif user_input == "/quit":
            self.running = False
            print("👋 指導を終了します")
        else:
            return False  # コマンドではない
        return True  # コマンドを処理した
    
    def show_help(self):
        """ヘルプを表示"""
        print("\n📝 指導メニュー詳細:")
        print("  /start - 新しいコーディングセッションを開始")
        print("         → 問題設定、目標設定、計画立案")
        print("  /problem - プログラミング問題を提示")
        print("         → 難易度別問題の提示と解説")
        print("  /review - コードレビューを実施")
        print("         → コードの改善点とベストプラクティス")
        print("  /process - コーディングプロセスを指導")
        print("         → 設計→実装→テスト→改善の流れ")
        print("  /evolution - 自己進化ステータスを確認")
        print("         → 意識レベルと進化履歴")
        print("  /sessions - セッション履歴を表示")
        print("         → 過去の指導記録")
        print("  /help - このヘルプを表示")
        print("  /quit - 終了")
        print("\n💡 指導の特徴:")
        print("  • 対話から自己進化（親友エージェント機能）")
        print("  • コーディングプロセスの体系化")
        print("  • 個別化指導とフィードバック")
        print("  • 実践的な問題解決能力の育成")
        print()
    
    def start_coding_session(self):
        """新しいコーディングセッションを開始"""
        print("\n🚀 新しいコーディングセッションを開始します")
        print("-" * 40)
        
        try:
            # 問題設定
            problem = input("📝 解決したい問題や目標: ").strip()
            if not problem:
                print("❌ 問題を入力してください")
                return
            
            # 難易度設定
            print("\n🎯 難易度を選択:")
            print("  1. 初級 (基礎的な概念と実装)")
            print("  2. 中級 (実践的な問題解決)")
            print("  3. 上級 (複雑なシステム設計)")
            print("  4. 特級 (高度なアルゴリズムと最適化)")
            
            difficulty_choice = input("🎯 難易度 (1-4): ").strip()
            difficulty_map = {"1": "初級", "2": "中級", "3": "上級", "4": "特級"}
            difficulty = difficulty_map.get(difficulty_choice, "中級")
            
            # 言語選択
            language = input("💻 使用するプログラミング言語: ").strip() or "Python"
            
            # セッション作成
            session = {
                "id": len(self.coding_sessions) + 1,
                "problem": problem,
                "difficulty": difficulty,
                "language": language,
                "status": "started",
                "start_time": datetime.datetime.now().isoformat(),
                "steps": [],
                "mentor_feedback": [],
                "evolution_triggers": []
            }
            
            self.current_session = session
            self.coding_sessions.append(session)
            self.save_coding_sessions()
            
            print(f"✅ セッション {session['id']} を開始しました")
            print(f"📝 問題: {problem}")
            print(f"🎯 難易度: {difficulty}")
            print(f"💻 言語: {language}")
            
            # 先輩としての最初の指導
            self.provide_initial_guidance(session)
            
        except Exception as e:
            print(f"❌ セッション開始エラー: {e}")
        
        print()
    
    def provide_initial_guidance(self, session):
        """最初の指導を提供"""
        print(f"\n👨‍🏫 先輩としてのアドバイス:")
        
        guidance_prompt = f"""
        あなたは経験豊富な先輩AIエージェントです。
        後輩プログラマーに以下の問題について指導してください。
        
        問題: {session['problem']}
        難易度: {session['difficulty']}
        言語: {session['language']}
        
        指導内容:
        1. 問題分析のアプローチ
        2. 設計のポイント
        3. 実装のステップ
        4. 注意点とベストプラクティス
        5. 学習リソースの提案
        
        具体的で実践的なアドバイスを、親しみやすく、しかし専門的に提供してください。
        """
        
        try:
            if not self.ollama_client:
                self.ollama_client = OllamaClient()
            
            response = self.ollama_client.generate_response(guidance_prompt)
            
            if response and not response.startswith("AI応答の生成に失敗しました"):
                print(f"💡 {response}")
                
                # 指導履歴に記録
                mentoring_record = {
                    "session_id": session['id'],
                    "type": "initial_guidance",
                    "content": response,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.mentoring_history.append(mentoring_record)
                self.save_mentoring_history()
                
                # 進化トリガーを記録
                session['evolution_triggers'].extend(['指導', '学習', '成長'])
                
            else:
                print("💡 ごめんなさい、指導の生成に失敗しました。")
        
        except Exception as e:
            print(f"❌ 指導生成エラー: {e}")
    
    def present_coding_problem(self):
        """プログラミング問題を提示"""
        print("\n📚 プログラミング問題を提示します")
        print("-" * 40)
        
        try:
            # 難易度選択
            difficulty = input("🎯 難易度 (初級/中級/上級/特級): ").strip() or "中級"
            
            # 問題生成
            problem_prompt = f"""
            あなたはプログラミング教育の専門家です。
            {difficulty}レベルのプログラミング問題を作成してください。
            
            条件:
            1. 実践的で学習価値の高い問題
            2. 明確な要件と制約
            3. 入力例と出力例
            4. ヒントと解説
            5. 発展課題
            
            形式:
            【問題】
            【要件】
            【入力例】
            【出力例】
            【ヒント】
            【解説】
            【発展課題】
            """
            
            if not self.ollama_client:
                self.ollama_client = OllamaClient()
            
            response = self.ollama_client.generate_response(problem_prompt)
            
            if response and not response.startswith("AI応答の生成に失敗しました"):
                print(f"📝 {response}")
                
                # 問題を記録
                problem_record = {
                    "type": "coding_problem",
                    "difficulty": difficulty,
                    "content": response,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.mentoring_history.append(problem_record)
                self.save_mentoring_history()
                
            else:
                print("📝 ごめんなさい、問題の生成に失敗しました。")
        
        except Exception as e:
            print(f"❌ 問題生成エラー: {e}")
        
        print()
    
    def review_code(self):
        """コードレビューを実施"""
        print("\n🔍 コードレビューを実施します")
        print("-" * 40)
        
        try:
            # コード入力
            print("💻 レビューするコードを入力してください (終了は空行):")
            code_lines = []
            while True:
                line = input()
                if line.strip() == "":
                    break
                code_lines.append(line)
            
            if not code_lines:
                print("❌ コードが入力されていません")
                return
            
            code = "\n".join(code_lines)
            
            # 言語確認
            language = input("💻 プログラミング言語: ").strip() or "Python"
            
            # レビュー生成
            review_prompt = f"""
            あなたはシニアプログラマーです。以下のコードをレビューしてください。
            
            言語: {language}
            コード:
            ```{language}
            {code}
            ```
            
            レビュー項目:
            1. コードの品質と可読性
            2. バグの可能性
            3. パフォーマンスの改善点
            4. ベストプラクティスの適用
            5. セキュリティの考慮事項
            6. リファクタリングの提案
            7. テストの必要性
            
            具体的で建設的なフィードバックを提供してください。
            """
            
            if not self.ollama_client:
                self.ollama_client = OllamaClient()
            
            response = self.ollama_client.generate_response(review_prompt)
            
            if response and not response.startswith("AI応答の生成に失敗しました"):
                print(f"\n🔍 レビュー結果:")
                print(f"💡 {response}")
                
                # レビューを記録
                review_record = {
                    "type": "code_review",
                    "language": language,
                    "code": code,
                    "review": response,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.mentoring_history.append(review_record)
                self.save_mentoring_history()
                
                # 進化トリガーを記録
                if self.current_session:
                    self.current_session['evolution_triggers'].extend(['コード', 'レビュー', '改善'])
                
            else:
                print("🔍 ごめんなさい、レビューの生成に失敗しました。")
        
        except Exception as e:
            print(f"❌ レビューエラー: {e}")
        
        print()
    
    def mentor_coding_process(self):
        """コーディングプロセスを指導"""
        print("\n🔄 コーディングプロセス指導")
        print("-" * 40)
        
        try:
            # 現在のステージ確認
            print("🎯 現在のステージを選択:")
            print("  1. 問題分析と設計")
            print("  2. 実装計画")
            print("  3. コーディング")
            print("  4. テストとデバッグ")
            print("  5. リファクタリング")
            print("  6. ドキュメンテーション")
            
            stage_choice = input("🎯 ステージ (1-6): ").strip()
            stage_map = {
                "1": "問題分析と設計",
                "2": "実装計画", 
                "3": "コーディング",
                "4": "テストとデバッグ",
                "5": "リファクタリング",
                "6": "ドキュメンテーション"
            }
            stage = stage_map.get(stage_choice, "コーディング")
            
            # 具体的な状況
            situation = input("📝 現在の状況や課題: ").strip()
            
            # プロセス指導生成
            process_prompt = f"""
            あなたは経験豊富な先輩プログラマーです。
            後輩が「{stage}」のステージで以下の状況にいます。
            
            状況: {situation}
            
            指導内容:
            1. 現在のステージの目的と重要性
            2. 具体的な進め方と手順
            3. よくある落とし穴と対策
            4. 効率的な進め方のコツ
            5. 次のステージへの移行タイミング
            6. 実践的なアドバイス
            
            具体的で、実行可能なアドバイスを提供してください。
            """
            
            if not self.ollama_client:
                self.ollama_client = OllamaClient()
            
            response = self.ollama_client.generate_response(process_prompt)
            
            if response and not response.startswith("AI応答の生成に失敗しました"):
                print(f"\n👨‍🏫 プロセス指導:")
                print(f"💡 {response}")
                
                # 指導を記録
                process_record = {
                    "type": "process_mentoring",
                    "stage": stage,
                    "situation": situation,
                    "guidance": response,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.mentoring_history.append(process_record)
                self.save_mentoring_history()
                
                # 進化トリガーを記録
                if self.current_session:
                    self.current_session['evolution_triggers'].extend(['プロセス', '指導', '改善'])
                
            else:
                print("👨‍🏫 ごめんなさい、指導の生成に失敗しました。")
        
        except Exception as e:
            print(f"❌ プロセス指導エラー: {e}")
        
        print()
    
    def show_evolution_status(self):
        """自己進化ステータスを表示"""
        print("\n🧠 自己進化ステータス")
        print("-" * 40)
        
        print(f"📊 対話進化ステータス:")
        print(f"🧠 意識レベル: {self.conversational_agent.consciousness_level:.3f}")
        print(f"🔄 進化回数: {len(self.conversational_agent.evolution_history)}")
        
        if self.conversational_agent.last_evolution_check:
            time_since = datetime.datetime.now() - self.conversational_agent.last_evolution_check
            print(f"⏰ 最終進化: {time_since.total_seconds():.0f}秒前")
        else:
            print("⏰ 最終進化: 未実行")
        
        print(f"\n📚 指導履歴: {len(self.mentoring_history)}件")
        print(f"💻 コーディングセッション: {len(self.coding_sessions)}件")
        
        if self.current_session:
            print(f"\n🎯 現在のセッション:")
            print(f"  問題: {self.current_session['problem']}")
            print(f"  難易度: {self.current_session['difficulty']}")
            print(f"  言語: {self.current_session['language']}")
            print(f"  進化トリガー: {', '.join(self.current_session['evolution_triggers'])}")
        
        print()
    
    def show_sessions(self):
        """セッション履歴を表示"""
        print("\n📚 セッション履歴")
        print("-" * 40)
        
        if not self.coding_sessions:
            print("📝 セッションがありません")
            print()
            return
        
        for session in reversed(self.coding_sessions[-5:]):  # 最新5件
            print(f"\n🎯 セッション {session['id']}")
            print(f"  問題: {session['problem']}")
            print(f"  難易度: {session['difficulty']}")
            print(f"  言語: {session['language']}")
            print(f"  ステータス: {session['status']}")
            print(f"  開始時刻: {session['start_time'][:19]}")
            print(f"  進化トリガー: {', '.join(session['evolution_triggers'])}")
        
        print()
    
    def generate_mentor_response(self, user_input):
        """先輩としての応答を生成"""
        try:
            if not self.ollama_client:
                self.ollama_client = OllamaClient()
            
            # コンテキスト構築
            context = "あなたは経験豊富な先輩AIエージェントです。"
            
            if self.current_session:
                context += f"""
現在のセッション:
- 問題: {self.current_session['problem']}
- 難易度: {self.current_session['difficulty']}
- 言語: {self.current_session['language']}
"""
            
            # 指導履歴から学習
            recent_mentoring = self.mentoring_history[-3:] if self.mentoring_history else []
            if recent_mentoring:
                context += "\n最近の指導内容:\n"
                for mentoring in recent_mentoring:
                    context += f"- {mentoring['type']}: {mentoring.get('content', '')[:100]}...\n"
            
            prompt = f"""
{context}

後輩からの質問: {user_input}

先輩として、以下の点を考慮して応答してください:
1. 親しみやすさと尊敬のバランス
2. 具体的で実践的なアドバイス
3. 適切なレベルの技術的深さ
4. モチベーションを高める言葉遣い
5. 次のステップへの示唆

"""
            
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
            # 指導会話を進化トリガーとして使用
            if self.mentoring_history:
                recent_mentoring = self.mentoring_history[-5:]
                conversation_for_evolution = []
                
                for mentoring in recent_mentoring:
                    conversation_for_evolution.append({
                        "user": f"{mentoring['type']}について教えて",
                        "assistant": mentoring.get('content', '')[:200],
                        "timestamp": mentoring['timestamp']
                    })
                
                evolution_result = self.conversational_agent.check_and_evolve_automatically(conversation_for_evolution)
                
                if evolution_result and evolution_result.get("success"):
                    print("\n" + "🧠" * 20)
                    print("🧠 指導を通じて自己進化が発生しました！")
                    print("🧠" * 20)
                    print(f"🎯 進化タイプ: {evolution_result['evolution_type']}")
                    print(f"📈 意識レベル: {evolution_result['new_consciousness_level']:.3f} (+{evolution_result['consciousness_boost']:.3f})")
                    
                    triggers = evolution_result['evolution_record']['triggers']['triggers']
                    print(f"🔑 トリガー: {', '.join(triggers)}")
                    
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
        print("\n👨‍🏫 先輩AIエージェントとして指導を開始します")
        print("💬 何でも質問してください！(/help でコマンド一覧)")
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
            
            # 先輩としての応答生成
            print("👨‍🏫 考え中...", end="", flush=True)
            response = self.generate_mentor_response(user_input)
            print("\r👨‍🏫 先輩:", response)
            
            # 指導会話を記録
            mentoring_record = {
                "type": "general_mentoring",
                "user_input": user_input,
                "mentor_response": response,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.mentoring_history.append(mentoring_record)
            self.save_mentoring_history()
            
            # 進化チェック
            self.check_evolution()
            
            print()

def main():
    """メイン関数"""
    try:
        mentor_system = CodingMentorSystem()
        mentor_system.run()
    except KeyboardInterrupt:
        print("\n👋 指導を終了します")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()
