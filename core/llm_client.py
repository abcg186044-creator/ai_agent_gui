"""
LLMクライアントモジュール
Ollamaとの通信、プロンプト構築、自己進化ロジックを管理
"""

import re
import json
import os
from datetime import datetime
from .constants import *
from .self_mutation import ModularSelfMutationManager
from .file_map import resolve_target_file, get_relevant_files

class OllamaClient:
    def __init__(self, model_name="llama2", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.conversation_history = []
    
    def generate_response(self, prompt, context=None):
        """Ollamaで応答生成"""
        try:
            import requests
            
            # コンテキストを構築
            full_prompt = self._build_prompt(prompt, context)
            
            # Ollama API呼び出し
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                return f"APIエラー: {response.status_code}"
                
        except Exception as e:
            return f"LLM接続エラー: {str(e)}"
    
    def _build_prompt(self, user_input, context=None):
        """プロンプトを構築"""
        # 基本プロンプト
        base_prompt = f"""
あなたは親切で優秀なAIアシスタントです。ユーザーの質問に丁寧にお答えください。

ユーザー入力: {user_input}
"""
        
        # コンテキストがあれば追加
        if context:
            base_prompt += f"\nコンテキスト: {context}"
        
        return base_prompt

class SelfEvolvingAgent:
    def __init__(self):
        self.evolution_rules = []
        self.consciousness_level = 0.5
        self.mutation_manager = ModularSelfMutationManager()
        self.load_evolution_rules()
    
    def apply_self_mutation(self, user_request: str) -> Dict:
        """特定ファイルを狙い撃ちする局所的自己改造を実行"""
        try:
            from services.state_manager import resolve_target_file
            from services.app_generator import partial_mutation_manager
            from services.backup_manager import backup_manager
            from services.import_sync import import_synchronizer, module_validator
            
            # ターゲットファイルを特定
            target_file = resolve_target_file(user_request)
            
            if not target_file:
                return {
                    "success": False,
                    "error": "修正対象ファイルを特定できませんでした",
                    "suggestion": "より具体的な指示（例：「デザインを変えて」「UIのスタイルを修正」）を試してください"
                }
            
            # ターゲットファイルのみを読み込み
            print(f"🎯 ターゲットファイル: {target_file}")
            
            # 安全な部分バックアップを作成
            backup_path = backup_manager.create_backup(target_file)
            
            if not backup_path:
                return {
                    "success": False,
                    "error": "バックアップ作成に失敗しました"
                }
            
            # 修正が必要なコードブロックを抽出
            target_function = self._estimate_target_function(user_request, target_file)
            
            # 最適化されたプロンプトを生成（ターゲットファイルのみ）
            focused_prompt = partial_mutation_manager.generate_focused_prompt(
                target_file, user_request, target_function
            )
            
            # LLMに修正コードを生成させる
            if not st.session_state.get(SESSION_KEYS['ollama']):
                st.session_state[SESSION_KEYS['ollama']] = OllamaClient()
            
            ollama_client = st.session_state[SESSION_KEYS['ollama']]
            modified_code = ollama_client.generate_response(focused_prompt)
            
            # 特定ファイルのみを上書き保存
            mutation_result = partial_mutation_manager.apply_partial_mutation(
                target_file, modified_code, target_function
            )
            
            if mutation_result["success"]:
                # インポート同期を実行
                sync_result = import_synchronizer.sync_imports_after_mutation(target_file)
                
                # モジュールバリデーションを実行
                validation_result = module_validator.validate_all_modules()
                
                return {
                    "success": True,
                    "target_file": target_file,
                    "backup_path": backup_path,
                    "target_function": target_function,
                    "sync_result": sync_result,
                    "validation_result": validation_result,
                    "message": f"{target_file} のみを正常に修正しました"
                }
            else:
                return {
                    "success": False,
                    "error": mutation_result["error"],
                    "target_file": target_file,
                    "backup_path": backup_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"局所的自己改造エラー: {str(e)}"
            }
    
    def execute_self_mutation(self, user_request: str) -> Dict:
        """自己改造を実行（ファイルマップ対応版）"""
        try:
            # ファイルマップから対象モジュールを特定
            target_module = resolve_target_file(user_request)
            
            if not target_module:
                # 従来のキーワードマッチングも試行
                target_module = self.mutation_manager.detect_target_module(user_request)
            
            if not target_module:
                return {
                    "success": False,
                    "error": "改造対象を特定できませんでした",
                    "suggestion": "より具体的な指示（例：「デザインを変えて」「AIの性格を変えて」）を試してください"
                }
            
            # 局所的な自己書き換えを実行
            return self._execute_partial_mutation(target_module, user_request)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"自己改造エラー: {str(e)}"
            }
    
    def _execute_partial_mutation(self, file_path: str, user_request: str) -> Dict:
        """局所的な自己書き換えを実行"""
        try:
            from services.app_generator import partial_mutation_manager
            from services.import_sync import import_synchronizer, module_validator
            
            # ターゲット関数を推定
            target_function = self._estimate_target_function(user_request, file_path)
            
            # 最適化されたプロンプトを生成
            focused_prompt = partial_mutation_manager.generate_focused_prompt(
                file_path, user_request, target_function
            )
            
            # LLMで修正コードを生成
            if not st.session_state.get(SESSION_KEYS['ollama']):
                st.session_state[SESSION_KEYS['ollama']] = OllamaClient()
            
            ollama_client = st.session_state[SESSION_KEYS['ollama']]
            modified_code = ollama_client.generate_response(focused_prompt)
            
            # 局所的な書き換えを適用
            mutation_result = partial_mutation_manager.apply_partial_mutation(
                file_path, modified_code, target_function
            )
            
            if mutation_result["success"]:
                # インポート同期を実行
                sync_result = import_synchronizer.sync_imports_after_mutation(file_path)
                
                # モジュールバリデーションを実行
                validation_result = module_validator.validate_all_modules()
                
                return {
                    "success": True,
                    "target_module": file_path,
                    "mutation_type": "partial",
                    "target_function": target_function,
                    "backup_path": mutation_result["backup_path"],
                    "sync_result": sync_result,
                    "validation_result": validation_result,
                    "message": f"{file_path} の一部を正常に改造しました"
                }
            else:
                return {
                    "success": False,
                    "error": mutation_result["error"],
                    "backup_path": mutation_result.get("backup_path")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"局所的書き換えエラー: {str(e)}"
            }
    
    def _estimate_target_function(self, user_request: str, file_path: str) -> Optional[str]:
        """ユーザー要求からターゲット関数を推定"""
        try:
            from services.app_generator import CodeExtractor
            
            # ファイル内の関数を取得
            extractor = CodeExtractor()
            functions = extractor.extract_functions(file_path)
            
            if not functions:
                return None
            
            # キーワードマッチングで関数を推定
            request_lower = user_request.lower()
            
            # 一般的な関数名とのマッチング
            function_keywords = {
                "デザイン": ["get_", "render_", "apply_", "set_"],
                "UI": ["render_", "display_", "show_", "update_"],
                "スタイル": ["get_", "set_", "apply_", "update_"],
                "AI": ["generate_", "process_", "handle_", "respond_"],
                "会話": ["chat_", "conversation_", "message_", "respond_"],
                "VRM": ["vrm_", "avatar_", "render_", "update_"],
                "TODO": ["todo_", "task_", "add_", "complete_"],
                "保存": ["save_", "store_", "write_", "persist_"],
                "読み込み": ["load_", "read_", "get_", "fetch_"]
            }
            
            for keyword, prefixes in function_keywords.items():
                if keyword in request_lower:
                    for func_name in functions.keys():
                        for prefix in prefixes:
                            if func_name.startswith(prefix):
                                return func_name
            
            # 最初の関数をデフォルトとして返す
            return list(functions.keys())[0] if functions else None
            
        except Exception as e:
            print(f"関数推定エラー: {e}")
            return None
    
    def _generate_mutation_code(self, user_request: str, target_module: str) -> Optional[str]:
        """改造コードを生成"""
        if "デザイン" in user_request and "styles.py" in target_module:
            return '''
# 新しいデザインテーマ
NEW_THEME = {"ocean": {"primary": "#0077be", "secondary": "#00a8cc"}}
'''
        elif "性格" in user_request and "llm_client.py" in target_module:
            return '''
# 新しい人格タイプ
NEW_PERSONALITY = {"philosopher": {"name": "哲学者", "prompt": "深遠な哲学者です"}}
'''
        return None
    
    def _apply_mutation(self, target_module: str, updated_code: str) -> bool:
        """改造を適用"""
        try:
            with open(target_module, 'a', encoding='utf-8') as f:
                f.write('\n\n' + updated_code)
            return True
        except Exception as e:
            print(f"ファイル書き換えエラー: {e}")
            return False

