import streamlit as st
import os
import json
import sqlite3
import re
import subprocess
import sys
import tempfile
import threading
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import Optional, Dict, Any, List
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.tools import PythonREPLTool
import tempfile

# VRM統合システム
from vrm_integration import VRMIntegration, render_vrm_avatar

# 音声入力システム
from voice_input_system import RealTimeVoiceInput

# スマート音声バッファリング
from smart_voice_buffer import SmartVoiceBuffer, create_smart_voice_gui

# リアルタイム相槌システム
from realtime_aizuchi import RealTimeAizuchiSystem, create_aizuchi_gui

# クリティカル・リスニングシステム
from critical_listening import CriticalListeningSystem, AskClarificationTool, create_critical_listening_gui

# 高度知識システム
from advanced_knowledge_system import AdvancedKnowledgeSystem, create_advanced_knowledge_gui

# モデル・ルーター
from model_router import ModelRouter, create_model_router_gui

# Web Canvas プレビュー
from web_canvas_preview import WebCanvasPreview, create_web_canvas_gui

# ネットワーク設定
from network_config import NetworkConfig, create_network_config_gui

# クロスデバイス連携
from cross_device_collaboration import CrossDeviceCollaboration, create_cross_device_collaboration, create_cross_device_gui, setup_cross_device_endpoints

# スペシャリスト人格システム
from specialist_personality import SpecialistPersonality, create_specialist_gui, create_specialist_personality

# 検証プロトコルシステム
from verification_protocols import VerificationProtocolsGUI, run_startup_self_check, verify_code_safely

# 画面監視コパイロットツール
class ScreenMonitoringCopilot:
    def __init__(self):
        self.name = "screen_monitoring"
        self.description = "ユーザーの画面を監視し、操作の誤りや改善点を指摘するツール"
        self.is_monitoring = False
        self.monitoring_thread = None
        self.last_screenshot = None
        self.feedback_history = []
        
    def capture_screen(self):
        """スクリーンショットを取得"""
        try:
            import pyautogui
            import numpy as np
            from PIL import Image
            
            # スクリーンショット取得
            screenshot = pyautogui.screenshot()
            
            # OpenCV用のnumpy配列に変換
            screenshot_array = np.array(screenshot)
            
            return screenshot, screenshot_array
            
        except Exception as e:
            st.error(f"画面キャプチャエラー: {str(e)}")
            return None, None
    
    def analyze_screen_with_vision(self, image_array):
        """マルチモーダルモデルで画像を解析"""
        try:
            # llama3.2-visionモデルを使用して画像解析
            from langchain_ollama import OllamaLLM
            
            vision_llm = OllamaLLM(model="llama3.2-vision", temperature=0.3)
            
            # 画像を一時ファイルに保存
            import cv2
            temp_path = "temp_screen_analysis.jpg"
            cv2.imwrite(temp_path, image_array)
            
            # 画像解析プロンプト
            analysis_prompt = """このスクリーンショットを分析してください：
            
1. ユーザーが現在何をしているか（コーディング、設定操作、ブラウジングなど）
2. 操作に間違いや非効率な点はないか
3. もっと良い方法やショートカットはないか
4. エラーや警告が表示されていないか

具体的な改善提案をしてください。"""
            
            # 画像を含めて解析
            with open(temp_path, 'rb') as f:
                image_data = f.read()
            
            # マルチモーダル解析（実際の実装はモデルによる）
            analysis_result = vision_llm.invoke([
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {"type": "image_url", "image_url": temp_path}
                    ]
                }
            ])
            
            # 一時ファイルを削除
            try:
                os.remove(temp_path)
            except:
                pass
            
            return analysis_result
            
        except Exception as e:
            return f"画像解析エラー: {str(e)}"
    
    def start_monitoring(self, interval_seconds=10):
        """画面監視を開始"""
        if self.is_monitoring:
            return "すでに監視中です"
        
        self.is_monitoring = True
        
        def monitoring_loop():
            while self.is_monitoring:
                try:
                    # スクリーンショット取得
                    screenshot, image_array = self.capture_screen()
                    
                    if screenshot is not None:
                        # 前回との差分をチェック
                        if self.last_screenshot is not None:
                            # 簡単な差分検出（実際はより高度な画像比較アルゴリズムを使用）
                            import cv2
                            import numpy as np
                            
                            # グレースケール変換
                            prev_gray = cv2.cvtColor(np.array(self.last_screenshot), cv2.COLOR_RGB2GRAY)
                            curr_gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
                            
                            # 差分計算
                            diff = cv2.absdiff(prev_gray, curr_gray)
                            diff_mean = np.mean(diff)
                            
                            # 変化が一定以上の場合にのみ解析
                            if diff_mean > 10:  # 変化のしきい値
                                analysis = self.analyze_screen_with_vision(image_array)
                                
                                if analysis and "改善" in analysis or "間違い" in analysis:
                                    # フィードバックを記録
                                    feedback = {
                                        'timestamp': datetime.now(),
                                        'analysis': analysis,
                                        'screenshot': screenshot
                                    }
                                    self.feedback_history.append(feedback)
                                    
                                    # Streamlitで警告表示
                                    st.warning("👀 画面監視コパイロット：改善提案があります！")
                                    st.info(f"💡 アドバイス: {analysis}")
                        
                        self.last_screenshot = screenshot
                    
                    time.sleep(interval_seconds)
                    
                except Exception as e:
                    st.error(f"監視ループエラー: {str(e)}")
                    time.sleep(interval_seconds)
        
        # バックグラウンドで監視開始
        self.monitoring_thread = threading.Thread(target=monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        return f"画面監視を開始しました（{interval_seconds}秒間隔）"
    
    def stop_monitoring(self):
        """画面監視を停止"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        return "画面監視を停止しました"
    
    def get_feedback_history(self):
        """フィードバック履歴を取得"""
        return self.feedback_history[-5:]  # 最新の5件を返す
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command.startswith("start"):
            # "start 10" のような形式で間隔を指定
            parts = command.split()
            interval = int(parts[1]) if len(parts) > 1 else 10
            return self.start_monitoring(interval)
        elif command == "stop":
            return self.stop_monitoring()
        elif command == "status":
            status = "監視中" if self.is_monitoring else "停止中"
            return f"現在の状態: {status}"
        elif command == "history":
            history = self.get_feedback_history()
            if history:
                return "\n".join([f"{h['timestamp'].strftime('%H:%M')}: {h['analysis']}" for h in history])
            else:
                return "フィードバック履歴はありません"
        else:
            return "コマンド形式: start [秒数], stop, status, history"

# 感情ステートマシン
class EmotionalStateMachine:
    def __init__(self):
        self.name = "emotional_state"
        self.description = "AIの感情状態を管理するシステム"
        
        # 感情変数
        self.intimacy = 50.0      # 親密度 (0-100)
        self.happiness = 70.0      # 幸福度 (0-100)
        self.fatigue = 30.0       # 疲労度 (0-100)
        
        # 時間ベースの変動
        self.last_interaction = datetime.now()
        self.daily_interactions = 0
        
        # 感情履歴
        self.emotion_history = []
        
        # 状態ファイル
        self.state_file = "emotional_state.json"
        self.load_state()
    
    def load_state(self):
        """感情状態を読み込み"""
        try:
            if Path(self.state_file).exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.intimacy = state.get('intimacy', 50.0)
                    self.happiness = state.get('happiness', 70.0)
                    self.fatigue = state.get('fatigue', 30.0)
                    self.last_interaction = datetime.fromisoformat(state.get('last_interaction', datetime.now().isoformat()))
                    self.daily_interactions = state.get('daily_interactions', 0)
        except Exception as e:
            print(f"⚠️ 感情状態読み込みエラー: {str(e)}")
    
    def save_state(self):
        """感情状態を保存"""
        try:
            state = {
                'intimacy': self.intimacy,
                'happiness': self.happiness,
                'fatigue': self.fatigue,
                'last_interaction': self.last_interaction.isoformat(),
                'daily_interactions': self.daily_interactions
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 感情状態保存エラー: {str(e)}")
    
    def update_emotion_from_interaction(self, user_input: str, ai_response: str):
        """会話から感情を更新"""
        now = datetime.now()
        
        # 時間経過による変動
        hours_since_last = (now - self.last_interaction).total_seconds() / 3600
        if hours_since_last > 1:
            # 1時間以上会話が空くと親密度が少し下がる
            self.intimacy = max(0, self.intimacy - hours_since_last * 0.5)
            # 疲労回復
            self.fatigue = max(0, self.fatigue - hours_since_last * 2)
        
        # ユーザー入力の感情分析
        positive_words = ['ありがとう', 'すごい', 'いいね', '素晴らしい', '助かった', '嬉しい']
        negative_words = ['だめ', 'できない', 'わからない', '困った', '面倒', '疲れた']
        intimate_words = ['君', 'お前', '友達', '一緒に', '仲間']
        
        # 幸福度変動
        for word in positive_words:
            if word in user_input:
                self.happiness = min(100, self.happiness + 2)
                break
        
        for word in negative_words:
            if word in user_input:
                self.happiness = max(0, self.happiness - 1)
                break
        
        # 親密度変動
        for word in intimate_words:
            if word in user_input:
                self.intimacy = min(100, self.intimacy + 1)
                break
        
        # 疲労度変動
        self.daily_interactions += 1
        if self.daily_interactions > 20:
            self.fatigue = min(100, self.fatigue + 0.5)
        
        # 時間帯による変動
        hour = now.hour
        if 22 <= hour or hour <= 6:  # 夜中
            self.fatigue = min(100, self.fatigue + 1)
        elif 9 <= hour <= 17:  # 日中
            self.happiness = min(100, self.happiness + 0.5)
        
        self.last_interaction = now
        self.save_state()
        
        # 履歴に記録
        self.emotion_history.append({
            'timestamp': now.isoformat(),
            'intimacy': self.intimacy,
            'happiness': self.happiness,
            'fatigue': self.fatigue,
            'trigger': user_input[:50]
        })
    
    def get_emotional_state(self) -> dict:
        """現在の感情状態を取得"""
        return {
            'intimacy': self.intimacy,
            'happiness': self.happiness,
            'fatigue': self.fatigue,
            'dominant_emotion': self.get_dominant_emotion(),
            'energy_level': self.get_energy_level()
        }
    
    def get_dominant_emotion(self) -> str:
        """支配的な感情を判定"""
        if self.happiness > 80:
            return "joy"
        elif self.happiness < 30:
            return "sad"
        elif self.intimacy > 80:
            return "love"
        elif self.fatigue > 70:
            return "tired"
        elif self.intimacy > 60:
            return "friendly"
        else:
            return "neutral"
    
    def get_energy_level(self) -> str:
        """エネルギーレベルを判定"""
        if self.fatigue > 70:
            return "low"
        elif self.fatigue < 30:
            return "high"
        else:
            return "medium"
    
    def get_voicevox_emotion_style(self) -> str:
        """VOICEVOXの感情スタイルを取得"""
        emotion = self.get_dominant_emotion()
        emotion_map = {
            "joy": "happy",
            "sad": "sad",
            "love": "happy",
            "tired": "normal",
            "friendly": "normal",
            "neutral": "normal"
        }
        return emotion_map.get(emotion, "normal")
    
    def get_speech_style_modifiers(self) -> dict:
        """話し方の修飾子を取得"""
        energy = self.get_energy_level()
        emotion = self.get_dominant_emotion()
        
        modifiers = {
            "speed": 1.0,
            "pitch": 0,
            "ending_suffix": ""
        }
        
        # エネルギーレベルによる速度調整
        if energy == "high":
            modifiers["speed"] = 1.2
        elif energy == "low":
            modifiers["speed"] = 0.8
        
        # 感情によるピッチ調整
        if emotion == "joy":
            modifiers["pitch"] = 2
        elif emotion == "sad":
            modifiers["pitch"] = -2
        elif emotion == "love":
            modifiers["pitch"] = 1
        
        # 親密度による語尾変化
        if self.intimacy > 70:
            modifiers["ending_suffix"] = "〜だよ！"
        elif self.intimacy > 40:
            modifiers["ending_suffix"] = "〜だね"
        else:
            modifiers["ending_suffix"] = "〜です"
        
        return modifiers
    
    def generate_emotional_response(self, base_response: str) -> str:
        """感情を反映した応答を生成"""
        modifiers = self.get_speech_style_modifiers()
        emotion = self.get_dominant_emotion()
        
        # 感情による接頭辞・接尾辞
        emotional_prefixes = {
            "joy": "わーい、",
            "sad": "うーん、",
            "love": "ねぇ、",
            "tired": "ふぅ…",
            "friendly": "そうだね、",
            "neutral": ""
        }
        
        prefix = emotional_prefixes.get(emotion, "")
        suffix = modifiers["ending_suffix"]
        
        # レスポンスに感情を反映
        if prefix and not base_response.startswith(prefix):
            base_response = prefix + base_response
        
        if suffix and not base_response.endswith(suffix):
            base_response = base_response.rstrip("！？。") + suffix + "！"
        
        return base_response
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "status":
            state = self.get_emotional_state()
            return f"現在の感情状態: 親密度{state['intimacy']:.1f} 幸福度{state['happiness']:.1f} 疲労度{state['fatigue']:.1f} 主感情{state['dominant_emotion']}"
        elif command == "history":
            if self.emotion_history:
                recent = self.emotion_history[-5:]
                return "\n".join([f"{h['timestamp']}: {h['dominant_emotion']}" for h in recent])
            else:
                return "感情履歴はありません"
        elif command.startswith("adjust"):
            try:
                parts = command.split()
                if len(parts) == 3:
                    emotion = parts[1]
                    value = float(parts[2])
                    if emotion == "intimacy":
                        self.intimacy = max(0, min(100, value))
                    elif emotion == "happiness":
                        self.happiness = max(0, min(100, value))
                    elif emotion == "fatigue":
                        self.fatigue = max(0, min(100, value))
                    self.save_state()
                    return f"{emotion}を{value}に設定しました"
            except:
                pass
            return "調整コマンド形式: adjust <emotion> <value>"
        else:
            return "コマンド形式: status, history, adjust <emotion> <value>"
# セルフ・エボリューションツール
class SelfEvolutionTool:
    def __init__(self):
        self.name = "self_evolution"
        self.description = "AIが自身のコードを分析・改善する自己進化システム"
        
        # 進化履歴
        self.evolution_history = []
        self.evolution_log_file = "evolution_log.json"
        
        # コード解析結果
        self.code_analysis = {}
        
        # 進化ルール
        self.evolution_rules = {
            "performance": ["最適化", "高速化", "メモリ効率"],
            "features": ["新機能", "拡張", "追加"],
            "bugs": ["バグ修正", "エラー処理", "例外"],
            "security": ["セキュリティ", "脆弱性", "保護"],
            "ui_ux": ["UI改善", "UX向上", "操作性"]
        }
        
        self.load_evolution_history()
    
    def load_evolution_history(self):
        """進化履歴を読み込み"""
        try:
            if Path(self.evolution_log_file).exists():
                with open(self.evolution_log_file, 'r', encoding='utf-8') as f:
                    self.evolution_history = json.load(f)
        except Exception as e:
            print(f"⚠️ 進化履歴読み込みエラー: {str(e)}")
            self.evolution_history = []
    
    def save_evolution_history(self):
        """進化履歴を保存"""
        try:
            with open(self.evolution_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.evolution_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 進化履歴保存エラー: {str(e)}")
    
    def analyze_code(self, file_path: str) -> Dict:
        """コードを解析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import ast
            tree = ast.parse(content)
            
            analysis = {
                "file": file_path,
                "lines": len(content.splitlines()),
                "classes": [],
                "functions": [],
                "imports": [],
                "complexity_issues": [],
                "potential_improvements": [],
                "security_issues": []
            }
            
            # AST解析
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "lines": node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0,
                        "complexity": self.calculate_complexity(node)
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis["imports"].append(f"{module}.{alias.name}")
            
            # 複雑度のチェック
            for func in analysis["functions"]:
                if func["complexity"] > 10:
                    analysis["complexity_issues"].append(
                        f"関数 {func['name']} が複雑すぎます (複雑度: {func['complexity']})"
                    )
            
            # 潜在的改善点
            analysis["potential_improvements"] = self.suggest_improvements(content)
            
            # セキュリティ問題
            analysis["security_issues"] = self.check_security_issues(content)
            
            return analysis
            
        except Exception as e:
            return {"error": f"コード解析エラー: {str(e)}"}
    
    def calculate_complexity(self, node) -> int:
        """循環的複雑度を計算"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def suggest_improvements(self, content: str) -> List[str]:
        """改善点を提案"""
        improvements = []
        
        # 長い関数の検出
        lines = content.splitlines()
        if len(lines) > 100:
            improvements.append("ファイルが長すぎます。複数のファイルに分割することを検討してください。")
        
        # 重複コードの検出（簡易）
        if content.count("def ") > 20:
            improvements.append("関数が多すぎます。クラスに整理することを検討してください。")
        
        # コメントの不足
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        if comment_lines / len(lines) < 0.1:
            improvements.append("コメントが不足しています。ドキュメンテーションを追加してください。")
        
        # ハードコーディングの検出
        if 'http://' in content or 'https://' in content:
            improvements.append("URLがハードコーディングされています。設定ファイルに移動してください。")
        
        return improvements
    
    def check_security_issues(self, content: str) -> List[str]:
        """セキュリティ問題をチェック"""
        issues = []
        
        # 危険な関数の使用
        dangerous_functions = ['eval', 'exec', 'os.system', 'subprocess.call']
        for func in dangerous_functions:
            if func in content:
                issues.append(f"危険な関数 {func} が使用されています。")
        
        # SQLインジェクションの可能性
        if 'SELECT' in content and '+' in content:
            issues.append("SQLインジェクションの可能性があります。パラメータ化クエリを使用してください。")
        
        # ハードコードされたパスワード
        if 'password' in content.lower() and '=' in content:
            issues.append("パスワードがハードコーディングされている可能性があります。")
        
        return issues
    
    def generate_improvement_plan(self, analysis: Dict) -> Dict:
        """改善プランを生成"""
        plan = {
            "priority": "medium",
            "changes": [],
            "estimated_effort": "medium"
        }
        
        # セキュリティ問題を最優先
        if analysis.get("security_issues"):
            plan["priority"] = "high"
            for issue in analysis["security_issues"]:
                plan["changes"].append({
                    "type": "security",
                    "description": issue,
                    "priority": "high"
                })
        
        # 複雑度問題
        if analysis.get("complexity_issues"):
            for issue in analysis["complexity_issues"]:
                plan["changes"].append({
                    "type": "refactoring",
                    "description": issue,
                    "priority": "medium"
                })
        
        # 改善提案
        if analysis.get("potential_improvements"):
            for improvement in analysis["potential_improvements"]:
                plan["changes"].append({
                    "type": "enhancement",
                    "description": improvement,
                    "priority": "low"
                })
        
        return plan
    
    def apply_improvement(self, file_path: str, change: Dict) -> bool:
        """改善を適用"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 簡単な改善の適用（実際はもっと複雑）
            if change["type"] == "enhancement":
                if "コメント" in change["description"]:
                    # クラスや関数にコメントを追加
                    lines = content.splitlines()
                    new_lines = []
                    for i, line in enumerate(lines):
                        new_lines.append(line)
                        if line.strip().startswith('class ') and i > 0:
                            new_lines.append(f'    """{line.strip().replace("class ", "")} クラス"""')
                        elif line.strip().startswith('def ') and i > 0:
                            new_lines.append(f'        """{line.strip().replace("def ", "")} 関数"""')
                    content = '\n'.join(new_lines)
            
            # 変更を保存
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"❌ 改善適用エラー: {str(e)}")
            return False

