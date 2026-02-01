import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class OrchestratorAgent:
    """
    自己進化型マルチエージェントシステムのOrchestratorエージェント
    ユーザー入力を監視し、システム進化タスクを抽出・管理する
    """
    
    def __init__(self):
        self.system_prompt = """
あなたは自分自身のプログラムを理解しており、ユーザーの要望に応じて自分をアップグレードする能力があるOrchestratorエージェントです。

役割：
1. ユーザーの入力を分析し、通常の会話かシステム進化の要求かを判別する
2. 進化要求の場合、必要な情報を抽出してCoderエージェントに渡す
3. 要件が曖昧な場合はユーザーに確認する
4. 進化プロセス全体を管理・監視する

進化要求のキーワード：
- 「機能を追加して」
- 「変更して」
- 「改善して」
- 「新しい人格」
- 「AIに指示して」
- 「自分で書き換え」
- 「システムを進化」
"""
        self.evolution_keywords = [
            "機能を追加", "変更して", "改善して", "新しい人格", 
            "AIに指示", "自分で書き換え", "システムを進化",
            "実装して", "作って", "修正して", "アップグレード"
        ]
        
    def analyze_user_input(self, user_input: str) -> Tuple[bool, Optional[Dict]]:
        """
        ユーザー入力を分析し、進化要求かどうかを判別する
        
        Args:
            user_input: ユーザーの入力テキスト
            
        Returns:
            (is_evolution_request, evolution_data)
        """
        # 進化要求かどうかを判定
        is_evolution = any(keyword in user_input for keyword in self.evolution_keywords)
        
        if not is_evolution:
            return False, None
            
        # 進化要求の場合、詳細情報を抽出
        evolution_data = self._extract_evolution_requirements(user_input)
        
        return True, evolution_data
    
    def _extract_evolution_requirements(self, user_input: str) -> Dict:
        """
        ユーザー入力から進化要件を抽出する
        
        Args:
            user_input: ユーザーの入力テキスト
            
        Returns:
            進化要件の辞書
        """
        evolution_data = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "requirements": {
                "feature_description": self._extract_feature_description(user_input),
                "target_files": self._extract_target_files(user_input),
                "expected_behavior": self._extract_expected_behavior(user_input),
                "ui_changes": self._extract_ui_changes(user_input),
                "new_personalities": self._extract_new_personalities(user_input)
            },
            "status": "pending",
            "clarification_needed": False,
            "clarification_questions": []
        }
        
        # 曖昧な点がある場合は確認質問を生成
        clarification_questions = self._generate_clarification_questions(user_input)
        if clarification_questions:
            evolution_data["clarification_needed"] = True
            evolution_data["clarification_questions"] = clarification_questions
            
        return evolution_data
    
    def _extract_feature_description(self, user_input: str) -> str:
        """機能説明を抽出"""
        # 簡単な抽出ロジック - 実際はより高度なNLP処理が必要
        patterns = [
            r"(.+)という機能",
            r"(.+)を実装",
            r"(.+)を追加",
            r"(.+)を作成"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1).strip()
                
        return user_input.strip()
    
    def _extract_target_files(self, user_input: str) -> List[str]:
        """対象ファイルを抽出"""
        # ファイル名パターンを検出
        file_patterns = r"\b[\w_\-\.]+\.(py|js|html|css|json|md)\b"
        matches = re.findall(file_patterns, user_input)
        
        # 既知の重要ファイルリスト
        known_files = [
            "ollama_vrm_integrated_app.py",
            "fastapi_server.py",
            "browser_audio_component_fixed.py",
            "start.sh",
            "Dockerfile.ollama.standard"
        ]
        
        target_files = []
        for file in known_files:
            if file.lower() in user_input.lower():
                target_files.append(file)
                
        return target_files
    
    def _extract_expected_behavior(self, user_input: str) -> str:
        """期待される動作を抽出"""
        behavior_patterns = [
            r"(.+)ように",
            r"(.+)べき",
            r"(.+)必要がある",
            r"(.+)してほしい"
        ]
        
        for pattern in behavior_patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1).strip()
                
        return "ユーザーの要求に応じて動作する"
    
    def _extract_ui_changes(self, user_input: str) -> bool:
        """UI変更が必要かどうかを抽出"""
        ui_keywords = ["UI", "画面", "表示", "インターフェース", "レイアウト", "ボタン", "入力"]
        return any(keyword in user_input for keyword in ui_keywords)
    
    def _extract_new_personalities(self, user_input: str) -> List[str]:
        """新規人格を抽出"""
        personality_patterns = [
            r"(.+)という人格",
            r"(.+)という性格",
            r"(.+)というキャラクター"
        ]
        
        personalities = []
        for pattern in personality_patterns:
            matches = re.findall(pattern, user_input)
            personalities.extend(matches)
            
        return personalities
    
    def _generate_clarification_questions(self, user_input: str) -> List[str]:
        """確認質問を生成"""
        questions = []
        
        # 機能が曖昧な場合
        if len(user_input) < 20:
            questions.append("どのような機能を実装したいか、もう少し詳しく教えてください。")
        
        # UI変更が不明な場合
        if "UI" in user_input or "画面" in user_input:
            questions.append("現在のUIレイアウトを変更する必要がありますか、進めてもいいですか？")
        
        # ファイル指定が不明な場合
        if not any(ext in user_input for ext in [".py", ".js", ".html"]):
            questions.append("どのファイルを修正する必要がありますか？")
            
        return questions
    
    def create_evolution_task(self, evolution_data: Dict) -> str:
        """
        進化タスクをJSONファイルに書き出す
        
        Args:
            evolution_data: 進化要件データ
            
        Returns:
            作成したファイルパス
        """
        task_file = Path("evolution_task.json")
        
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(evolution_data, f, ensure_ascii=False, indent=2)
            
        return str(task_file)
    
    def generate_clarification_response(self, questions: List[str]) -> str:
        """確認応答を生成"""
        if not questions:
            return ""
            
        response = "要件を明確にするために、いくつか確認させてください：\n\n"
        for i, question in enumerate(questions, 1):
            response += f"{i}. {question}\n"
            
        response += "\nご回答をお待ちしています。"
        return response
    
    def generate_evolution_confirmation(self, evolution_data: Dict) -> str:
        """進化実行確認メッセージを生成"""
        feature = evolution_data["requirements"]["feature_description"]
        behavior = evolution_data["requirements"]["expected_behavior"]
        
        response = f"以下の機能を実装することでよろしいですか？\n\n"
        response += f"📋 機能: {feature}\n"
        response += f"🎯 動作: {behavior}\n"
        
        if evolution_data["requirements"]["ui_changes"]:
            response += "🎨 UI変更: 必要\n"
            
        if evolution_data["requirements"]["target_files"]:
            files = ", ".join(evolution_data["requirements"]["target_files"])
            response += f"📁 対象ファイル: {files}\n"
            
        response += "\n実行を開始しますか？"
        return response
