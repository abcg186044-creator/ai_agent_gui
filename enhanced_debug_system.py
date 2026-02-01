#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強化版スクリーンショット分析・デバッグ・自己進化システム
Dockerなしで完全動作するバージョン
"""

import sys
import json
import datetime
import os
import re
import base64
import shutil
from pathlib import Path

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import OllamaClient, ConversationalEvolutionAgent

class EnhancedDebugSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.debug_sessions = []
        self.debug_count = 0
        self.error_patterns = []  # 初期化を追加
        
        # データ保存先
        self.base_dir = Path.cwd()
        self.screenshots_dir = self.base_dir / "screenshots"
        self.data_dir = self.base_dir / "data"
        
        # ディレクトリを作成
        self.screenshots_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # データファイル
        self.sessions_file = self.data_dir / "enhanced_debug_sessions.json"
        self.patterns_file = self.data_dir / "error_patterns.json"
        
        # 既存データを読み込み
        self.load_sessions()
        self.load_error_patterns()
        
        # エラーパターン初期化
        self.init_error_patterns()
        
        print("🔍 強化版スクリーンショット分析・デバッグ・自己進化システム")
        print("=" * 70)
        print(f"📁 スクリーンショット保存先: {self.screenshots_dir}")
        print(f"📊 データ保存先: {self.data_dir}")
        print("=" * 70)
    
    def init_error_patterns(self):
        """エラーパターンを初期化"""
        if not self.error_patterns:
            self.error_patterns = [
                {
                    "pattern": r"Error\s+(\d+)",
                    "type": "error_code",
                    "description": "一般的なエラーコード",
                    "severity": "high",
                    "solutions": ["エラーコードを検索", "公式ドキュメントを確認", "ログを詳細に確認"]
                },
                {
                    "pattern": r"Exception\s+in\s+thread",
                    "type": "java_exception",
                    "description": "Javaスレッド例外",
                    "severity": "high",
                    "solutions": ["スタックトレースを確認", "スレッドセーフティを確認", "同期処理を見直す"]
                },
                {
                    "pattern": r"404\s+Not\s+Found",
                    "type": "http_error",
                    "description": "HTTP 404エラー",
                    "severity": "medium",
                    "solutions": ["URLを確認", "ルーティング設定を確認", "ファイル存在を確認"]
                },
                {
                    "pattern": r"500\s+Internal\s+Server\s+Error",
                    "type": "http_error",
                    "description": "HTTP 500エラー",
                    "severity": "high",
                    "solutions": ["サーバーログを確認", "コードのバグを修正", "設定を見直す"]
                },
                {
                    "pattern": r"SyntaxError",
                    "type": "syntax_error",
                    "description": "構文エラー",
                    "severity": "high",
                    "solutions": ["構文を修正", "インデントを確認", "括弧の対応を確認"]
                },
                {
                    "pattern": r"TypeError",
                    "type": "type_error",
                    "description": "型エラー",
                    "severity": "medium",
                    "solutions": ["型変換を確認", "変数の型をチェック", "関数の引数を確認"]
                },
                {
                    "pattern": r"Connection\s+refused",
                    "type": "connection_error",
                    "description": "接続拒否エラー",
                    "severity": "high",
                    "solutions": ["サービス起動を確認", "ポートを確認", "ファイアウォールを確認"]
                },
                {
                    "pattern": r"Timeout",
                    "type": "timeout_error",
                    "description": "タイムアウトエラー",
                    "severity": "medium",
                    "solutions": ["タイムアウト値を調整", "ネットワークを確認", "処理時間を最適化"]
                }
            ]
            self.save_error_patterns()
    
    def load_sessions(self):
        """デバッグセッションを読み込む"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.debug_sessions = data.get('sessions', [])
                    self.debug_count = data.get('debug_count', 0)
                print(f"📚 デバッグセッションを読み込みました ({len(self.debug_sessions)}件)")
        except Exception as e:
            print(f"❌ セッション読み込みエラー: {e}")
            self.debug_sessions = []
            self.debug_count = 0
    
    def load_error_patterns(self):
        """エラーパターンを読み込む"""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, "r", encoding="utf-8") as f:
                    self.error_patterns = json.load(f)
                print(f"📚 エラーパターンを読み込みました ({len(self.error_patterns)}件)")
        except Exception as e:
            print(f"❌ パターン読み込みエラー: {e}")
            self.error_patterns = []
    
    def save_sessions(self):
        """デバッグセッションを保存"""
        try:
            data = {
                'sessions': self.debug_sessions,
                'debug_count': self.debug_count,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ セッション保存エラー: {e}")
    
    def save_error_patterns(self):
        """エラーパターンを保存"""
        try:
            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(self.error_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ パターン保存エラー: {e}")
    
    def save_screenshot(self, source_path, filename=None):
        """スクリーンショットを保存"""
        try:
            if not filename:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                ext = Path(source_path).suffix
                filename = f"screenshot_{timestamp}{ext}"
            
            dest_path = self.screenshots_dir / filename
            
            # ファイルをコピー
            shutil.copy2(source_path, dest_path)
            
            print(f"💾 スクリーンショットを保存: {dest_path}")
            return str(dest_path)
            
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return None
    
    def extract_text_from_file(self, file_path):
        """ファイルからテキストを抽出"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="shift_jis") as f:
                    content = f.read()
                return content
            except:
                return "テキスト抽出失敗"
        except Exception as e:
            return f"ファイル読み込みエラー: {e}"
    
    def detect_error_patterns(self, text):
        """エラーパターンを検出"""
        detected_errors = []
        
        for pattern in self.error_patterns:
            matches = re.findall(pattern["pattern"], text, re.IGNORECASE)
            if matches:
                detected_errors.append({
                    "type": pattern["type"],
                    "description": pattern["description"],
                    "severity": pattern["severity"],
                    "matches": matches,
                    "solutions": pattern["solutions"]
                })
        
        return detected_errors
    
    def analyze_with_ai(self, text, file_path):
        """AIでテキストを分析"""
        try:
            prompt = f"""
            以下のスクリーンショットテキストを詳細に分析してください。
            
            ファイルパス: {file_path}
            
            テキスト内容:
            {text[:2000]}  # 最初の2000文字のみ
            
            分析項目:
            1. エラーメッセージの検出と特定
            2. 問題の根本原因の分析
            3. 具体的な解決策の提案
            4. 問題の重大度評価（低/中/高/緊急）
            5. 予防策の提案
            
            技術的な詳細を含めて、実践的なデバッグアドバイスを提供してください。
            """
            
            response = self.ollama_client.generate_response(prompt)
            return response
            
        except Exception as e:
            return f"AI分析エラー: {e}"
    
    def debug_screenshot(self, file_path):
        """スクリーンショットデバッグを実行"""
        print(f"\n🔍 スクリーンショット分析開始: {file_path}")
        print("-" * 60)
        
        # ファイル存在確認
        if not os.path.exists(file_path):
            print(f"❌ ファイルが存在しません: {file_path}")
            return None
        
        # スクリーンショットを保存
        saved_path = self.save_screenshot(file_path)
        if not saved_path:
            print("❌ スクリーンショット保存に失敗しました")
            return None
        
        # テキスト抽出
        print("📝 テキスト抽出中...")
        text_content = self.extract_text_from_file(file_path)
        
        # エラーパターン検出
        print("🔍 エラーパターン検出中...")
        detected_errors = self.detect_error_patterns(text_content)
        
        # AI分析
        print("🤖 AI分析中...")
        ai_analysis = self.analyze_with_ai(text_content, file_path)
        
        # 結果表示
        print(f"\n📊 分析結果:")
        print(f"📄 テキスト内容（抜粋）: {text_content[:200]}...")
        
        if detected_errors:
            print(f"\n🚨 検出されたエラー ({len(detected_errors)}件):")
            for i, error in enumerate(detected_errors, 1):
                print(f"  {i}. {error['description']} ({error['severity']})")
                print(f"     検出: {error['matches']}")
                print(f"     解決策: {', '.join(error['solutions'][:2])}")
        else:
            print("✅ エラーパターンは検出されませんでした")
        
        print(f"\n🤖 AI分析:")
        print(f"{ai_analysis}")
        
        # セッション記録
        session = {
            "id": self.debug_count + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "original_path": str(file_path),
            "saved_path": saved_path,
            "text_content": text_content[:1000],  # 最初の1000文字のみ保存
            "detected_errors": detected_errors,
            "ai_analysis": ai_analysis,
            "consciousness_before": self.conversational_agent.consciousness_level
        }
        
        # 進化チェック
        print("\n🧠 進化チェック中...")
        evolution_result = self.check_evolution(ai_analysis, detected_errors)
        if evolution_result:
            session["evolution"] = evolution_result
            print(f"✨ 自己進化が発生しました！")
        
        # セッション保存
        self.debug_sessions.append(session)
        self.debug_count += 1
        self.save_sessions()
        
        print(f"\n✅ デバッグセッション完了 (ID: {session['id']})")
        return session
    
    def check_evolution(self, analysis, detected_errors):
        """進化をチェック"""
        try:
            # デバッグ分析を進化トリガーとして使用
            evolution_text = f"デバッグ分析: {analysis[:500]}"
            if detected_errors:
                evolution_text += f" エラー検出: {len(detected_errors)}件"
            
            conversation = [
                {"user": "スクリーンショットデバッグ分析", "assistant": evolution_text}
            ]
            
            result = self.conversational_agent.check_and_evolve_automatically(conversation)
            
            if result and result.get("success"):
                print(f"🧠 意識レベル: {result['new_consciousness_level']:.3f} (+{result['consciousness_boost']:.3f})")
                print(f"🎯 進化タイプ: {result['evolution_type']}")
                return result
        
        except Exception as e:
            print(f"❌ 進化チェックエラー: {e}")
        
        return None
    
    def list_screenshots(self):
        """スクリーンショット一覧を取得"""
        try:
            screenshots = list(self.screenshots_dir.glob("*"))
            screenshots = [f for f in screenshots if f.is_file()]
            return sorted(screenshots, key=lambda x: x.stat().st_mtime, reverse=True)
        except Exception as e:
            print(f"❌ 一覧取得エラー: {e}")
            return []
    
    def get_debug_summary(self):
        """デバッグサマリーを取得"""
        if not self.debug_sessions:
            return "📊 デバッグセッションがありません"
        
        total_sessions = len(self.debug_sessions)
        evolution_count = sum(1 for s in self.debug_sessions if 'evolution' in s)
        error_count = sum(len(s.get('detected_errors', [])) for s in self.debug_sessions)
        
        # エラータイプ集計
        error_types = {}
        for session in self.debug_sessions:
            for error in session.get('detected_errors', []):
                error_type = error['type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        summary = f"""
📊 デバッグサマリー:
  💾 総セッション数: {total_sessions}
  🚨 総エラー検出数: {error_count}
  🧠 進化回数: {evolution_count}
  📈 進化率: {(evolution_count/total_sessions*100):.1f}%
  🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}
  
📋 エラータイプ分布:
"""
        
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            summary += f"  {error_type}: {count}件\n"
        
        return summary
    
    def interactive_mode(self):
        """対話モード"""
        print("\n🔍 強化版スクリーンショットデバッグシステム")
        print("1. 新規デバッグ")
        print("2. スクリーンショット一覧")
        print("3. デバッグサマリー")
        print("4. エラーパターン一覧")
        print("5. 終了")
        
        while True:
            choice = input("\n選択 (1-5): ").strip()
            
            if choice == "1":
                file_path = input("📸 スクリーンショットパス: ").strip()
                if os.path.exists(file_path):
                    self.debug_screenshot(file_path)
                else:
                    print("❌ ファイルが見つかりません")
            
            elif choice == "2":
                screenshots = self.list_screenshots()
                print(f"\n📁 スクリーンショット一覧 ({len(screenshots)}件):")
                for i, screenshot in enumerate(screenshots, 1):
                    size = screenshot.stat().st_size
                    mtime = datetime.datetime.fromtimestamp(screenshot.stat().st_mtime)
                    print(f"  {i}. {screenshot.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
            
            elif choice == "3":
                print(self.get_debug_summary())
            
            elif choice == "4":
                print(f"\n📋 エラーパターン一覧 ({len(self.error_patterns)}件):")
                for i, pattern in enumerate(self.error_patterns, 1):
                    print(f"  {i}. {pattern['description']} ({pattern['severity']})")
                    print(f"     パターン: {pattern['pattern']}")
            
            elif choice == "5":
                print("👋 終了します")
                break
            
            else:
                print("❌ 無効な選択です")

def main():
    """メイン関数"""
    debug_system = EnhancedDebugSystem()
    debug_system.interactive_mode()

if __name__ == "__main__":
    main()