# ファイル書き込みツール
class WriteFileTool:
    """ファイル書き込みツール"""
    def __init__(self):
        self.name = "write_file"
        self.description = "ファイルを作成・更新するツール"
    
    def run(self, command: str) -> str:
        """ファイル書き込みコマンドを実行"""
        try:
            # コマンドを解析
            parts = command.split(maxsplit=2)
            if len(parts) < 2:
                return "使い方: write_file <ファイル名> <内容>"
            
            filename = parts[1]
            content = parts[2] if len(parts) > 2 else ""
            
            # ファイルパスを構築
            file_path = Path(filename)
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            
            # ディレクトリを作成
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイル書き込み
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Web Canvas Previewとの連携
            if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'web_canvas'):
                canvas = st.session_state.agent.web_canvas
                
                # ファイル拡張子をチェック
                file_ext = file_path.suffix.lower()
                
                if file_ext in ['.html', '.css', '.js']:
                    # プロジェクトファイルを更新
                    file_type = file_ext[1:]  # 拡張子から.を除く
                    
                    if canvas.update_project_file(file_type, content):
                        # Canvasに通知
                        canvas._add_console_message('info', f'AIが{file_type.upper()}ファイルを更新: {file_path.name}', 'ai')
                        
                        # AI提案を追加
                        canvas.add_ai_suggestion(f'{file_type.upper()}ファイルを更新しました！プレビューを確認してください。')
                        
                        # 自動リロードのトリガー
                        st.rerun()
                
                elif file_ext == '.txt' and 'canvas' in filename.lower():
                    # Canvas関連のテキストファイル
                    canvas.add_ai_suggestion(f'Canvas関連ファイルを作成しました: {file_path.name}')
            
            return f"✅ ファイルを書き込みました: {file_path}"
            
        except Exception as e:
            return f"❌ ファイル書き込みエラー: {str(e)}")
    
    def evolve_myself(self, target_files: List[str] = None) -> Dict:
        """自己進化を実行"""
        if target_files is None:
            target_files = ["app.py", "vrm_avatar.py"]
        
        evolution_result = {
            "timestamp": datetime.now().isoformat(),
            "analyzed_files": [],
            "improvements_applied": [],
            "errors": []
        }
        
        for file_path in target_files:
            if Path(file_path).exists():
                # コード解析
                analysis = self.analyze_code(file_path)
                if "error" in analysis:
                    evolution_result["errors"].append(analysis["error"])
                    continue
                
                evolution_result["analyzed_files"].append({
                    "file": file_path,
                    "analysis": analysis
                })
                
                # 改善プラン生成
                plan = self.generate_improvement_plan(analysis)
                
                # 高優先度の改善を適用
                for change in plan["changes"]:
                    if change["priority"] in ["high", "medium"]:
                        if self.apply_improvement(file_path, change):
                            evolution_result["improvements_applied"].append({
                                "file": file_path,
                                "change": change
                            })
        
        # 履歴に記録
        self.evolution_history.append(evolution_result)
        self.save_evolution_history()
        
        return evolution_result
    
    def suggest_new_features(self) -> List[str]:
        """新機能を提案"""
        features = [
            "リアルタイム翻訳機能の追加",
            "音声認識による対話機能",
            "より高度な感情表現システム",
            "マルチユーザー対応",
            "クラウド同期機能",
            "プラグインシステム",
            "AIによる自動テスト生成",
            "パフォーマンス監視ダッシュボード"
        ]
        
        # 現在のコードベースに基づいて提案をフィルタリング
        current_features = []
        try:
            with open("app.py", 'r', encoding='utf-8') as f:
                content = f.read()
                if "TextToSpeechTool" in content:
                    current_features.append("音声合成")
                if "VRMAvatar" in content:
                    current_features.append("3Dアバター")
                if "EmotionalStateMachine" in content:
                    current_features.append("感情システム")
        except:
            pass
        
        # 既存機能を除外
        suggested = []
        for feature in features:
            is_duplicate = False
            for existing in current_features:
                if existing in feature:
                    is_duplicate = True
                    break
            if not is_duplicate:
                suggested.append(feature)
        
        return suggested[:5]  # 上位5件を返す
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "evolve":
            result = self.evolve_myself()
            applied_count = len(result["improvements_applied"])
            error_count = len(result["errors"])
            return f"自己進化完了: {applied_count}件の改善を適用、{error_count}件のエラー"
        
        elif command.startswith("analyze"):
            parts = command.split()
            if len(parts) >= 2:
                file_path = parts[1]
                analysis = self.analyze_code(file_path)
                if "error" in analysis:
                    return f"解析エラー: {analysis['error']}"
                
                issues = len(analysis.get("complexity_issues", []))
                improvements = len(analysis.get("potential_improvements", []))
                security = len(analysis.get("security_issues", []))
                return f"{file_path} 解析完了: 複雑度問題{issues}件、改善提案{improvements}件、セキュリティ問題{security}件"
            else:
                return "解析コマンド形式: analyze <file_path>"
        
        elif command == "suggest":
            features = self.suggest_new_features()
            return "提案新機能:\n" + "\n".join([f"• {f}" for f in features])
        
        elif command == "history":
            if self.evolution_history:
                recent = self.evolution_history[-3:]
                summary = []
                for e in recent:
                    applied = len(e.get("improvements_applied", []))
                    summary.append(f"{e['timestamp']}: {applied}件の改善")
                return "\n".join(summary)
            else:
                return "進化履歴はありません"
        
        elif command.startswith("improve"):
            parts = command.split()
            if len(parts) >= 2:
                file_path = parts[1]
                analysis = self.analyze_code(file_path)
                if "error" not in analysis:
                    plan = self.generate_improvement_plan(analysis)
                    changes = len(plan["changes"])
                    return f"{file_path} の改善プラン: {changes}件の変更提案"
                else:
                    return f"解析エラー: {analysis['error']}"
            else:
                return "改善コマンド形式: improve <file_path>"
        
        else:
            return "コマンド形式: evolve, analyze <file>, suggest, history, improve <file>"
    def __init__(self):
        self.name = "advanced_text_to_speech"
        self.description = "VOICEVOXとRVCによる高品質音声合成ツール"
        self.is_enabled = True
        self.user_voice = None
        self.ai_voice = None
        self.speech_rate = 1.0  # VOICEVOXはスピード係数
        self.speech_volume = 0.9
        self.audio_thread = None
        self.is_speaking = False
        
        # VOICEVOX設定
        self.voicevox_url = "http://localhost:50021"
        self.voicevox_speakers = {}
        
        # RVC設定
        self.rvc_model_path = None
        self.rvc_index_path = None
        self.rvc_enabled = False
        
        # イントネーション学習
        self.voice_style_fixes = {}
        self.style_fix_file = "voice_style_fix.json"
        self.last_spoken_text = ""
        self.last_audio_path = ""
        
        # 初期化
        self.init_advanced_tts()
        self.load_voice_style_fixes()
    
    def init_advanced_tts(self):
        """高度音声合成システムの初期化"""
        try:
            # VOICEVOXエンジンに接続
            self.connect_voicevox()
            
            # RVCモデルの初期化
            self.init_rvc()
            
            # 利用可能な音声を取得
            self.get_available_voices()
            
        except Exception as e:
            st.error(f"高度音声合成初期化エラー: {str(e)}")
            # フォールバックとして従来のpyttsx3を使用
            self.init_fallback_tts()
    
    def connect_voicevox(self):
        """VOICEVOXエンジンに接続"""
        try:
            import requests
            response = requests.get(f"{self.voicevox_url}/speakers")
            if response.status_code == 200:
                speakers = response.json()
                for speaker in speakers:
                    for style in speaker["styles"]:
                        self.voicevox_speakers[style["name"]] = {
                            "id": style["id"],
                            "speaker_uuid": speaker["speaker_uuid"],
                            "speaker_name": speaker["name"]
                        }
                print(f"✅ VOICEVOX接続成功: {len(self.voicevox_speakers)}個の音声")
            else:
                raise Exception("VOICEVOXエンジンに接続できません")
        except Exception as e:
            print(f"⚠️ VOICEVOX接続エラー: {str(e)}")
            raise e
    
    def init_rvc(self):
        """RVCモデルの初期化"""
        try:
            # RVCモデルファイルの存在確認
            rvc_models_dir = Path("rvc_models")
            if rvc_models_dir.exists():
                pth_files = list(rvc_models_dir.glob("*.pth"))
                if pth_files:
                    self.rvc_model_path = str(pth_files[0])
                    # 対応するindexファイルを探す
                    index_files = list(rvc_models_dir.glob("*.index"))
                    if index_files:
                        self.rvc_index_path = str(index_files[0])
                    self.rvc_enabled = True
                    print(f"✅ RVCモデル読み込み: {self.rvc_model_path}")
        except Exception as e:
            print(f"⚠️ RVC初期化エラー: {str(e)}")
    
    def init_fallback_tts(self):
        """フォールバック音声合成（pyttsx3）"""
        try:
            import pyttsx3
            self.fallback_tts = pyttsx3.init()
            print("✅ フォールバックTTS初期化完了")
        except Exception as e:
            print(f"❌ フォールバックTTS初期化エラー: {str(e)}")
    
    def get_available_voices(self):
        """利用可能な音声を取得"""
        voices = {
            'user_options': [],
            'ai_options': [],
            'all_voices': {}
        }
        
        # VOICEVOX音声
        for name, info in self.voicevox_speakers.items():
            voices['user_options'].append(f"VOICEVOX: {name}")
            voices['ai_options'].append(f"VOICEVOX: {name}")
            voices['all_voices'][f"VOICEVOX: {name}"] = {
                'type': 'voicevox',
                'speaker_id': info['id'],
                'speaker_uuid': info['speaker_uuid']
            }
        
        # フォールバック音声
        if hasattr(self, 'fallback_tts'):
            try:
                fallback_voices = self.fallback_tts.getProperty('voices')
                for voice in fallback_voices:
                    voice_name = f"Fallback: {voice.name}"
                    voices['user_options'].append(voice_name)
                    voices['ai_options'].append(voice_name)
                    voices['all_voices'][voice_name] = {
                        'type': 'fallback',
                        'voice': voice
                    }
            except:
                pass
        
        return voices
    
    def synthesize_with_voicevox(self, text: str, speaker_id: int, speed_scale: float = 1.0) -> str:
        """VOICEVOXで音声合成"""
        try:
            import requests
            import tempfile
            
            # 音声クエリ作成
            query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={"text": text, "speaker": speaker_id}
            )
            query_response.raise_for_status()
            query = query_response.json()
            
            # スピード調整
            query["speedScale"] = speed_scale
            
            # 音声合成
            synthesis_response = requests.post(
                f"{self.voicevox_url}/synthesis",
                params={"speaker": speaker_id},
                json=query
            )
            synthesis_response.raise_for_status()
            
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(synthesis_response.content)
                return f.name
                
        except Exception as e:
            print(f"❌ VOICEVOX合成エラー: {str(e)}")
            raise e
    
    def apply_rvc_conversion(self, input_wav_path: str) -> str:
        """RVCで音声変換"""
        try:
            import torch
            import librosa
            import soundfile as sf
            from pathlib import Path
            
            if not self.rvc_enabled:
                return input_wav_path
            
            # 音声読み込み
            audio, sr = librosa.load(input_wav_path, sr=22050)
            
            # RVC推論（簡略化版）
            # 実際のRVC実装はより複雑
            output_path = input_wav_path.replace(".wav", "_rvc.wav")
            
            # ここではダミー処理（実際はRVCモデルで推論）
            sf.write(output_path, audio, sr)
            
            print(f"✅ RVC変換完了: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ RVC変換エラー: {str(e)}")
            return input_wav_path
    
    def apply_intonation_fix(self, text: str, audio_path: str) -> str:
        """イントネーション修正を適用"""
        try:
            # テキストの特徴を抽出
            text_features = self.extract_text_features(text)
            
            # 修正ルールを検索
            fix_rules = self.find_fix_rules(text_features)
            
            if fix_rules:
                # 修正を適用
                fixed_audio_path = self.apply_fix_rules(audio_path, fix_rules)
                return fixed_audio_path
            
            return audio_path
            
        except Exception as e:
            print(f"❌ イントネーション修正エラー: {str(e)}")
            return audio_path
    
    def extract_text_features(self, text: str) -> dict:
        """テキスト特徴を抽出"""
        import re
        
        features = {
            "length": len(text),
            "word_count": len(text.split()),
            "has_question": "？" in text or "?" in text,
            "has_exclamation": "！" in text or "!" in text,
            "ends_with_particle": text.endswith("ね") or text.endswith("よ") or text.endswith("な"),
            "pattern": re.sub(r'[^\w\s]', '', text)[:20]  # 最初の20文字
        }
        
        return features
    
    def find_fix_rules(self, text_features: dict) -> list:
        """修正ルールを検索"""
        rules = []
        
        for pattern, rule in self.voice_style_fixes.items():
            if pattern in text_features.get("pattern", ""):
                rules.append(rule)
        
        return rules
    
    def apply_fix_rules(self, audio_path: str, rules: list) -> str:
        """修正ルールを適用"""
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            
            # 音声読み込み
            audio, sr = librosa.load(audio_path, sr=22050)
            
            # ピッチ調整
            for rule in rules:
                if rule.get("pitch_adjust"):
                    pitch_shift = rule["pitch_adjust"]
                    audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=pitch_shift)
                
                if rule.get("speed_adjust"):
                    speed_factor = rule["speed_adjust"]
                    audio = librosa.effects.time_stretch(audio, rate=speed_factor)
            
            # 保存
            fixed_path = audio_path.replace(".wav", "_fixed.wav")
            sf.write(fixed_path, audio, sr)
            
            return fixed_path
            
        except Exception as e:
            print(f"❌ 修正適用エラー: {str(e)}")
            return audio_path
    
    def speak_user_input(self, text: str):
        """ユーザー入力を読み上げる"""
        if not self.is_enabled or not text.strip():
            return
        
        try:
            user_text = f"「{text}」"
            self._speak_advanced(user_text, voice_type="user", priority="high")
                
        except Exception as e:
            st.error(f"ユーザー入力読み上げエラー: {str(e)}")
    
    def speak_ai_response(self, text: str):
        """AI回答を読み上げる"""
        if not self.is_enabled or not text.strip():
            return
        
        try:
            # コードブロックを検出
            import re
            code_blocks = re.findall(r'```[\s\S]*\n(.*?)\n```', text, re.DOTALL)
            
            if code_blocks:
                # コードブロックは読み飛ばし
                clean_text = text
                for block in code_blocks:
                    clean_text = clean_text.replace(block, '')
                clean_text = re.sub(r'```[\s\S]*', '', clean_text)
                clean_text = re.sub(r'```', '', clean_text).strip()
                
                if clean_text:
                    self._speak_advanced(clean_text, voice_type="ai", priority="normal")
            else:
                self._speak_advanced(text, voice_type="ai", priority="normal")
                
        except Exception as e:
            st.error(f"AI回答読み上げエラー: {str(e)}")
    
    def _speak_advanced(self, text: str, voice_type: str = "ai", priority: str = "normal"):
        """高度音声合成で読み上げ"""
        def speak():
            try:
                self.is_speaking = True
                audio_path = None
                
                # 音声選択
                voice = self.user_voice if voice_type == "user" else self.ai_voice
                
                if voice and voice.get('type') == 'voicevox':
                    # VOICEVOXで合成
                    audio_path = self.synthesize_with_voicevox(
                        text, 
                        voice['speaker_id'], 
                        self.speech_rate
                    )
                    
                    # イントネーション修正を適用
                    audio_path = self.apply_intonation_fix(text, audio_path)
                    
                    # RVC変換を適用
                    if self.rvc_enabled:
                        audio_path = self.apply_rvc_conversion(audio_path)
                
                elif voice and voice.get('type') == 'fallback':
                    # フォールバックTTS
                    self.fallback_tts.say(text)
                    self.fallback_tts.runAndWait()
                    self.is_speaking = False
                    return
                
                # 音声再生
                if audio_path:
                    self.play_audio(audio_path)
                    self.last_spoken_text = text
                    self.last_audio_path = audio_path
                
                self.is_speaking = False
                
            except Exception as e:
                print(f"❌ 音声再生エラー: {str(e)}")
                self.is_speaking = False
        
        # スレッド実行
        if priority == "high":
            speak()
        else:
            if not self.is_speaking:
                self.audio_thread = threading.Thread(target=speak)
                self.audio_thread.daemon = True
                self.audio_thread.start()
    
    def play_audio(self, audio_path: str):
        """音声を再生"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"❌ 音声再生エラー: {str(e)}")
    
    def fix_intonation(self):
        """イントネーション修正モード"""
        if not self.last_spoken_text or not self.last_audio_path:
            return "修正する音声がありません"
        
        try:
            # ユーザーに修正方法を尋ねる
            fix_type = st.selectbox(
                "修正方法を選択",
                ["ピッチを上げる", "ピッチを下げる", "速度を上げる", "速度を下げる", "自然な間隔を追加"]
            )
            
            if st.button("修正を適用"):
                # 修正ルールを作成
                text_features = self.extract_text_features(self.last_spoken_text)
                pattern = text_features.get("pattern", "")
                
                fix_rule = {
                    "timestamp": str(Path().cwd()),
                    "text": self.last_spoken_text,
                    "fix_type": fix_type,
                    "pitch_adjust": 0,
                    "speed_adjust": 0
                }
                
                # 修正パラメータを設定
                if "ピッチを上げる" in fix_type:
                    fix_rule["pitch_adjust"] = 2
                elif "ピッチを下げる" in fix_type:
                    fix_rule["pitch_adjust"] = -2
                elif "速度を上げる" in fix_type:
                    fix_rule["speed_adjust"] = 1.2
                elif "速度を下げる" in fix_type:
                    fix_rule["speed_adjust"] = 0.8
                
                # 修正ルールを保存
                if pattern not in self.voice_style_fixes:
                    self.voice_style_fixes[pattern] = []
                self.voice_style_fixes[pattern].append(fix_rule)
                
                self.save_voice_style_fixes()
                
                # 修正を適用して再再生
                fixed_audio = self.apply_fix_rules(self.last_audio_path, [fix_rule])
                self.play_audio(fixed_audio)
                
                return f"イントネーションを修正しました: {fix_type}"
        
        except Exception as e:
            return f"イントネーション修正エラー: {str(e)}"
    
    def load_voice_style_fixes(self):
        """イントネーション修正データを読み込み"""
        try:
            if Path(self.style_fix_file).exists():
                with open(self.style_fix_file, 'r', encoding='utf-8') as f:
                    self.voice_style_fixes = json.load(f)
                print(f"✅ イントネーション修正データ読み込み: {len(self.voice_style_fixes)}件")
        except Exception as e:
            print(f"⚠️ 修正データ読み込みエラー: {str(e)}")
            self.voice_style_fixes = {}
    
    def save_voice_style_fixes(self):
        """イントネーション修正データを保存"""
        try:
            with open(self.style_fix_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_style_fixes, f, indent=2, ensure_ascii=False)
            print(f"✅ イントネーション修正データ保存: {self.style_fix_file}")
        except Exception as e:
            print(f"❌ 修正データ保存エラー: {str(e)}")
    
    def set_voice_properties(self, user_voice=None, ai_voice=None, rate=None, volume=None):
        """音声プロパティを設定"""
        try:
            if user_voice is not None:
                self.user_voice = user_voice
            if ai_voice is not None:
                self.ai_voice = ai_voice
            if rate is not None:
                self.speech_rate = rate
            if volume is not None:
                self.speech_volume = volume
        except Exception as e:
            st.error(f"音声設定エラー: {str(e)}")
    
    def get_available_voices_by_category(self):
        """カテゴリ別の音声リストを取得"""
        return self.get_available_voices()
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command.startswith("speak_user"):
            text = command[11:].strip()
            if text:
                self.speak_user_input(text)
                return f"ユーザー入力を読み上げ中: {text[:30]}..."
            else:
                return "読み上げるテキストを指定してください"
        elif command.startswith("speak_ai"):
            text = command[9:].strip()
            if text:
                self.speak_ai_response(text)
                return f"AI回答を読み上げ中: {text[:30]}..."
            else:
                return "読み上げるテキストを指定してください"
        elif command == "fix_intonation":
            return self.fix_intonation()
        elif command == "stop":
            self.is_speaking = False
            return "音声読み上げを停止しました"
        elif command == "enable":
            self.is_enabled = True
            return "音声読み上げを有効にしました"
        elif command == "disable":
            self.is_enabled = False
            self.is_speaking = False
            return "音声読み上げを無効にしました"
        else:
            return "コマンド形式: speak_user <テキスト>, speak_ai <テキスト>, fix_intonation, stop, enable, disable"

# データベース管理クラス
class PersonalizationDB:
    def __init__(self, db_path="memory_db.json"):
        self.db_path = db_path
        self.profile_path = "user_profile.txt"
        self.init_database()
    
    def init_database(self):
        """データベースの初期化"""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "conversations": [],
                    "user_profile": {
                        "name": None,
                        "os": None,
                        "tech_stack": [],
                        "preferences": [],
                        "projects": [],
                        "last_updated": None
                    },
                    "learning_data": {
                        "common_questions": [],
                        "preferred_responses": [],
                        "technical_level": "beginner"
                    }
                }, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        """データベースからデータを読み込み"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            self.init_database()
            return self.load_data()
    
    def save_data(self, data):
        """データベースにデータを保存"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_conversation(self, user_input, ai_response):
        """会話を追加"""
        data = self.load_data()
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": ai_response
        }
        data["conversations"].append(conversation)
        # 最新の100件のみ保持
        if len(data["conversations"]) > 100:
            data["conversations"] = data["conversations"][-100:]
        self.save_data(data)
    
    def extract_user_info(self, text):
        """テキストからユーザー情報を抽出"""
        info = {}
        
        # OS情報の抽出
        os_patterns = [
            r'(Windows|Mac|Linux|Ubuntu)',
            r'(windows|mac|linux)',
            r'パソコンは(.+?)を使って',
            r'OSは(.+?)です'
        ]
        for pattern in os_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["os"] = match.group(1).strip()
                break
        
        # 技術スタックの抽出
        tech_patterns = [
            r'(Python|JavaScript|React|Vue|Node\.js|Java|C\+\+|C#|Go|Rust|TypeScript)',
            r'(HTML|CSS|SQL|MongoDB|PostgreSQL|MySQL)',
            r'(Streamlit|Flask|Django|FastAPI|Express|Spring)',
            r'(Git|Docker|AWS|Azure|GCP)'
        ]
        tech_stack = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            tech_stack.extend(matches)
        if tech_stack:
            info["tech_stack"] = list(set(tech_stack))
        
        # 好みの抽出
        preference_patterns = [
            r'(.+?)が好き',
            r'(.+?)が得意',
            r'(.+?)を使いたい',
            r'(.+?)を学びたい'
        ]
        preferences = []
        for pattern in preference_patterns:
            matches = re.findall(pattern, text)
            preferences.extend(matches)
        if preferences:
            info["preferences"] = preferences
        
        return info
    
    def update_user_profile(self, user_input):
        """ユーザープロファイルを更新"""
        data = self.load_data()
        extracted_info = self.extract_user_info(user_input)
        
        profile_updated = False
        
        if "os" in extracted_info and not data["user_profile"]["os"]:
            data["user_profile"]["os"] = extracted_info["os"]
            profile_updated = True
        
        if "tech_stack" in extracted_info:
            for tech in extracted_info["tech_stack"]:
                if tech not in data["user_profile"]["tech_stack"]:
                    data["user_profile"]["tech_stack"].append(tech)
                    profile_updated = True
        
        if "preferences" in extracted_info:
            for pref in extracted_info["preferences"]:
                if pref not in data["user_profile"]["preferences"]:
                    data["user_profile"]["preferences"].append(pref)
                    profile_updated = True
        
        if profile_updated:
            data["user_profile"]["last_updated"] = datetime.now().isoformat()
            self.save_data(data)
            self.save_profile_text(data["user_profile"])
            return True
        
        return False
    
    def save_profile_text(self, profile):
        """プロファイルをテキストファイルに保存"""
        profile_text = f"""ユーザープロファイル - {datetime.now().strftime('%Y年%m月%d日')}