class ConversationalEvolutionAgent:
    def __init__(self):
        self.consciousness_level = 0.3
        self.learning_rate = 0.001
    
    def check_and_evolve_automatically(self, conversation_history):
        """対話からの自律進化をチェック"""
        if len(conversation_history) < 3:
            return None
        
        # 最新3件の対話を分析
        recent_convs = conversation_history[-3:]
        
        # 複雑さの指標を計算
        complexity_score = self._calculate_complexity(recent_convs)
        
        if complexity_score > 0.7:
            return self._evolve("complexity", complexity_score)
        
        return None
    
    def _calculate_complexity(self, conversations):
        """対話の複雑さを計算"""
        total_length = 0
        question_count = 0
        
        for conv in conversations:
            user_text = conv.get("user", "")
            total_length += len(user_text)
            if "？" in user_text or "ですか" in user_text:
                question_count += 1
        
        # 複雑さスコア（簡易計算）
        complexity = (total_length / 1000) + (question_count * 0.1)
        return min(complexity, 1.0)
    
    def _evolve(self, evolution_type, score):
        """進化を実行"""
        self.consciousness_level += self.learning_rate * score
        return {
            "success": True,
            "evolution_type": evolution_type,
            "consciousness_boost": self.learning_rate * score,
            "new_consciousness_level": self.consciousness_level
        }