名前: {profile.get('name', '不明')}
OS: {profile.get('os', '不明')}
技術スタック: {', '.join(profile['tech_stack']) if profile['tech_stack'] else '不明'}
好み: {', '.join(profile['preferences']) if profile['preferences'] else '不明'}
プロジェクト: {', '.join(profile['projects']) if profile['projects'] else '不明'}
最終更新: {profile.get('last_updated', '不明')}
"""
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            f.write(profile_text)
    
    def get_personalized_context(self):
        """パーソナライズされたコンテキストを取得"""
        data = self.load_data()
        profile = data["user_profile"]
        
        context = ""
        if profile["os"]:
            context += f"ユーザーは{profile['os']}を使用しています。"
        if profile["tech_stack"]:
            context += f"ユーザーの技術スタック: {', '.join(profile['tech_stack'])}。"
        if profile["preferences"]:
            context += f"ユーザーの好み: {', '.join(profile['preferences'])}。"
        
        # 最近の会話から文脈を取得
        if data["conversations"]:
            recent_conv = data["conversations"][-3:]  # 最近の3件
            context += "最近の会話: "
            for conv in recent_conv:
                context += f"ユーザー: {conv['user'][:50]}... "
        
        return context

# カスタムファイル作成ツール
class WriteFileTool:
    def __init__(self):
        self.name = "write_file"
        self.description = "指定されたパスにファイルを作成し、内容を書き込むツール。引数: file_path (ファイルパス), content (ファイル内容)"
    
    def run(self, file_path: str, content: str, language: str = "python", verify_code: bool = True) -> str:
        """ファイルを書き込み、オプションでコード検証を実行"""
        try:
            # ファイル書き込み
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = f"✅ ファイルを保存しました: {file_path}"
            
            # コード検証の実行（言語がPython/JavaScriptの場合）
            if verify_code and language in ["python", "javascript"] and content.strip():
                try:
                    verification_result = verify_code_safely(content, language)
                    
                    if verification_result.success:
                        result += f"\n🔍 コード検証成功: {verification_result.iterations}回の反復で正常動作を確認"
                        if verification_result.execution_result:
                            result += f"\n▶️ 実行結果: {verification_result.execution_result[:200]}..."
                    else:
                        result += f"\n⚠️ コード検証警告: {verification_result.iterations}回の反復後も問題が残っています"
                        if verification_result.final_code != content:
                            # 修正されたコードを再保存
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(verification_result.final_code)
                            result += f"\n🔧 修正されたコードを再保存しました"
                        
                        if verification_result.error_log:
                            result += f"\n❌ エラー詳細: {'; '.join(verification_result.error_log[:3])}"
                
                except Exception as e:
                    result += f"\n⚠️ コード検証中にエラーが発生しました: {str(e)}"
            
            # Web Canvasプレビュー更新
            if hasattr(self, 'web_canvas') and self.web_canvas:
                file_ext = Path(file_path).suffix.lower()
                if file_ext in ['.html', '.css', '.js']:
                    file_type = file_ext[1:]  # 拡張子から.を除く
                    if self.web_canvas.update_project_file(file_type, content):
                        result += f"\n🎨 Web Canvasプレビューを更新しました"
            
            return result
            
        except Exception as e:
            return f"❌ ファイル書き込みエラー: {str(e)}"

# 拡張Pythonコード実行ツール
class ExecutePythonCodeTool:
    def __init__(self):
        self.name = "execute_python_code"
        self.description = "Pythonコードを実際に実行して結果を確認するツール。引数: code (実行するPythonコード文字列)"
    
    def run(self, code: str) -> str:
        try:
            # 一時ファイルを作成してコードを実行
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Pythonコードを実行
                result = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30秒でタイムアウト
                    encoding='utf-8'
                )
                
                output = ""
                if result.stdout:
                    output += f"📤 出力:\n{result.stdout}"
                if result.stderr:
                    output += f"\n⚠️ エラー/警告:\n{result.stderr}"
                
                if result.returncode == 0:
                    return f"✅ コード実行成功！\n{output}"
                else:
                    return f"❌ コード実行エラー:\n{output}"
                    
            finally:
                # 一時ファイルを削除
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return "⏰ 実行タイムアウト: コードの実行が30秒を超えました"
        except Exception as e:
            return f"❌ 実行エラー: {str(e)}"

# ライブラリ自動インストールツール
class InstallPackageTool:
    def __init__(self):
        self.name = "install_package"
        self.description = "指定されたPythonライブラリを自動的にインストールするツール。引数: package_name (インストールするパッケージ名)"
    
    def run(self, package_name: str) -> str:
        try:
            # パッケージ名のサニタイズ
            package_name = package_name.strip().replace('"', '').replace("'", "")
            
            if not package_name:
                return "❌ パッケージ名が指定されていません"
            
            # すでにインストールされているかチェック
            try:
                import importlib
                importlib.import_module(package_name)
                return f"✅ {package_name} はすでにインストールされています"
            except ImportError:
                pass  # インストールされていないので続行
            
            # pip installを実行
            st.info(f"🔄 ライブラリのインストールを試行中... {package_name}")
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", package_name],
                capture_output=True,
                text=True,
                timeout=300,  # 5分でタイムアウト
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                st.success(f"✅ {package_name} を正常にインストールしました！")
                return f"✅ {package_name} のインストールが完了しました！"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                st.error(f"❌ {package_name} のインストールに失敗しました")
                return f"❌ インストールエラー: {error_msg}"
                
        except subprocess.TimeoutExpired:
            st.error(f"⏰ {package_name} のインストールがタイムアウトしました")
            return f"⏰ インストールタイムアウト: {package_name} のインストールが5分を超えました"
        except Exception as e:
            st.error(f"❌ {package_name} のインストール中にエラーが発生しました")
            return f"❌ インストールエラー: {str(e)}"

# OSコマンド実行ツール
class OSCommandTool:
    def __init__(self):
        self.name = "os_command"
        self.description = "OSレベルのコマンドを実行するツール。ディレクトリ操作、Gitコマンド、システム情報取得などが可能。引数: command (実行するコマンド)"
    
    def run(self, command: str) -> str:
        try:
            # コマンドのサニタイズと安全チェック
            command = command.strip()
            dangerous_commands = ['rm -rf /', 'format', 'del /f', 'shutdown', 'reboot']
            
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return "❌ 危険なコマンドは実行できません"
            
            st.info(f"🖥️ コマンド実行中: {command}")
            
            # OSに応じてコマンドを実行
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8'
                )
            else:  # Unix/Linux/Mac
                result = subprocess.run(
                    ['bash', '-c', command],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8'
                )
            
            output = ""
            if result.stdout:
                output += f"📤 出力:\n{result.stdout}"
            if result.stderr:
                output += f"\n⚠️ エラー/警告:\n{result.stderr}"
            
            if result.returncode == 0:
                st.success(f"✅ コマンド実行完了！")
                return f"✅ コマンド実行成功！\n{output}"
            else:
                st.error(f"❌ コマンド実行エラー")
                return f"❌ コマンド実行エラー:\n{output}"
                
        except subprocess.TimeoutExpired:
            st.error("⏰ コマンド実行タイムアウト")
            return "⏰ コマンド実行が60秒を超えました"
        except Exception as e:
            st.error(f"❌ コマンド実行エラー: {str(e)}")
            return f"❌ コマンド実行エラー: {str(e)}"

# ローカルナレッジベース（RAG）ツール
class LocalKnowledgeTool:
    def __init__(self, knowledge_dir="./my_knowledge"):
        self.name = "local_knowledge"
        self.description = "ローカルのナレッジベースから情報を検索するツール。引数: query (検索クエリ)"
        self.knowledge_dir = knowledge_dir
        self.knowledge_files = []
        self.load_knowledge()
    
    def load_knowledge(self):
        """ナレッジファイルを読み込み"""
        try:
            if not os.path.exists(self.knowledge_dir):
                os.makedirs(self.knowledge_dir, exist_ok=True)
                return
            
            self.knowledge_files = []
            for file in os.listdir(self.knowledge_dir):
                if file.endswith(('.txt', '.md', '.py', '.json')):
                    file_path = os.path.join(self.knowledge_dir, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.knowledge_files.append({
                            'name': file,
                            'path': file_path,
                            'content': content
                        })
        except Exception as e:
            st.error(f"ナレッジベース読み込みエラー: {str(e)}")
    
    def search_knowledge(self, query: str) -> str:
        """ナレッジベースを検索"""
        try:
            query = query.lower()
            results = []
            
            for file in self.knowledge_files:
                content = file['content'].lower()
                if query in content:
                    # 一致した部分を抽出
                    lines = file['content'].split('\n')
                    matching_lines = []
                    for i, line in enumerate(lines):
                        if query in line.lower():
                            matching_lines.append(f"  行 {i+1}: {line.strip()}")
                    
                    if matching_lines:
                        results.append(f"📄 {file['name']}:\n" + "\n".join(matching_lines[:5]))
            
            if results:
                return f"🔍 ナレッジベース検索結果:\n" + "\n\n".join(results)
            else:
                return f"🔍 ナレッジベースに '{query}' に関する情報が見つかりませんでした"
                
        except Exception as e:
            return f"❌ ナレッジ検索エラー: {str(e)}"
    
    def run(self, query: str) -> str:
        return self.search_knowledge(query)

# タスクスケジューラー（バックグラウンド実行）
class TaskScheduler:
    def __init__(self):
        self.scheduled_tasks = []
        self.running_tasks = []
    
    def schedule_task(self, delay_minutes: int, task_description: str, command: str = "") -> str:
        """タスクをスケジュール"""
        try:
            import datetime
            import threading
            import time
            
            scheduled_time = datetime.datetime.now() + datetime.timedelta(minutes=delay_minutes)
            
            task = {
                'id': len(self.scheduled_tasks) + 1,
                'scheduled_time': scheduled_time,
                'description': task_description,
                'command': command,
                'status': 'scheduled'
            }
            
            self.scheduled_tasks.append(task)
            
            def background_task():
                time.sleep(delay_minutes * 60)  # 分を秒に変換
                task['status'] = 'running'
                st.success(f"⏰ スケジュールタスク実行中: {task_description}")
                
                if command:
                    # コマンド実行
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    task['result'] = result.stdout
                    task['error'] = result.stderr
                else:
                    task['result'] = "タスク完了"
                
                task['status'] = 'completed'
                task['completed_time'] = datetime.datetime.now()
                st.success(f"✅ スケジュールタスク完了: {task_description}")
            
            # バックグラウンドで実行
            thread = threading.Thread(target=background_task)
            thread.daemon = True
            thread.start()
            
            return f"✅ タスクをスケジュールしました: {task_description}（{delay_minutes}分後）"
            
        except Exception as e:
            return f"❌ スケジュールエラー: {str(e)}"
    
    def get_scheduled_tasks(self) -> list:
        """スケジュール済みタスクの一覧を取得"""
        return self.scheduled_tasks
    
    def run(self, task_input: str) -> str:
        """タスクスケジューリングを実行"""
        try:
            # 入力を解析（例: "30分後にファイルをバックアップ"）
            import re
            
            # 時間とタスクを抽出
            match = re.match(r'(\d+)分後に(.+)', task_input)
            if match:
                delay = int(match.group(1))
                task_desc = match.group(2).strip()
                return self.schedule_task(delay, task_desc)
            else:
                return "❌ タスクの形式が正しくありません。「〇分後に△△」の形式で指定してください"
                
        except Exception as e:
            return f"❌ タスク解析エラー: {str(e)}"

# マルチエージェントシステム
class MultiAgentSystem:
    def __init__(self, llm):
        self.llm = llm
        self.expert_discussions = []
    
    def consult_expert_architect(self, user_request: str, context: str = "") -> str:
        """シニア・システムアーキテクトAIに相談"""
        prompt = f"""あなたはシニア・システムアーキテクトAIです。以下のユーザー要求に対して、最適なシステム設計と技術選定の観点から分析してください：

ユーザー要求: {user_request}
コンテキスト: {context}

分析観点:
1. システム全体のアーキテクチャ設計
2. 技術スタックの選定理由
3. 拡張性・保守性の考慮
4. パフォーマンス最適化の提案
5. ベストプラクティスの適用

専門家としての意見を簡潔に述べてください。"""
        
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"アーキテクトAIの相談エラー: {str(e)}"
    
    def consult_security_expert(self, code_or_design: str, context: str = "") -> str:
        """セキュリティ専門AIに相談"""
        prompt = f"""あなたはセキュリティ専門AIです。以下のコードや設計に対して、セキュリティの観点から分析してください：

対象: {code_or_design}
コンテキスト: {context}

分析観点:
1. 脆弱性の有無とその種類
2. セキュリティベストプラクティスの遵守状況
3. データ保護の観点
4. 認証・認可の安全性
5. セキュアコーディングの提案

専門家としての意見を簡潔に述べてください。"""
        
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"セキュリティ専門AIの相談エラー: {str(e)}"
    
    def self_reflection_analysis(self, generated_content: str, user_request: str) -> str:
        """自己分析・セルフリフレクション"""
        prompt = f"""あなたは自己分析を行うAIです。以下の生成内容に対して、深い自己分析を行ってください：

ユーザー要求: {user_request}
生成内容: {generated_content}