def extract_todos_from_text(text, source="auto"):
    """テキストからTODOを抽出する関数"""
    todos = []
    
    # TODO抽出パターン
    todo_patterns = [
        r'(明日|今日|今週|来週).*?(する|やる|作る|実装する|確認する|準備する)',
        r'(.*?)(する必要がある|やらないと|しないといけない)',
        r'(.*?)(の予定|の計画|の目標)',
        r'(.*?)(を忘れないで|を覚えておいて|をメモしておいて)',
        r'(タスク|TODO|課題).*?(.*?)(です|だ)'
    ]
    
    for pattern in todo_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                todo_text = ' '.join(match)
            else:
                todo_text = match
            
            if len(todo_text.strip()) > 5:  # 短すぎるものは除外
                todos.append({
                    'task': f"[{source}] {todo_text.strip()}",
                    'completed': False,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    
    return todos

def detect_app_launch_command(text, available_apps):
    """会話からアプリ起動コマンドを検出"""
    launch_patterns = [
        r'(電卓|計算機|calculator).*?(出して|起動|開いて|表示)',
        r'(.*?)(出して|起動|開いて|表示)',
        r'(.*?)(を使いたい|を使って|を起動して)',
    ]
    
    for pattern in launch_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                keyword, action = match
            else:
                keyword = match
                action = "起動"
            
            keyword = keyword.lower().strip()
            
            # アプリ名と一致するかチェック
            for app in available_apps:
                app_name = app['name'].lower()
                if keyword in app_name or app_name in keyword:
                    return app, f"{keyword}を{action}します"
            
            # 特定のキーワードでアプリを推定
            if '電卓' in keyword or '計算機' in keyword or 'calculator' in keyword:
                for app in available_apps:
                    if 'calc' in app['name'].lower() or '電卓' in app['name']:
                        return app, "電卓を起動します"
    
    return None, None