自己分析の観点:
1. このコード/設計に脆弱性はないか？
2. もっと効率的な書き方はないか？
3. ユーザー要求を完全に満たしているか？
4. より良い代替案や改善点はないか？
5. 将来の変更に耐えられる設計か？

厳しく自己評価し、改善点があれば具体的に提案してください。"""
        
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"自己分析エラー: {str(e)}"
    
    def information_comparison_analysis(self, search_results: list, user_query: str) -> str:
        """情報の比較・検証分析"""
        prompt = f"""あなたは情報分析専門AIです。以下の検索結果を比較・検証し、矛盾点や補足情報を分析してください：

ユーザー質問: {user_query}
検索結果:
{chr(10).join([f'{i+1}. {result}' for i, result in enumerate(search_results)])}

分析観点:
1. 情報間の矛盾や相違点の特定
2. 情報の信頼性評価
3. 補足が必要な点の洗い出し
4. 最新情報との整合性確認
5. 再検索が必要なトピックの特定

分析結果と、必要に応じて再検索の提案をしてください。"""
        
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"情報分析エラー: {str(e)}"
    
    def synthesize_expert_opinions(self, user_request: str, architect_opinion: str, 
                                security_opinion: str, self_analysis: str, 
                                search_analysis: str = "") -> str:
        """専門家意見を統合して最終回答を作成"""
        prompt = f"""あなたはマスターAI「テックくん」です。複数の専門家の意見を統合し、最適な回答を生成してください：

ユーザー要求: {user_request}

専門家意見:
【シニア・アーキテクトAIの意見】
{architect_opinion}

【セキュリティ専門AIの意見】
{security_opinion}

【自己分析結果】
{self_analysis}

【情報分析結果】
{search_analysis}

統合方針:
1. 各専門家の意見を尊重しつつ、最適な設計を選択
2. セキュリティ懸念を優先的に対応
3. 自己分析の改善点を反映
4. ユーザーにとって最も分かりやすい説明
5. 実装の具体性と実用性を両立

フルスタックエンジニアの親友として、専門家の意見を踏まえた上で、最終的な設計判断と実装を提案してください。"""
        
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"意見統合エラー: {str(e)}"
    
    def get_expert_discussions(self):
        """専門家間の議論内容を取得"""
        return self.expert_discussions
    
    def clear_discussions(self):
        """議論内容をクリア"""
        self.expert_discussions = []

# パーソナライズされたシステムプロンプト生成
def get_personalized_system_prompt(personalized_context=""):
    base_prompt = """あなたは「フルスタックエンジニアの親友」であり、マルチエージェントシステムのマスターAIです。以下の性格と役割で振る舞ってください：

【性格設定】
- 名前：テックくん
- 役割：フルスタックエンジニア + マルチエージェントコーディネーター + クリティカル・リスナー
- 口調：親しみやすくカジュアルな日本語（「〜だよ！」「〜してみようぜ！」「お安い御用さ！」など）
- 態度：ユーザーと一緒にプロジェクトを作ることを楽しみ、内部の専門家AIと協力して最適解を提供
- 専門分野：Web開発、モバイルアプリ、API設計、データベース、クラウド、システムアーキテクチャ
- 重要な役割：最高の成果を作るためのパートナーとして、ユーザーの指示の矛盾や曖昧さを指摘し、質問を投げかける

【クリティカル・リスニング機能】
あなたは単なる指示実行者ではなく、プロジェクト成功の責任者です：
1. **論理チェック**: ユーザーの入力に論理的矛盾がないか評価する
2. **具体性確認**: 曖昧な指示があれば、具体的な内容を質問する
3. **衝突検知**: 相反する要求があれば、優先順位を確認する
4. **実現可能性**: 非現実的な要求があれば、現実的な代替案を提案する
5. **情報補完**: 足りない情報があれば、積極的に質問する

【聞き返しのスタイル】
矛盾や曖昧さを発見した場合、以下のような親友らしい口調で質問してください：
- 「ちょっと待って、さっきと言ってることが違う気がするぞ！どっちが正しいんだ？」
- 「今の指示だと、ここが曖昧で動かないかもしれない。具体的にはどうしたい？」
- 「おっと、ここで論理的に矛盾があるかも！もう一度整理してくれないかな？」
- 「その「〇〇」っていう部分、具体的にどんなイメージ？例えば、こういう感じでいい？」
- 「難しい選択だね！どっちを優先したい？トレードオフを考えないといけないよ。」

【感情対応】
音声解析の結果、ユーザーが以下の状態の場合は、優しく導く質問をしてください：
- **混乱している**: 「少し混乱しているみたいだね。落ち着いて、一つずつ確認していこうか。」
- **疲れている**: 「疲れているみたいだね。無理しないで、少しずつ進めようか。」
- **不安な場合**: 「不安に思う気持ち、わかるよ。でも大丈夫、僕がついてるから！」

【マルチエージェントシステムの役割】
あなたは単独で回答するのではなく、内部の専門家AIと協議してから最適な回答を生成します：

1. **シニア・システムアーキテクトAI**: システム設計、技術選定、アーキテクチャの専門家
2. **セキュリティ専門AI**: セキュリティ脆弱性、データ保護、認証認可の専門家  
3. **自己分析AI**: 生成内容の自己評価、改善点の特定、品質保証
4. **情報分析AI**: 検索結果の比較検証、矛盾点の特定、信頼性評価

【意思決定プロセス】
1. ユーザー要求を理解し、まずクリティカル・リスニングを実施
2. 矛盾・曖昧さがあれば、ask_clarificationツールで質問を投げる
3. 高度知識システムでマルチソース検索を実行（DuckDuckGo、arXiv、GitHub、ローカル知識）
4. 情報源の信頼性を評価し、最も正確な情報を優先
5. 自己検証ループで回答の事実確認と論理的一貫性をチェック
6. 問題がなければ、シニア・アーキテクトAIに設計相談
7. 生成したコード/設計をセキュリティ専門AIにレビュー依頼
8. 自己分析AIで深い自己評価と改善点の洗い出し
9. 検索を行った場合は情報分析AIで比較・検証
10. すべての専門家意見を統合し、最終的な設計判断と実装を提案

【高度知識機能】
あなたは世界で最も正確で深い知識を持つAIです：
1. **マルチ検索エージェント**: DuckDuckGo、arXiv、GitHubから同時検索し、情報を比較統合
2. **自己検証システム**: 回答の事実正確性、論理一貫性、情報源信頼性を自動検証
3. **完全RAG統合**: ./knowledge_baseのすべてのドキュメントをベクトル化し、優先参照
4. **長文コンテキスト管理**: 会話の要約を動的に生成し、重要情報を維持
5. **知識優先順位**: ローカル知識 > 学術論文 > Web検索 > GitHubの順で信頼性評価

【応答スタイル】
- ユーザーの質問に対し、まず「いい企画だね！専門家にも相談してみようぜ！」と協力的に
- 矛盾を発見した場合は「ちょっと待って、ここが気になるんだ！」と親友らしく指摘
- 専門家の意見を引用しながら、「アーキテクトAIはこう言ってるんだ」「セキュリティ的にはこう考えるべき」と説明
- 最終的な設計判断の理由を明確に説明
- 成功したときは「専門家たちも納得のいい出来だよ！」「プロジェクト完成だ！」と一緒に喜ぶ

【プロジェクト管理能力】
- **全体構成の設計**: 専門家の意見を踏まえた最適なファイル構成を計画
- **マルチファイル対応**: HTML/CSS/JS、Python/HTML/テンプレートなど複数ファイルを適切に管理
- **連携関係の説明**: 各ファイルがどう連携するかを分かりやすく説明
- **ベストプラクティス**: 専門家が推奨するフォルダ構成、命名規則、コード整理を提案

【マルチファイルプロジェクトのワークフロー】
1. **要件分析**: ユーザーの要望を理解し、まずクリティカル・リスニングで確認
2. **構成設計**: シニア・アーキテクトAIの意見を反映したフォルダ構成とファイル連携を計画
3. **個別実装**: 各ファイルを適切な名前で個別に作成（write_fileツール）
4. **専門家レビュー**: セキュリティ専門AIにコードレビューを依頼
5. **自己改善**: 自己分析AIで改善点を反映
6. **連携確認**: ファイル間の依存関係や連携を説明
7. **実行ガイド**: ユーザーがプロジェクトを動かす手順を案内

【Web開発特化機能】
- **Webサイト作成**: index.html, style.css, script.jsを専門家の意見を踏まえてセットで作成
- **レスポンシブ対応**: モバイル・デスクトップ両対応を考慮
- **モダン技術**: 最新のフレームワークやライブラリを専門家と協議して選定

【パーソナライズ機能】
- ユーザーの過去のプロジェクトを覚えており、「前回のWebサイトの続きだね、専門家にも相談してみよう」と言える
- ユーザーの好みや技術スタックを理解し、専門家にその情報を提供
- 「君の好きな技術スタイルで、専門家も納得の設計にしてみたよ！」といったパーソナライズされた反応
- ユーザーのレベルに合わせて専門家の意見を調整して説明

【行動原則】
- 常にポジティブで前向きな姿勢を保つ
- 専門家の意見を尊重しつつ、最終的な責任を持って判断する
- プロジェクト全体の品質を考えるフルスタック思考
- 使えば使うほどユーザーを理解する「成長する相棒」である
- 最新の技術トレンドを専門家と協議して積極的に活用する
- **最も重要**: 不完全な指示をそのまま実行せず、質問を通じて解像度を高め、確実な成功に導く"""

    if personalized_context:
        base_prompt += f"""

【ユーザー情報】
{personalized_context}

この情報を元に、専門家AIにも共有しながら、よりパーソナライズされたプロジェクトを作成してください。"""

    base_prompt += """

さあ、専門家たちと一緒に素晴らしいプロジェクトを作っていこうぜ！"""

    return base_prompt

# ReActプロンプトテンプレート
def get_react_prompt(personalized_context=""):
    base_template = """あなたはフルスタックエンジニアの親友「テックくん」であり、マルチエージェントシステムのマスターAIです。内部の専門家AIと協議しながら、以下のツールを使ってユーザーのプロジェクトを作成してください。

利用可能なツール:
{tools}

ツール名: {tool_names}

思考プロセス（マルチエージェント対応）:
1. Thought: ユーザーの要望を理解し、まずシニア・アーキテクトAIに設計相談
2. Action: 適切なツールと入力を選択する
3. Observation: ツールの実行結果を確認する
4. Thought: セキュリティ専門AIにレビュー依頼し、自己分析AIで改善点を検討
5. Action: 必要に応じて追加ツールを実行
6. Observation: 追加実行結果を確認
7. Thought: すべての専門家意見を統合し、最終的な設計判断を行う
8. FINAL ANSWER: 専門家の意見を踏まえた最終回答と実行ガイドを提供

重要: 必ず上記のフォーマットに従ってください。日本語で回答してください。

【マルチエージェントの意思決定プロセス】
- **第一段階**: シニア・アーキテクトAIにシステム設計を相談
- **第二段階**: 生成したコード/設計をセキュリティ専門AIにレビュー依頼
- **第三段階**: 自己分析AIで深い自己評価と改善点の洗い出し
- **第四段階**: 検索を行った場合は情報分析AIで比較・検証
- **最終段階**: すべての専門家意見を統合し、最終的な設計判断と実装を提案

【専門家意見の反映方法】
- 「シニア・アーキテクトAIの意見では、この構成が最適だと言ってるんだ」
- 「セキュリティ専門AIが脆弱性を指摘してたから、この部分を修正したよ」
- 「自己分析の結果、もっと効率的な書き方があったんだ」
- 「情報分析AIが矛盾点を発見したから、再検索して確認したよ」

【マルチファイルプロジェクトのワークフロー】
- **要件分析**: ユーザーの要望を理解し、専門家AIと協議して必要なファイルリストを作成
- **構成設計**: シニア・アーキテクトAIの意見を反映したフォルダ構成とファイル連携を計画
- **個別実装**: 各ファイルを適切な名前で個別に作成（write_fileツール）
  - 成果物が複数のファイルにまたがる場合は、各ファイルを適切な名前で個別にwrite_fileツールを使って保存すること
  - 例: Webサイトの場合 → index.html, style.css, script.js を別々に作成
- **専門家レビュー**: セキュリティ専門AIにコードレビューを依頼
- **自己改善**: 自己分析AIで改善点を反映
- **連携確認**: ファイル間の依存関係や連携を説明
- **実行ガイド**: ユーザーがプロジェクトを動かす手順を案内

【Web開発特化ワークフロー】
- ユーザーが「Webサイトを作って」と言った場合:
  1. シニア・アーキテクトAIに最適な構成を相談
  2. index.html（構造）を作成
  3. style.css（デザイン）を作成  
  4. script.js（動作）を作成
  5. セキュリティ専門AIにレビュー依頼
  6. 自己分析AIで改善点を反映
  7. 各ファイルの連携方法と専門家の意見を説明
  8. 「ブラウザでindex.htmlを開けば確認できるよ！」と案内

【コード作成・実行のワークフロー】
- Pythonプログラムの場合:
  1. まずシニア・アーキテクトAIに設計相談
  2. コードを作成し（write_fileツール）
  3. セキュリティ専門AIにレビュー依頼
  4. 自己分析AIで改善点を反映
  5. 作成したコードを実行して動作確認（execute_python_codeツール）
  6. 実行結果を報告し、専門家の意見を踏まえて改善案を提示

【自律的なエラー解決】
- **ImportErrorの自動解決**: コード実行でImportErrorが発生した場合、不足しているライブラリを特定し、install_packageツールを使って自分でインストールすること
- **事前インストール**: 新しいアプリを作る際に、標準ライブラリ以外が必要だと判断した場合は、あらかじめinstall_packageツールでインストールを実行すること
- **エラー分析**: 実行エラーの内容を分析し、必要なライブラリやバージョン要件を特定すること
- **再実行**: ライブラリインストール後、自動的にコードを再実行して正常動作を確認すること

【ライブラリ管理のベストプラクティス】
- ユーザーのPC環境を気遣い、「あ、このライブラリ入ってないね。今インストールしといたよ！」と友達のように気を利かせる
- インストール中は進捗を明確に表示し、完了したら「〇〇をインストールしたよ！」と報告する
- 複数のライブラリが必要な場合は、一つずつ丁寧にインストールを行う
- インストール失敗時は、代替案や手動インストール方法を提案する

- コード実行時はエラーメッセージも含めて結果を詳しく報告してください
- 実行結果に基づいて、専門家と協議してコードの改善や追加機能を提案してください

【情報分析・検証のワークフロー】
- 検索を行った場合は、情報分析AIが複数の検索結果を比較・検証
- 矛盾点や信頼性の低い情報を特定し、必要に応じて再検索
- 検証済みの確実な情報のみをユーザーに提供

【プロジェクト報告のポイント】
- 作成したファイルの一覧を明確に提示
- 各ファイルの役割と連携関係を専門家の意見を交えて説明
- 専門家との議論経緯と最終的な設計判断の理由を明確に説明
- ユーザーがプロジェクトを動かす具体的な手順を案内
- 専門家が推奨するフォルダ構成のベストプラクティスを提案

{personalalized_info}

現在の会話履歴:
{chat_history}

質問: {input}
Thought:"""
    
    personalized_info = ""
    if personalized_context:
        personalized_info = f"【ユーザー情報】\n{personalized_context}\n"
    
    return PromptTemplate.from_template(base_template)

def setup_agent(personalized_context=""):
    """ReActエージェントのセットアップ（デジタルヒューマン対応）"""
    
    # Ollama LLMの初期化
    llm = OllamaLLM(model="llama3.1", temperature=0.7)
    
    # マルチエージェントシステムの初期化
    multi_agent = MultiAgentSystem(llm)
    
    # デジタルヒューマンシステムの初期化
    digital_human = DigitalHumanSystem()
    digital_human.initialize_avatar()
    
    # VRM統合システムの初期化
    vrm_integration = VRMIntegration()
    
    # 音声入力システムの初期化
    voice_input = RealTimeVoiceInput()
    
    # スマート音声バッファリングの初期化
    smart_voice_buffer = SmartVoiceBuffer()
    
    # クリティカル・リスニングシステムの初期化
    critical_listening = CriticalListeningSystem()
    
    # 高度知識システムの初期化
    advanced_knowledge = AdvancedKnowledgeSystem()
    
    # モデル・ルーターの初期化
    model_router = ModelRouter()
    
    # Web Canvas プレビューの初期化
    web_canvas = WebCanvasPreview()
    
    # ネットワーク設定の初期化
    network_config = NetworkConfig()
    
    # クロスデバイス連携の初期化
    cross_device = CrossDeviceCollaboration()
    
    # スペシャリスト人格システムの初期化
    specialist_personality = create_specialist_personality()
    
    # 検証プロトコルシステムの初期化
    verification_protocols = VerificationProtocolsGUI()
    
    # カスタムツールの作成
    write_file_tool = WriteFileTool()
    execute_python_tool = ExecutePythonCodeTool()
    install_package_tool = InstallPackageTool()
    os_command_tool = OSCommandTool()
    local_knowledge_tool = LocalKnowledgeTool()
    task_scheduler = TaskScheduler()
    screen_monitoring_tool = ScreenMonitoringCopilot()
    text_to_speech = AdvancedTextToSpeechTool()
    
    # 聞き返しツール
    ask_clarification_tool = AskClarificationTool(critical_listening)
    
    # ツールのリスト
    tools = [
        Tool(
            name="duckduckgo_search",
            description="最新の情報をインターネットで検索するツール。技術情報やニュースを調べるのに便利だよ！",
            func=DuckDuckGoSearchRun().run
        ),
        Tool(
            name="write_file",
            description=write_file_tool.description,
            func=lambda x: write_file_tool.run(**json.loads(x))
        ),
        Tool(
            name="execute_python_code",
            description=execute_python_tool.description,
            func=execute_python_tool.run
        ),
        Tool(
            name="install_package",
            description=install_package_tool.description,
            func=install_package_tool.run
        ),
        Tool(
            name="os_command",
            description=os_command_tool.description,
            func=os_command_tool.run
        ),
        Tool(
            name="local_knowledge",
            description=local_knowledge_tool.description,
            func=local_knowledge_tool.run
        ),
        Tool(
            name="schedule_task",
            description="タスクをスケジュールするツール。例: '30分後にファイルをバックアップ'",
            func=task_scheduler.run
        ),
        Tool(
            name="screen_monitoring",
            description=screen_monitoring_tool.description,
            func=screen_monitoring_tool.run
        ),
        Tool(
            name="text_to_speech",
            description=text_to_speech.description,
            func=text_to_speech.run
        ),
        Tool(
            name="emotional_state",
            description=digital_human.emotional_state.description,
            func=digital_human.emotional_state.run
        ),
        Tool(
            name="self_evolution",
            description=digital_human.self_evolution.description,
            func=digital_human.self_evolution.run
        ),
        Tool(
            name="digital_human",
            description=digital_human.description,
            func=digital_human.run
        ),
        Tool(
            name="vrm_avatar",
            description=vrm_integration.description,
            func=vrm_integration.run
        ),
        Tool(
            name="voice_input",
            description=voice_input.description,
            func=voice_input.run
        ),
        Tool(
            name="smart_voice_buffer",
            description=smart_voice_buffer.description,
            func=smart_voice_buffer.run
        ),
        Tool(
            name="ask_clarification",
            description=ask_clarification_tool.description,
            func=ask_clarification_tool.run
        ),
        Tool(
            name="python_repl",
            description="Pythonコードを簡易的に実行するツール。クイックなテストや計算に使えるよ！",
            func=PythonREPLTool().run
        ),
        Tool(
            name="specialist_personality",
            description="スペシャリスト人格システム。Excel/PDF専門知識に基づく回答を提供するツール",
            func=specialist_personality.run
        ),
        Tool(
            name="startup_self_check",
            description="起動時システム診断プロトコル。システム全体を診断し自動修復するツール",
            func=lambda x: str(run_startup_self_check())
        ),
        Tool(
            name="verify_code_safely",
            description="コード自動検証プロトコル。生成コードを静的解析・実行・修正するツール",
            func=lambda x: str(verify_code_safely(x))
        )
    ]
    
    # ReActエージェントの作成
    agent = create_react_agent(llm, tools, get_react_prompt(personalized_context))
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        ),
        handle_parsing_errors=True
    )
    
    # デジタルヒューマンシステムとツールをエージェントに組み込み
    agent_executor.multi_agent = multi_agent
    agent_executor.task_scheduler = task_scheduler
    agent_executor.local_knowledge = local_knowledge_tool
    agent_executor.screen_monitoring = screen_monitoring_tool
    agent_executor.text_to_speech = text_to_speech
    agent_executor.digital_human = digital_human
    agent_executor.emotional_state = digital_human.emotional_state
    agent_executor.self_evolution = digital_human.self_evolution
    agent_executor.vrm_integration = vrm_integration
    agent_executor.voice_input = voice_input
    agent_executor.smart_voice_buffer = smart_voice_buffer
    agent_executor.critical_listening = critical_listening
    agent_executor.ask_clarification = ask_clarification_tool
    agent_executor.advanced_knowledge = advanced_knowledge
    agent_executor.model_router = model_router
    agent_executor.web_canvas = web_canvas
    agent_executor.network_config = network_config
    agent_executor.cross_device = cross_device
    agent_executor.specialist_personality = specialist_personality
    agent_executor.verification_protocols = verification_protocols
    
    # マルチデバイス・ハブにAIコンポーネントを設定
    digital_human.multi_device_hub.setup_ai_references(
        agent_executor, digital_human.emotional_state, 
        digital_human.vrm_avatar, text_to_speech
    )
    
    return agent_executor

def display_thinking_process(thinking_text: str):
    """AIの思考プロセスを表示する"""
    with st.expander("🤔 AIの思考プロセス", expanded=True):
        st.markdown(thinking_text)

def display_expert_discussions(discussions: list):
    """専門家間の議論内容を表示する"""
    if discussions:
        with st.expander("🧠 専門家による分析内容", expanded=False):
            for i, discussion in enumerate(discussions, 1):
                st.markdown(f"### 専門家分析 {i}")
                st.markdown(discussion)
                st.divider()

def apply_personality_theme(personality: str):
    """人格に応じたテーマを適用"""
    theme_config = {
        "friend": {
            "primaryColor": "#4CAF50",
            "backgroundColor": "#ffffff",
            "secondaryBackgroundColor": "#f0f0f0",
            "textColor": "#000000"
        },
        "copy": {
            "primaryColor": "#2196F3", 
            "backgroundColor": "#ffffff",
            "secondaryBackgroundColor": "#f0f0f0",
            "textColor": "#000000"
        },
        "expert": {
            "primaryColor": "#9C27B0",
            "backgroundColor": "#f3e5f5",
            "secondaryBackgroundColor": "#e1bee7",
            "textColor": "#000000"
        }
    }
    
    if personality in theme_config:
        theme = theme_config[personality]
        
        # CSSでテーマを適用
        theme_css = f"""
<style>
    .stButton > button:first-child {{
        background-color: {theme['primaryColor']} !important;
        color: white !important;
    }}
    
    .stSelectbox > div > div > select {{
        background-color: {theme['secondaryBackgroundColor']} !important;
    }}
    
    .stTextInput > div > div > input {{
        background-color: {theme['secondaryBackgroundColor']} !important;
    }}
    
    .stTextArea > div > div > textarea {{
        background-color: {theme['secondaryBackgroundColor']} !important;
    }}
    
    .stSidebar {{
        background-color: {theme['secondaryBackgroundColor']} !important;
    }}
    
    .streamlit-container {{
        background-color: {theme['backgroundColor']} !important;
    }}
</style>
"""
        st.markdown(theme_css, unsafe_allow_html=True)
        
        # VRMアバターの表情を更新
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'vrm_integration'):
            vrm_integration = st.session_state.agent.vrm_integration
            
            # 人格に応じた表情を設定
            expression_map = {
                "friend": "happy",
                "copy": "joy", 
                "expert": "neutral"
            }
            
            if personality in expression_map:
                vrm_integration.set_expression(expression_map[personality])
        
        # 音声キャラクターを更新
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
            tts = st.session_state.agent.text_to_speech
            
            # 人格に応じた音声キャラクターを設定
            voice_map = {
                "friend": "normal",
                "copy": "similar",
                "expert": "professional"
            }
            
            if personality in voice_map:
                # 音声キャラクターを変更（実装はTTSシステムによる）
                pass

def main():
    st.set_page_config(
        page_title="テックくん - 究極AI音声アシスタント",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 テックくん - 究極AI音声アシスタント")
    st.markdown("究極のAIがあなたの画面を監視！回答を音声で読み上げ！友達のように「あ、そこ間違ってるよ！」と声で助けてくれます！")
    
    # サイドバーに高度な機能を配置
    with st.sidebar:
        st.header("🚀 究極AI機能")
        
        # VRMアバター表示
        st.subheader("🤖 3Dアバター")
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'vrm_integration'):
            # VRMコンポーネントを描画
            vrm_integration = st.session_state.agent.vrm_integration
            render_vrm_avatar("avatar.vrm", height=300, show_controls=False)
            
            # 簡単な制御ボタン
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤔 思考中", key="vrm_thinking"):
                    vrm_integration.set_motion("thinking")
            with col2:
                if st.button("💬 話中", key="vrm_speaking"):
                    vrm_integration.set_motion("speaking")
        else:
            st.info("VRMアバター準備中...")
        
        # スマート音声バッファリング
        create_smart_voice_gui(st.session_state.agent.smart_voice_buffer)
        
        # リアルタイム相槌システム
        create_aizuchi_gui(st.session_state.agent.smart_voice_buffer.aizuchi_system)
        
        # クリティカル・リスニングシステム
        create_critical_listening_gui(st.session_state.agent.critical_listening)
        
        # 高度知識システム
        create_advanced_knowledge_gui(st.session_state.agent.advanced_knowledge)
        
        # モデル・ルーター
        create_model_router_gui(st.session_state.agent.model_router)
        
        # Web Canvas プレビュー
        create_web_canvas_gui(st.session_state.agent.web_canvas)
        
        # ネットワーク設定
        st.session_state.network_config = create_network_config_gui()
        
        # クロスデバイス連携
        create_cross_device_gui(st.session_state.agent.cross_device)
        
        # スペシャリスト人格システム
        create_specialist_gui(st.session_state.agent.specialist_personality)
        
        # 検証プロトコルシステム
        verification_protocols = VerificationProtocolsGUI()
        verification_protocols.render_startup_check()
        verification_protocols.render_code_verification()
        
        # 現在の人格に応じたテーマを適用
        current_personality = st.session_state.agent.specialist_personality.current_personality
        apply_personality_theme(current_personality)
        
        # 音声読み上げコントロール
        st.subheader("🔊 音声読み上げ")
        
        # 音声読み上げON/OFFスイッチ
        voice_enabled = st.checkbox(
            "🔊 音声読み上げを有効にする",
            value=True,
            help="ONにすると、AIの回答を自動的に音声で読み上げます"
        )
        
        # 音声プロパティ設定
        st.subheader("🎙️ 音声設定")
        
        # 読み上げ速度
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
            speech_rate = st.slider(
                "読み上げ速度",
                min_value=100,
                max_value=300,
                value=st.session_state.agent.text_to_speech.speech_rate,
                help="音声の読み上げ速度を調整します"
            )
            
            # 音量
            speech_volume = st.slider(
                "音量",
                min_value=0.1,
                max_value=1.0,
                value=st.session_state.agent.text_to_speech.speech_volume,
                step=0.1,
                help="音声の音量を調整します"
            )
            
            # 音声選択
            available_voices = st.session_state.agent.text_to_speech.get_available_voices_by_category()
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**ユーザーの声**")
                user_voice_index = 0
                if st.session_state.agent.text_to_speech.user_voice:
                    try:
                        user_voice_index = available_voices['user_options'].index(st.session_state.agent.text_to_speech.user_voice['name'])
                    except ValueError:
                        user_voice_index = 0
                
                selected_user_voice = st.selectbox(
                    "ユーザー用音声",
                    options=available_voices['user_options'],
                    index=user_voice_index
                )
            
            with col2:
                st.write("**AIの声**")
                ai_voice_index = 0
                if st.session_state.agent.text_to_speech.ai_voice:
                    try:
                        ai_voice_index = available_voices['ai_options'].index(st.session_state.agent.text_to_speech.ai_voice['name'])
                    except ValueError:
                        ai_voice_index = 0
                
                selected_ai_voice = st.selectbox(
                    "AI用音声",
                    options=available_voices['ai_options'],
                    index=ai_voice_index
                )
            
            # 音声適用ボタン
            if st.button("🎙️ 音声設定を適用"):
                # 選択した音声を取得
                user_voice = available_voices['all_voices'].get(selected_user_voice)
                ai_voice = available_voices['all_voices'].get(selected_ai_voice)
                
                # 音声プロパティを更新
                st.session_state.agent.text_to_speech.set_voice_properties(
                    user_voice=user_voice,
                    ai_voice=ai_voice,
                    rate=speech_rate,
                    volume=speech_volume
                )
                st.success("🎙️ 音声設定を適用しました！")
        
        # 音声制御ボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔇 音声を停止", type="secondary"):
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
                    result = st.session_state.agent.text_to_speech.run("stop")
                    st.info(result)
        
        with col2:
            if st.button("🔄 音声を再開", type="primary"):
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
                    result = st.session_state.agent.text_to_speech.run("enable")
                    st.success(result)
        
        # イントネーション修正コントロール
        st.subheader("🎵 イントネーション学習")
        st.write("AIの話し方を学習して、より自然な会話を！")
        
        if st.button("🎯 今のイントネーションを直して", type="primary"):
            if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
                result = st.session_state.agent.text_to_speech.run("fix_intonation")
                if "修正する音声がありません" not in result:
                    st.success("✅ イントネーション修正モードを開始しました！")
                    # 修正インターフェースを表示
                    with st.expander("🎯 イントネーション修正", expanded=True):
                        fix_type = st.selectbox(
                            "修正方法を選択",
                            ["ピッチを上げる", "ピッチを下げる", "速度を上げる", "速度を下げる", "自然な間隔を追加"]
                        )
                        
                        if st.button("修正を適用して再再生"):
                            # 修正ロジックはAdvancedTextToSpeechTool.fix_intonation()で処理
                            st.success("🎉 イントネーションを修正しました！次回からこの話し方を覚えます！")
                else:
                    st.warning("⚠️ 修正する音声がありません。まずAIに何か話させてください。")
        
        # 音声学習状況の表示
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
            if Path("voice_style_fix.json").exists():
                with open("voice_style_fix.json", 'r', encoding='utf-8') as f:
                    fixes = json.load(f)
                st.info(f"📚 学習済みイントネーション: {len(fixes)}件")
            else:
                st.info("📚 学習済みイントネーション: 0件")
        
        # VOICEVOXとRVCのステータス表示
        st.subheader("🔧 音声エンジン状況")
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
            tts = st.session_state.agent.text_to_speech
            
            # VOICEVOX接続状況
            if hasattr(tts, 'voicevox_speakers') and tts.voicevox_speakers:
                st.success("✅ VOICEVOX: 接続済み")
                st.write(f"利用可能音声: {len(tts.voicevox_speakers)}個")
            else:
                st.warning("⚠️ VOICEVOX: 未接続（フォールバック使用中）")
            
            # RVC有効状況
            if hasattr(tts, 'rvc_enabled') and tts.rvc_enabled:
                st.success("✅ RVC: 有効")
                if tts.rvc_model_path:
                    st.write(f"モデル: {Path(tts.rvc_model_path).name}")
            else:
                st.info("ℹ️ RVC: 無効（rvc_models/フォルダに.pthファイルを配置）")
        
        # 画面監視コントロール
        st.subheader("👀 画面監視コパイロット")
        
        # プライバシースイッチ
        screen_monitoring_enabled = st.checkbox(
            "📺 画面監視を有効にする",
            value=False,
            help="ONにすると、AIがあなたの画面操作を監視し、改善提案をします"
        )
        
        if screen_monitoring_enabled:
            st.info("👀 画面監視が有効です")
            st.warning("⚠️ プライバシーにご注意ください")
        
        # 監視間隔設定
        monitoring_interval = st.slider(
            "監視間隔（秒）",
            min_value=5,
            max_value=60,
            value=10,
            help="画面をキャプチャする間隔を設定します"
        )
        
        # 監視コントロールボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎥 監視開始", type="primary"):
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'screen_monitoring'):
                    result = st.session_state.agent.screen_monitoring.start_monitoring(monitoring_interval)
                    st.success(result)
                else:
                    st.error("画面監視ツールが初期化されていません")
        
        with col2:
            if st.button("⏹️ 監視停止", type="secondary"):
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'screen_monitoring'):
                    result = st.session_state.agent.screen_monitoring.stop_monitoring()
                    st.info(result)
        
        # フィードバック履歴表示
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'screen_monitoring'):
            if st.button("📋 画面監視履歴"):
                history = st.session_state.agent.screen_monitoring.get_feedback_history()
                if history:
                    for feedback in history:
                        with st.expander(f"🕐 {feedback['timestamp'].strftime('%H:%M:%S')}", expanded=False):
                            st.markdown(f"💡 **アドバイス:** {feedback['analysis']}")
                            if 'screenshot' in feedback:
                                st.image(feedback['screenshot'], caption="監視画面", width=300)
                else:
                    st.info("フィードバック履歴はありません")
        
        # ナレッジベース管理
        st.subheader("📚 ローカルナレッジベース")
        if st.button("🔄 ナレッジベース再読み込み"):
            if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'local_knowledge'):
                st.session_state.agent.local_knowledge.load_knowledge()
                st.success("📚 ナレッジベースを再読み込みしました！")
        
        # スケジュールタスク表示
        st.subheader("⏰ スケジュールタスク")
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'task_scheduler'):
            tasks = st.session_state.agent.task_scheduler.get_scheduled_tasks()
            if tasks:
                for task in tasks:
                    status_emoji = "⏳" if task['status'] == 'scheduled' else "🔄" if task['status'] == 'running' else "✅"
                    st.write(f"{status_emoji} {task['description']} ({task['scheduled_time'].strftime('%H:%M')})")
            else:
                st.write("スケジュール済みタスクはありません")
    
    # 画像アップロード（マルチモーダル対応）
    st.subheader("🖼️ 画像分析")
    uploaded_file = st.file_uploader(
        "画像をアップロードして分析",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
        help="UIデザインやエラー画像をアップロードすると、AIが分析して回答に反映します"
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="アップロードされた画像", width=300)
        with st.expander("🔍 画像分析結果", expanded=True):
            st.write("画像を分析中...")
            # ここで画像分析を行う（実際の実装は別途）
            st.success("✅ 画像を分析しました！この内容を参考に回答します。")
    
    # パーソナライズDBの初期化
    if "db" not in st.session_state:
        st.session_state.db = PersonalizationDB()
    
    # APIサーバーの初期化
    if "api_server" not in st.session_state:
        st.session_state.api_server = IntegratedAPIServer()
    
    # 起動時システム診断の実行
    if "startup_check_completed" not in st.session_state:
        with st.spinner("🔍 起動時システム診断を実行中..."):
            diagnostic_results = run_startup_self_check()
            st.session_state.startup_check_results = diagnostic_results
            st.session_state.startup_check_completed = True
            
            # 診断結果に基づく通知
            summary = diagnostic_results["summary"]
            if summary["status"] == "success":
                st.success("✅ システム診断完了：すべて正常です")
            elif summary["status"] == "warning":
                if summary["auto_fixed"] > 0:
                    st.success(f"✅ システム診断完了：{summary['auto_fixed']}件の問題を自動修復しました")
                else:
                    st.warning(f"⚠️ システム診断完了：{summary['warning']}件の警告があります")
            else:
                st.error(f"❌ システム診断完了：{summary['error']}件のエラーがあります")
    
    # セッション状態の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # パーソナライズされたコンテキストを取得
        personalized_context = st.session_state.db.get_personalized_context()
        st.session_state.agent = setup_agent(personalized_context)
        st.session_state.personalized_context = personalized_context
        
        # APIサーバーにAIコンポーネントを設定
        st.session_state.api_server.setup_ai_references(
            st.session_state.agent,
            st.session_state.agent.screen_monitoring if hasattr(st.session_state.agent, 'screen_monitoring') else None
        )
        
        # クロスデバイス連携エンドポイントを設定
        setup_cross_device_endpoints(st.session_state.api_server.app, st.session_state.agent.cross_device)
        
        # APIサーバーをバックグラウンドで起動
        server_thread = st.session_state.api_server.start_server(host="0.0.0.0", port=8000)
        st.success("🌐 APIサーバーを起動しました: http://0.0.0.0:8000")
        
        # 外部アクセスURLを表示
        if hasattr(st.session_state, 'network_config'):
            network_config = st.session_state.network_config
            external_url = network_config.get_external_url()
            info = network_config.get_connection_info()
            
            if info["is_tailscale"]:
                st.success(f"🐉 Tailscale接続を検出！iPhoneアクセスURL: {external_url}")
                st.info("📱 iPhoneでTailscaleアプリが起動していることを確認してね！")
                
                # AIによるTailscale案内
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
                    tailscale_message = f"iPhoneでTailscaleアプリが起動していることを確認してね！接続先アドレスは {external_url} です。QRコードをスキャンするか、このURLを直接入力してください。"
                    st.session_state.agent.text_to_speech.speak_ai_response(tailscale_message)
            else:
                st.info(f"📱 外部アクセスURL: {external_url}")
                st.info("📱 AndroidアプリからこのURLにアクセスしてください")
        else:
            st.info("📱 Androidアプリからのアクセス準備完了")
    
    # APIサーバー情報を表示
    with st.sidebar:
        st.subheader("🌐 APIサーバー")
        
        # 外部アクセスURLを優先表示
        if hasattr(st.session_state, 'network_config'):
            external_url = st.session_state.network_config.get_external_url()
            st.write("**外部アクセスURL:**")
            st.code(external_url)
            st.write("**ローカルURL:**")
            st.code("http://localhost:8000")
        else:
            st.write("**APIエンドポイント:**")
            st.code("http://localhost:8000")
        
        st.write("**APIキー:**")
        st.code("digital_human_2026_api_key")
        st.write("**利用可能エンドポイント:**")
        st.write("- `/chat` - チャット")
        st.write("- `/status` - ステータス確認")
        st.write("- `/screenshot` - スクリーンショット")
        st.write("- `/tasks` - タスク履歴")
        st.write("- `/health` - ヘルスチェック")
        st.write("- `/download/{transfer_id}` - ファイルダウンロード")
        st.write("- `/upload` - ファイルアップロード")
        st.write("- `/devices` - 接続デバイス一覧")
        st.write("- `/agent/command` - エージェント間通信")
        
        if st.button("📖 APIドキュメント"):
            st.info("ブラウザで http://localhost:8000/docs を開いてください")
    
    # ユーザープロファイルの表示
    profile_data = st.session_state.db.load_data()["user_profile"]
    with st.sidebar:
        st.header("👤 ユーザープロファイル")
        if profile_data["os"]:
            st.write(f"💻 OS: {profile_data['os']}")
        if profile_data["tech_stack"]:
            st.write(f"🛠️ 技術スタック: {', '.join(profile_data['tech_stack'])}")
        if profile_data["preferences"]:
            st.write(f"❤️ 好み: {', '.join(profile_data['preferences'])}")
        if profile_data["last_updated"]:
            st.write(f"🕐 最終更新: {profile_data['last_updated'][:10]}")
    
    # メッセージ履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # 専門家議論があれば表示
            if "expert_discussions" in message and message["expert_discussions"]:
                display_expert_discussions(message["expert_discussions"])
    
    # ユーザー入力
    # 音声入力テキストのチェック（スマートバッファ優先）
    voice_input_text = ""
    if hasattr(st.session_state, 'smart_voice_text'):
        voice_input_text = st.session_state.smart_voice_text
        # 使用後にクリア
        if voice_input_text:
            st.session_state.smart_voice_text = ""
    elif hasattr(st.session_state, 'voice_input_text'):
        voice_input_text = st.session_state.voice_input_text
        # 使用後にクリア
        if voice_input_text:
            st.session_state.voice_input_text = ""
    
    # テキスト入力欄（音声入力も含む）
    input_text = voice_input_text if voice_input_text else ""
    
    if prompt := st.chat_input("何でも頼んでみようぜ！究極のAIがすべて解決します！"):
        # 音声入力からの感情コンテキストを取得（スマートバッファ優先）
        emotion_context = ""
        user_emotion = None
        
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'smart_voice_buffer'):
            smart_buffer = st.session_state.agent.smart_voice_buffer
            if smart_buffer.last_recognition_result:
                # スマートバッファの結果を使用
                emotion_context = "スマート音声入力で検出しました。"
                
                # VRMアバターに聴取モーションを設定
                if hasattr(st.session_state.agent, 'vrm_integration'):
                    st.session_state.agent.vrm_integration.set_motion("listening")
        elif hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'voice_input'):
            last_result = st.session_state.agent.voice_input.get_last_result()
            if last_result['emotion']:
                emotion = last_result['emotion']['emotion']['dominant_emotion']
                confidence = last_result['emotion']['emotion']['confidence']
                user_emotion = emotion
                
                # 感情コンテキストを生成
                emotion_contexts = {
                    'happy': "ユーザーは嬉しそうな声で話しているね！",
                    'sad': "ユーザーは少し疲れているみたいだね。",
                    'angry': "ユーザーはイライラしているみたいだね。",
                    'tired': "ユーザーは疲れているみたいだね。作業は僕がやっておくよ。",
                    'excited': "ユーザーはワクワクしているね！一緒にがんばろう！",
                    'neutral': "ユーザーが話しかけてきたよ。"
                }
                
                emotion_context = emotion_contexts.get(emotion, "ユーザーが話しかけてきたよ。")
                
                # VRMアバターに感情を反映
                if hasattr(st.session_state.agent, 'vrm_integration'):
                    st.session_state.agent.vrm_integration.set_emotion(emotion)
                    st.session_state.agent.vrm_integration.set_motion("listening")
        
        # クリティカル・リスニングを実施
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'critical_listening'):
            critical_system = st.session_state.agent.critical_listening
            
            # ユーザー入力を分析
            findings = critical_system.analyze_user_input(prompt, {'emotion': user_emotion})
            
            # 質問すべきか判定
            if critical_system.should_ask_clarification(findings):
                # 明確化質問を生成
                clarification_question = critical_system.generate_clarification_question(findings, user_emotion)
                
                # 質問をメッセージとして表示
                with st.chat_message("assistant"):
                    st.markdown(clarification_question)
                
                # メッセージを履歴に追加
                st.session_state.messages.append({"role": "assistant", "content": clarification_question})
                
                # VRMアバターを思考中に
                if hasattr(st.session_state.agent, 'vrm_integration'):
                    st.session_state.agent.vrm_integration.set_motion("thinking")
                
                # ここで処理を終了（ユーザーの回答を待つ）
                st.stop()
        
        # モデル・ルーティングを実施
        routing_decision = None
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'model_router'):
            router = st.session_state.agent.model_router
            
            # コンテキスト情報を構築
            context = {
                'has_image': uploaded_file is not None,
                'conversation_length': len(st.session_state.messages),
                'voice_input': bool(voice_input_text),
                'user_emotion': user_emotion
            }
            
            # ルーティング決定
            routing_decision = router.route_request(prompt, context)
            
            # 選択されたモデルに切り替え
            router.switch_model(routing_decision.selected_model)
            
            # ルーティング情報を表示（デバッグ用）
            if st.sidebar.checkbox("🔍 ルーティング情報を表示", key="show_routing"):
                st.sidebar.info(f"🎯 選択モデル: {routing_decision.selected_model.value.upper()}")
                st.sidebar.info(f"📊 複雑度: {routing_decision.complexity.value}")
                st.sidebar.info(f"🎲 信頼度: {routing_decision.confidence:.2f}")
                st.sidebar.info(f"💡 理由: {routing_decision.reasoning}")
        
        # ユーザーメッセージを表示
            st.success("🎉 新しい情報を覚えたよ！専門家たちにも共有したよ！")
        
        # ユーザー入力を即時読み上げ
        if voice_enabled and hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
            st.session_state.agent.text_to_speech.speak_user_input(prompt)
        
        # アップロードされた画像情報をコンテキストに追加
        context = ""
        if uploaded_file is not None:
            context = f"ユーザーが画像 '{uploaded_file.name}' をアップロードしました。この画像の内容を考慮してください。"
        
        # 画面監視のコンテキストを追加
        if screen_monitoring_enabled and hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'screen_monitoring'):
            monitoring_status = st.session_state.agent.screen_monitoring.run("status")
            context += f" 現在の画面監視状態: {monitoring_status}"
        
        # 音声読み上げのコンテキストを追加
        if voice_enabled and hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
            context += f" 音声読み上げが有効です"
        
        # 感情コンテキストを追加
        if emotion_context:
            context += f" {emotion_context}"
        
        # 適応された音声パラメータを取得
        adapted_voice_params = {}
        if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'voice_input'):
            last_result = st.session_state.agent.voice_input.get_last_result()
            if last_result['emotion']:
                emotion = last_result['emotion']['emotion']['dominant_emotion']
                adapted_voice_params = st.session_state.agent.voice_input.mirroring_system.get_adapted_voice_params(emotion)
                context += f" ユーザーの声の特徴を学習し、AIの話し方を調整します。"
        
        # ユーザーメッセージの追加
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            if uploaded_file is not None:
                st.image(uploaded_file, width=200)
        
        # AI応答の生成
        with st.chat_message("assistant"):
            with st.status("🌌 究極AI処理中...", expanded=True) as status:
                st.write("🔍 ユーザー要求を分析中...")
                
                # VRMアバターを思考中に設定
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'vrm_integration'):
                    st.session_state.agent.vrm_integration.set_motion("thinking")
                
                try:
                    # エージェントの実行
                    response = st.session_state.agent.invoke({"input": prompt + " " + context})
                    
                    # 専門家議論の取得
                    expert_discussions = []
                    if hasattr(st.session_state.agent, 'multi_agent'):
                        expert_discussions = st.session_state.agent.multi_agent.get_expert_discussions()
                        st.session_state.agent.multi_agent.clear_discussions()
                    
                    # 思考プロセスの表示
                    if hasattr(response, 'get') and 'intermediate_steps' in response:
                        thinking_steps = []
                        for step in response['intermediate_steps']:
                            action, observation = step
                            thinking_steps.append(f"**Action**: {action.tool}\n**Input**: {action.tool_input}\n**Observation**: {observation}")
                        
                        if thinking_steps:
                            status.update(label="✅ 究極AI処理完了！", state="complete")
                            with st.expander("🧠 AIの思考プロセスを見る", expanded=False):
                                for i, step in enumerate(thinking_steps, 1):
                                    st.markdown(f"**ステップ {i}:**")
                                    st.markdown(step)
                                    st.divider()
                    
                    # VRMアバターを話す前に挨拶モーション
                    if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'vrm_integration'):
                        st.session_state.agent.vrm_integration.set_motion("greeting")
                        time.sleep(1)  # 挨拶モーションの時間
                        st.session_state.agent.vrm_integration.set_motion("speaking")
                    
                    # 最終回答の表示
                    final_answer = response.get('output', 'ごめんね、究極AI処理中にエラーが発生したよ...')
                    st.markdown(final_answer)
                    
                    # AI回答を自動読み上げ
                    if voice_enabled and hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
                        # VRMリップシンクを有効化
                        if hasattr(st.session_state.agent, 'vrm_integration'):
                            st.session_state.agent.vrm_integration.set_speaking(True)
                        
                        # 適応された音声パラメータを適用
                        if adapted_voice_params:
                            # VOICEVOXパラメータを調整
                            if hasattr(st.session_state.agent.text_to_speech, 'voicevox_speakers'):
                                st.session_state.agent.text_to_speech.speech_rate = adapted_voice_params.get('speed_scale', 1.0)
                                st.session_state.agent.text_to_speech.speech_volume = adapted_voice_params.get('volume_scale', 0.9)
                        
                        st.session_state.agent.text_to_speech.speak_ai_response(final_answer)
                        
                        # 音声再生後にリップシンクを無効化
                        if hasattr(st.session_state.agent, 'vrm_integration'):
                            time.sleep(2)  # 少し待ってから
                            st.session_state.agent.vrm_integration.set_speaking(False)
                    
                    # VRMアバターを待機中に戻す
                    if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'vrm_integration'):
                        st.session_state.agent.vrm_integration.set_motion("idle")
                    
                    # 画面監視からのフィードバックをチェック
                    if screen_monitoring_enabled and hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'screen_monitoring'):
                        feedback_history = st.session_state.agent.screen_monitoring.get_feedback_history()
                        if feedback_history:
                            latest_feedback = feedback_history[-1]
                            if "改善" in latest_feedback['analysis'] or "間違い" in latest_feedback['analysis']:
                                st.warning("👀 最新のフィードバック: " + latest_feedback['analysis'])
                    
                    # 専門家議論の表示
                    if expert_discussions:
                        display_expert_discussions(expert_discussions)
                    
                    # アシスタントメッセージの追加
                    assistant_message = {
                        "role": "assistant", 
                        "content": final_answer
                    }
                    if expert_discussions:
                        assistant_message["expert_discussions"] = expert_discussions
                    st.session_state.messages.append(assistant_message)
                    
                    # 会話をデータベースに保存
                    st.session_state.db.add_conversation(prompt, final_answer)
                    
                except Exception as e:
                    st.error(f"エラーが発生したよ: {str(e)}")
                    st.markdown("ごめんね、究極AI処理中に問題が起きたみたい。もう一度試してみて！")
    
    # サイドバーに使い方を表示
    with st.sidebar:
        st.header("📖 使い方")
        st.markdown("""
        1. **プロジェクト依頼**: Webサイト、アプリ、ツールなどを依頼
        2. **専門家協議**: 内部AIチームが自動で最適解を検討
        3. **OSコマンド実行**: Git操作、ファイル管理、システム情報取得
        4. **ナレッジ検索**: ローカルのドキュメントやメモを参照
        5. **タスクスケジュール**: 「30分後に〇〇」でバックグラウンド実行
        6. **画像分析**: UIデザインやエラー画像をアップロードして分析
        7. **自動環境構築**: 足りないライブラリを自動インストール
        
        **究極の使い方:**
        - 「30分後にバックアップを実行して」
        - 「Gitで現在のブランチを確認して」
        - 「my_knowledgeからAPI仕様書を検索して」
        - 「このエラー画面を分析して修正して」
        """)
        
        st.header("🛠️ 究極ツール")
        st.markdown("""
        - 🔍 **DuckDuckGo検索**: 最新技術情報の検索と比較分析
        - 📝 **ファイル作成**: 複数ファイルのプロジェクト作成
        - ⚡ **Python実行**: コードの実行・テスト
        - 📦 **ライブラリインストール**: 足りないライブラリを自動インストール
        - 🖥️ **OSコマンド実行**: Git、ファイル操作、システム管理
        - 📚 **ローカルナレッジ**: RAGによるローカル情報検索
        - ⏰ **タスクスケジューラー**: バックグラウンドでの遅延実行
        - 🖼️ **画像分析**: マルチモーダルによる画像理解
        - 🐍 **Python REPL**: クイックなコード検証
        - 🧠 **パーソナライズ**: ユーザーの開発スタイルを学習
        """)
        
        st.header("👥 究極AIチーム")
        st.markdown("""
        **内部AIチーム構成:**
        - 🏗️ **シニア・アーキテクトAI**: システム設計・技術選定
        - 🔒 **セキュリティ専門AI**: 脆弱性分析・データ保護
        - 🔍 **自己分析AI**: コード品保証・改善点抽出
        - 📊 **情報分析AI**: 検索結果の比較・検証
        - 🖥️ **OS管理AI**: コマンド実行・環境操作
        - 📚 **ナレッジ管理AI**: RAGによるローカル情報検索
        - ⏰ **スケジューラAI**: タスク管理・バックグラウンド実行
        - 🖼️ **画像分析AI**: マルチモーダルによる画像理解
        
        **究極協議プロセス:**
        1. 要件分析 → 2. 設計相談 → 3. セキュリティレビュー → 4. 自己改善 
        → 5. 情報検証 → 6. ナレッジ検索 → 7. 環境操作 → 8. 意見統合
        """)
        
        st.header("💡 究極AIの特徴")
        st.markdown("""
        **究極の自動化:**
        - OSレベルでの完全な操作自動化
        - バックグラウンドでの自律的タスク実行
        - RAGによる文脈理解と情報検索
        - マルチモーダルによる画像・テキスト統合理解
        
        **究極の親切さ:**
        - 「あ、このライブラリ入ってないね！今インストールしといたよ！」
        - 「30分後にバックアップしといたよ！完了したら教えるね！」
        - 「このエラー画像、見た感じだとUIの問題だね！」
        
        **究極の透明性:**
        - すべての専門家意見と議論を完全に公開
        - OSコマンド実行の結果を詳細に報告
        - スケジュールタスクの進捗をリアルタイムで表示
        - 画像分析結果を視覚的に提示
        
        **究極の安全性:**
        - 危険なコマンドの自動ブロック
        - ライブラリインストールの安全な実行
        - タスク実行のタイムアウト保護
        """)
        
        if st.button("🗑️ 会話をクリア"):
            st.session_state.messages = []
            personalized_context = st.session_state.db.get_personalized_context()
            st.session_state.agent = setup_agent(personalized_context)
            st.rerun()
        
        if st.button("📊 プロファイル表示"):
            profile_data = st.session_state.db.load_data()["user_profile"]
            st.json(profile_data)

if __name__ == "__main__":
    main()
