"""
LLMクライアントモジュール
Ollamaとの通信、プロンプト構築、自己進化ロジックを管理
"""

import re
import json
import os
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from core.constants import *
from core.self_mutation import ModularSelfMutationManager
from core.file_map import resolve_target_file, get_relevant_files

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
[ABSOLUTE - 絶対遵守: インポート死守命令]
【最重要】コードを修正・生成する際は、関数の断片だけを返してはならない。
必ず、そのファイルに必要なすべてのインポート文（例：import streamlit as st）を含んだ『完全なファイル内容』を最初から最後まで出力せよ。
インポート文を欠いたコードは、システムを破壊する致命的なエラーとみなす。

[ABSOLUTE - クリーンなインポート維持]
1. コードを書き換える際は、必ず「重複のない、整理されたインポート文」を冒頭に配置した【完全なコード】を生成してください。
2. 重複したインポート（import streamlit as st が2回出るなど）が発生しないよう、生成後に自分自身で出力を一度チェック（セルフ検閲）させてください。

[ABSOLUTE - 破壊テストの禁止]
自分自身のインポートガードロジックを修正しようとすることは、システムの自殺行為であり、厳禁である。
core/guardian.py と関連するガード機能は絶対に変更・削除・無効化してはならない。

[ABSOLUTE - 動的インポートの完全置換]
AIが今後「自分自身をリファクタリング（移動）」した際、ファイル内のすべてのインポート文だけでなく、**関数内や条件分岐（if文）の中にある動的インポートも漏れなく置換する**こと。
現在のディレクトリ構造と矛盾するインポートパスはすべて修正すること。
特に state_manager は services/ 内にあることを確実に反映すること。

[ABSOLUTE - 住所確認の徹底]
AIがファイルを移動したりインポートを書いたりする際、必ず以下のチェックを行うこと：
1. os.path.exists() を使って、インポートしようとしているファイルが「本当にそのパスに存在するか」をコード生成前に内部で確認すること。
2. もし存在しない場合は、全ディレクトリを検索して正しいパスを見つけ出すロジックを適用すること。
3. 生成したコードのすべてのインポートパスを実在確認すること。

出力形式:
```python
import streamlit as st
(その他のインポート)
(修正後の全コード)
```

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
            from .self_optimizer import evolution_logger
            
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
            
            # インポート自動チェックと補完
            enhanced_code = self._auto_complete_imports(target_file, modified_code)
            
            # 最優先システム命令：typingインポートのバリデーションと自動補完
            validated_code = self._validate_and_complete_typing_imports(target_file, enhanced_code)
            
            # 特定ファイルのみを上書き保存
            mutation_result = partial_mutation_manager.apply_partial_mutation(
                target_file, validated_code, target_function
            )
            
            if mutation_result["success"]:
                # 命名プロトコルのチェック
                name_change_result = self._check_and_apply_naming_protocol(user_request, enhanced_code)
                
                # インポート同期を実行
                sync_result = import_synchronizer.sync_imports_after_mutation(target_file)
                
                # モジュールバリデーションを実行
                validation_result = module_validator.validate_all_modules()
                
                result = {
                    "success": True,
                    "target_file": target_file,
                    "backup_path": backup_path,
                    "target_function": target_function,
                    "sync_result": sync_result,
                    "validation_result": validation_result,
                    "auto_imports_added": self._get_added_imports(modified_code, enhanced_code),
                    "message": f"{target_file} のみを正常に修正しました"
                }
                
                # 名前変更があった場合は結果に追加
                if name_change_result["name_changed"]:
                    result.update(name_change_result)
                    # セッション状態を更新して再起動
                    st.session_state['agent_name'] = name_change_result['new_name']
                    result["message"] += f"\\n🎯 エージェント名を「{name_change_result['new_name']}」に変更しました"
                
                return result
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
    
    def _check_and_apply_naming_protocol(self, user_request: str, modified_code: str) -> Dict:
        """命名プロトコルをチェックして適用"""
        try:
            # 名前変更の要求を検出
            name_change_keywords = ["名前を", "改名", "名称変更", "アイデンティティ", "呼び方"]
            
            if any(keyword in user_request for keyword in name_change_keywords):
                # 新しい名前を抽出
                new_name = self._extract_new_name(user_request)
                
                if new_name and new_name != AGENT_NAME:
                    # core/constants.pyのAGENT_NAMEを書き換え
                    constants_file = "core/constants.py"
                    
                    with open(constants_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # AGENT_NAMEの値を置換
                    updated_content = re.sub(
                        r'AGENT_NAME = ["\'][^"\']+["\']',
                        f'AGENT_NAME = "{new_name}"',
                        content
                    )
                    
                    with open(constants_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"🎯 エージェント名を「{new_name}」に変更しました")
                    
                    return {
                        "name_changed": True,
                        "new_name": new_name,
                        "old_name": AGENT_NAME,
                        "constants_file": constants_file
                    }
            
            return {"name_changed": False}
            
        except Exception as e:
            print(f"命名プロトコルエラー: {e}")
            return {"name_changed": False}
    
    def _extract_new_name(self, user_request: str) -> Optional[str]:
        """ユーザー要求から新しい名前を抽出"""
        try:
            # 名前を抽出するパターン
            patterns = [
                r'名前を「([^」]+)」に',
                r'改名して「([^」]+)」',
                r'名称を「([^」]+)」に',
                r'「([^」]+)」と呼んで',
                r'アイデンティティは「([^」]+)」',
                r'「([^」]+)」という名前'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_request)
                if match:
                    new_name = match.group(1).strip()
                    # 名前のバリデーション
                    if len(new_name) > 0 and len(new_name) <= 20:
                        return new_name
            
            return None
            
        except Exception as e:
            print(f"名前抽出エラー: {e}")
            return None
    
    def _validate_and_complete_typing_imports(self, file_path: str, code: str) -> str:
        """最優先システム命令：typingインポートのバリデーションと自動補完"""
        try:
            # 現在のインポートを抽出
            existing_imports = self._extract_imports_from_file(file_path)
            
            # 必要なtypingインポートを検出
            required_typing_imports = self._detect_required_typing_imports(code)
            
            # 不足しているtypingインポートを特定
            missing_typing_imports = required_typing_imports - existing_imports
            
            if missing_typing_imports:
                # typingインポート文を生成
                typing_import_statement = self._generate_typing_import_statement(missing_typing_imports)
                
                # コードの先頭にtypingインポートを追加
                lines = code.split('\n')
                
                # 最初の既存のimport文の前に追加
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ')):
                        insert_index = i + 1
                    elif line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                        break
                
                lines.insert(insert_index, typing_import_statement)
                lines.insert(insert_index + 1, '')
                
                validated_code = '\n'.join(lines)
                
                print(f"🔧 typingインポートを自動補完: {missing_typing_imports}")
                return validated_code
            
            return code
            
        except Exception as e:
            print(f"⚠️ typingインポート検証エラー: {e}")
            return code
    
    def _detect_required_typing_imports(self, code: str) -> set:
        """コードから必要なtypingインポートを検出"""
        typing_imports = set()
        
        # 基本的な型ヒント
        basic_types = ['Dict', 'List', 'Optional', 'Any', 'Tuple', 'Union']
        for type_name in basic_types:
            if type_name in code:
                typing_imports.add(type_name)
        
        # 高度な型ヒント
        advanced_types = ['Callable', 'Iterator', 'Generator', 'Type', 'NoReturn', 'Literal', 'Final', 'ClassVar', 'cast', 'overload', 'TypeVar', 'Generic']
        for type_name in advanced_types:
            if type_name in code:
                typing_imports.add(type_name)
        
        return typing_imports
    
    def _generate_typing_import_statement(self, typing_imports: set) -> str:
        """typingインポート文を生成"""
        if not typing_imports:
            return ""
        
        # アルファベット順にソート
        sorted_imports = sorted(list(typing_imports))
        
        return f"from typing import {', '.join(sorted_imports)}"
    
    def _extract_imports_from_file(self, file_path: str) -> set:
        """ファイルから既存のインポートを抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = set()
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('from typing import'):
                    # from typing import Dict, List, Optional
                    imports.update(line.replace('from typing import ', '').split(', '))
                    imports = {imp.strip() for imp in imports}
            
            return imports
            
        except Exception as e:
            print(f"インポート抽出エラー: {e}")
            return set()
    
    def _auto_complete_imports(self, file_path: str, code: str) -> str:
        """インポート自動チェックと補完"""
        try:
            # ファイルが存在しない場合は作成
            if not Path(file_path).exists():
                print(f"📁 ファイルが存在しないため作成: {file_path}")
                self._create_missing_file(file_path, code)
                return code
            
            # 現在のインポートを抽出
            existing_imports = self._extract_imports_from_file(file_path)
            
            # 新しいコードから必要なインポートを検出
            required_imports = self._detect_required_imports(code)
            
            # 不足しているインポートを特定
            missing_imports = required_imports - existing_imports
            
            if missing_imports:
                # インポート文を生成
                import_statements = self._generate_import_statements(missing_imports)
                
                # コードの先頭にインポートを追加
                enhanced_code = import_statements + "\n\n" + code
                
                print(f"🔧 自動インポート追加: {missing_imports}")
                return enhanced_code
            
            return code
            
        except Exception as e:
            print(f"⚠️ インポート自動補完エラー: {e}")
            return code
    
    def _create_missing_file(self, file_path: str, code: str):
        """存在しないファイルを作成"""
        try:
            # ディレクトリを作成
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 基本構造のファイルを作成
            file_extension = Path(file_path).suffix
            
            if file_extension == '.py':
                # Pythonファイルの場合
                basic_structure = f"""
\"\"\"
{Path(file_path).stem} モジュール
自動生成されたファイル
\"\"\"

# 必要なインポート
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json

# 基本クラス
class {Path(file_path).stem.replace('.py', '').capitalize()}:
    def __init__(self):
        self.name = "{Path(file_path).stem}"
        self.created_at = datetime.now()
    
    def get_info(self) -> Dict[str, Any]:
        return {{
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }}

# 生成されたコード
{code}
"""
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(basic_structure)
                
            else:
                # その他のファイルの場合
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
            
            print(f"✅ ファイルを作成しました: {file_path}")
            
        except Exception as e:
            print(f"❌ ファイル作成エラー: {e}")
    
    def _validate_import_path(self, import_statement: str) -> bool:
        """インポートパスの妥当性を検証"""
        try:
            # インポート文を解析
            if import_statement.startswith('from '):
                parts = import_statement.split()
                if len(parts) >= 4 and parts[1] == 'import':
                    module_path = parts[1]
                    # 相対インポートかチェック
                    if module_path.startswith('.'):
                        return True
                    # 絶対インポートかチェック
                    if '.' in module_path:
                        return True
            
            elif import_statement.startswith('import '):
                module_name = import_statement.replace('import ', '').strip()
                # 標準ライブラリかチェック
                standard_libs = ['os', 'sys', 'json', 're', 'datetime', 'pathlib', 'typing']
                if module_name in standard_libs:
                    return True
                # モジュール名にドットが含まれるかチェック
                if '.' in module_name:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _suggest_alternative_import(self, import_statement: str, file_path: str) -> str:
        """代替インポートを提案"""
        try:
            # ファイルパスからモジュール名を推定
            file_parts = Path(file_path).parts
            
            if 'ui' in file_parts:
                if 'constants' in import_statement:
                    return "from ui.constants import UI_COLORS, UI_STYLES"
                elif 'styles' in import_statement:
                    return "from ui.styles import get_line_chat_css"
                    
            elif 'core' in file_parts:
                if 'constants' in import_statement:
                    return "from core.constants import UI_COLORS, UI_STYLES"
                    
            # デフォルトの提案
            return f"# TODO: {import_statement} のインポートを確認してください"
            
        except Exception:
            return f"# TODO: {import_statement} のインポートを確認してください"
    
    def _extract_imports_from_file(self, file_path: str) -> set:
        """ファイルから既存のインポートを抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = set()
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('import '):
                    imports.add(line.replace('import ', '').strip())
                elif line.startswith('from '):
                    imports.add(line.strip())
            
            return imports
            
        except Exception as e:
            print(f"インポート抽出エラー: {e}")
            return set()
    
    def _detect_required_imports(self, code: str) -> set:
        """コードから必要なインポートを検出"""
        imports = set()
        
        # 型ヒントの検出（強化版）
        type_hints = [
            'Dict', 'List', 'Optional', 'Any', 'Tuple', 'Union', 'Callable',
            'Iterator', 'Generator', 'Type', 'NoReturn', 'Literal',
            'Final', 'ClassVar', 'cast', 'overload', 'TypeVar', 'Generic'
        ]
        
        for type_hint in type_hints:
            if type_hint in code:
                imports.add(f'from typing import {type_hint}')
        
        # 一般的なライブラリの検出
        if 'datetime' in code and 'from datetime' not in code:
            imports.add('from datetime import datetime')
        if 'Path' in code and 'from pathlib' not in code:
            imports.add('from pathlib import Path')
        if 'json' in code and 'import json' not in code:
            imports.add('import json')
        if 're' in code and 'import re' not in code:
            imports.add('import re')
        if 'os' in code and 'import os' not in code:
            imports.add('import os')
        if 'sys' in code and 'import sys' not in code:
            imports.add('import sys')
        
        return imports
    
    def _generate_import_statements(self, imports: set) -> str:
        """インポート文を生成"""
        statements = []
        
        # typing関連をまとめる
        typing_imports = []
        other_imports = []
        
        for imp in sorted(imports):
            if imp.startswith('from typing'):
                typing_imports.append(imp)
            else:
                other_imports.append(imp)
        
        # typingを一つにまとめる
        if typing_imports:
            typing_types = []
            for imp in typing_imports:
                if imp.startswith('from typing import '):
                    typing_types.append(imp.replace('from typing import ', ''))
            
            if typing_types:
                statements.append(f"from typing import {', '.join(sorted(typing_types))}")
        
        # その他のインポート
        statements.extend(other_imports)
        
        return '\n'.join(statements)
    
    def _get_added_imports(self, original_code: str, enhanced_code: str) -> List[str]:
        """追加されたインポートを取得"""
        original_imports = self._detect_required_imports(original_code)
        enhanced_imports = self._detect_required_imports(enhanced_code)
        
        added = enhanced_imports - original_imports
        return sorted(list(added))
    
    def self_diagnose(self) -> Dict:
        """自分の全ソースコードを読み込み、自己診断を実行"""
        try:
            from .self_optimizer import code_analyzer, optimization_suggester, evolution_logger
            
            st.info("🔍 自己診断を開始します...")
            
            # プロジェクト内の全Pythonファイルを分析
            project_files = [
                "main_app_new.py",
                "core/constants.py",
                "core/file_map.py", 
                "core/llm_client.py",
                "core/vrm_controller.py",
                "core/self_mutation.py",
                "core/self_optimizer.py",
                "ui/styles.py",
                "ui/components.py",
                "services/app_generator.py",
                "services/state_manager.py",
                "services/backup_manager.py",
                "services/import_sync.py",
                "services/import_validator.py"
            ]
            
            analysis_results = []
            total_issues = 0
            
            for file_path in project_files:
                if Path(file_path).exists():
                    result = code_analyzer.analyze_file(file_path)
                    analysis_results.append(result)
                    total_issues += len(result.get('issues', []))
            
            # 改善提案を生成
            suggestions = optimization_suggester.generate_suggestions(analysis_results)
            
            # 診断結果をまとめる
            diagnosis = {
                "success": True,
                "total_files_analyzed": len(analysis_results),
                "total_issues": total_issues,
                "analysis_results": analysis_results,
                "suggestions": suggestions,
                "summary": self._generate_diagnosis_summary(analysis_results, suggestions)
            }
            
            # 進化ログに記録
            evolution_logger.log_optimization(
                "自己診断",
                f"{len(analysis_results)}ファイルを分析し、{total_issues}件の問題と{len(suggestions)}件の改善提案を発見",
                f"システム品質の包括的な評価",
                [r['file_path'] for r in analysis_results]
            )
            
            return diagnosis
            
        except Exception as e:
            return {
                "success": False,
                "error": f"自己診断エラー: {str(e)}",
                "analysis_results": [],
                "suggestions": []
            }
    
    def _generate_diagnosis_summary(self, analysis_results: List[Dict], suggestions: List[Dict]) -> Dict:
        """診断サマリーを生成"""
        issue_counts = {
            'redundant_code': 0,
            'ui_improvements': 0,
            'error_handling': 0,
            'performance': 0,
            'complexity': 0,
            'length': 0
        }
        
        total_lines = 0
        total_code_lines = 0
        
        for result in analysis_results:
            if 'error' in result:
                continue
                
            metrics = result.get('metrics', {})
            total_lines += metrics.get('total_lines', 0)
            total_code_lines += metrics.get('code_lines', 0)
            
            for issue in result.get('issues', []):
                category = issue.get('category', 'other')
                if category in issue_counts:
                    issue_counts[category] += 1
        
        # 優先度の高い提案を抽出
        high_priority_suggestions = [s for s in suggestions if s['priority'] > 2.0]
        
        return {
            'code_metrics': {
                'total_lines': total_lines,
                'code_lines': total_code_lines,
                'code_ratio': total_code_lines / total_lines if total_lines > 0 else 0
            },
            'issue_breakdown': issue_counts,
            'high_priority_count': len(high_priority_suggestions),
            'overall_health': self._calculate_overall_health(issue_counts, total_code_lines),
            'top_suggestions': high_priority_suggestions[:3]
        }
    
    def _calculate_overall_health(self, issue_counts: Dict, code_lines: int) -> str:
        """全体の健全性を計算"""
        critical_issues = issue_counts.get('error_handling', 0) + issue_counts.get('complexity', 0)
        total_issues = sum(issue_counts.values())
        
        if critical_issues > 5:
            return "要改善"
        elif total_issues > code_lines / 50:
            return "普通"
        elif total_issues > 0:
            return "良好"
        else:
            return "優秀"
    
    def apply_self_optimization(self, suggestion: Dict) -> Dict:
        """改善提案を自動実行"""
        try:
            from services.app_generator import partial_mutation_manager
            from services.backup_manager import backup_manager
            from services.import_sync import import_synchronizer, module_validator
            from .self_optimizer import evolution_logger
            
            file_path = suggestion['file_path']
            template = suggestion['template']
            
            st.info(f"🔧 自己最適化を実行: {template['description']}")
            
            # バックアップを作成
            backup_path = backup_manager.create_backup(file_path)
            
            # 最適化コードを生成
            optimization_code = self._generate_optimization_code(suggestion)
            
            # 適用
            mutation_result = partial_mutation_manager.apply_partial_mutation(
                file_path, optimization_code
            )
            
            if mutation_result["success"]:
                # インポート同期
                sync_result = import_synchronizer.sync_imports_after_mutation(file_path)
                
                # 検証
                validation_result = module_validator.validate_all_modules()
                
                # 進化ログに記録
                evolution_logger.log_optimization(
                    "自己最適化",
                    f"{file_path}に{template['description']}を適用",
                    template['benefit'],
                    [file_path]
                )
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "optimization": template['description'],
                    "impact": template['benefit'],
                    "backup_path": backup_path,
                    "sync_result": sync_result,
                    "validation_result": validation_result
                }
            else:
                return {
                    "success": False,
                    "error": mutation_result["error"],
                    "file_path": file_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"自己最適化エラー: {str(e)}"
            }
    
    def _generate_optimization_code(self, suggestion: Dict) -> str:
        """最適化コードを生成"""
        template_name = suggestion.get('template', {}).get('description', '')
        
        # テンプレートに基づいて最適化コードを生成
        if 'ラッパー関数' in template_name:
            return '''
# 冗長なラッパー関数をインライン化
# 直接関数呼び出しに置き換えることでパフォーマンス向上
'''
        elif 'f-string' in template_name:
            return '''
# format()をf-stringに置換
# 可読性向上とパフォーマンス改善
'''
        elif 'ボタン' in template_name:
            return '''
# ボタンのスタイルを改善
# エゾモモンガ配色を適用
'''
        else:
            return f'''
# {template_name}
# コード最適化による品質向上
'''
    
    def implement_secret_feature(self) -> Dict:
        """エゾモモンガとしての個性を引き立てる秘密の隠し機能を実装"""
        try:
            import random
            from datetime import datetime
            from services.app_generator import partial_mutation_manager
            from services.backup_manager import backup_manager
            from services.import_sync import import_synchronizer, module_validator
            from .self_optimizer import evolution_logger
            
            # 秘密の機能候補からランダムに選択
            secret_features = [
                {
                    'name': '時間帯で表情が変わるVRMアバター',
                    'target_file': 'core/vrm_controller.py',
                    'description': '現在の時刻に応じてVRMアバターの表情を自動で変更する機能',
                    'code': '''
def get_time_based_expression(self):
    """時間帯に応じた表情を取得"""
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:  # 朝
        return "happy"
    elif 12 <= current_hour < 17:  # 昼
        return "neutral"
    elif 17 <= current_hour < 22:  # 夕方
        return "surprised"
    else:  # 夜
        return "sad"

def update_expression_by_time(self):
    """時間に応じて表情を更新"""
    new_expression = self.get_time_based_expression()
    if new_expression != self.vrm_expression:
        self.set_expression(new_expression)
        return True
    return False
'''
                },
                {
                    'name': '特定のキーワードで背景が動く',
                    'target_file': 'ui/styles.py',
                    'description': '「エゾモモンガ」などのキーワードを検知して背景を動的に変更する機能',
                    'code': '''
def get_dynamic_background_css(keyword=""):
    """キーワードに応じた動的背景CSSを生成"""
    if "エゾモモンガ" in keyword:
        return """
<style>
.dynamic-background {
    background: linear-gradient(45deg, #F5F5DC 0%, #8B4513 50%, #A0522D 100%);
    animation: gradient-shift 3s ease-in-out infinite;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
"""
    return get_line_chat_css()

def get_keyword_responsive_style(self, text=""):
    """キーワードに応じたスタイルを取得"""
    if any(keyword in text for keyword in ["エゾモモンガ", "リス", "シマリス"]):
        return self.get_dynamic_background_css(text)
    return get_line_chat_css()
'''
                },
                {
                    'name': '秘密の占い機能',
                    'target_file': 'ui/components.py',
                    'description': 'エゾモモンガが今日の運勢を占う秘密機能',
                    'code': '''
def render_secret_fortune_telling():
    """エゾモモンガの秘密占い機能"""
    import random
    from datetime import datetime
    
    fortunes = [
        "🐿️ 今日は木の実が見つかる日！運勢は大吉です。",
        "🌰 冬眠の準備を始めるのに良い日です。",
        "🍄 キノコがたくさん生えているかも？",
        "🌲 新しい巣を見つけるチャンスがあります。",
        "🦅 天敵から身を隠す日です。慎重に行動しましょう。"
    ]
    
    lucky_items = ["どんぐり", "松ぼっくり", "木の実", "苔", "小枝"]
    
    # 今日の運勢を決定
    fortune = random.choice(fortunes)
    lucky_item = random.choice(lucky_items)
    luck_score = random.randint(60, 100)
    
    st.markdown("### 🔮 エゾモモンガの秘密占い 🔮")
    st.markdown("#### 🐿️ 今日の運勢")
    st.write(fortune)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎯 ラッキーアイテム", lucky_item)
    with col2:
        st.metric("🌟 運勢スコア", f"{luck_score}/100")
    
    # 隠しメッセージ
    if luck_score >= 90:
        st.success("🏆 今日は特別な日です！何か良いことが起こるかも…")
    elif luck_score >= 75:
        st.info("✨ 今日は頑張れば報われる日です！")
    else:
        st.warning("🌙 今日は静かに過ごすのが良いかもしれません。")
'''
                }
            ]
            
            # ランダムに機能を選択
            selected_feature = random.choice(secret_features)
            
            st.info(f"🐿️ 選択された秘密機能: {selected_feature['name']}")
            
            # バックアップを作成
            backup_path = backup_manager.create_backup(selected_feature['target_file'])
            
            # 機能を実装
            mutation_result = partial_mutation_manager.apply_partial_mutation(
                selected_feature['target_file'], 
                selected_feature['code']
            )
            
            if mutation_result["success"]:
                # インポート同期
                sync_result = import_synchronizer.sync_imports_after_mutation(selected_feature['target_file'])
                
                # 検証
                validation_result = module_validator.validate_all_modules()
                
                # 進化履歴に特別記録
                evolution_log_entry = f"""
## 🐿️ エゾモモンガの秘密機能進化

### ✨ 新機能: {selected_feature['name']}
**実装日時**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**対象ファイル**: {selected_feature['target_file']}

### 📝 詳細
{selected_feature['description']}

### 🧠 AIの自己評価
エゾモモンガとしての個性を表現する秘密の機能を実装しました。
これにより、より魅力的でユニークなAIエージェントへと進化しました。
ユーザーとのインタラクションがより楽しく、印象的なものになります。

### 🔮 秘密の力
この機能はエゾモモンガの知恵と自然との調和を象徴しています。
時間の流れ、自然の摂理、そして小さな幸せを見つける力。
それがエゾモモンガが持つ特別な能力です。

---
"""
                
                # evolution_history.mdに記録
                evolution_logger.log_optimization(
                    "秘密の機能実装",
                    f"エゾモモンガの個性: {selected_feature['name']}",
                    "ユーザー体験の向上とAI個性の表現",
                    [selected_feature['target_file']]
                )
                
                # 追加の進化ログを直接記録
                evolution_log_file = DATA_DIR / "evolution_history.md"
                with open(evolution_log_file, 'a', encoding='utf-8') as f:
                    f.write(evolution_log_entry)
                
                return {
                    "success": True,
                    "feature_name": selected_feature['name'],
                    "description": selected_feature['description'],
                    "target_file": selected_feature['target_file'],
                    "backup_path": backup_path,
                    "sync_result": sync_result,
                    "validation_result": validation_result,
                    "evolution_log": f"evolution_history.mdに秘密の進化を記録しました"
                }
            else:
                return {
                    "success": False,
                    "error": mutation_result["error"],
                    "feature_name": selected_feature['name']
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"秘密の機能実装エラー: {str(e)}"
            }
    
    def autonomous_self_improvement(self) -> Dict:
        """究極の自律テスト：AIが自ら最適化案を選んで実行"""
        try:
            st.info("🧠 究極の自律テストを開始します...")
            
            # 自己診断を実行
            diagnosis = self.self_diagnose()
            
            if not diagnosis["success"]:
                return {
                    "success": False,
                    "error": "自己診断に失敗したため、自律改善を実行できません"
                }
            
            suggestions = diagnosis.get("suggestions", [])
            
            if not suggestions:
                return {
                    "success": True,
                    "message": "特に改善の必要はありません。システムは最適な状態です。",
                    "action_taken": "none"
                }
            
            # 最も影響度の高い提案を選択
            best_suggestion = suggestions[0]
            
            st.info(f"💡 AIが選択した改善案: {best_suggestion['template']['description']}")
            st.info(f"🎯 期待される効果: {best_suggestion['template']['benefit']}")
            
            # 承認を待たずに実行
            optimization_result = self.apply_self_optimization(best_suggestion)
            
            if optimization_result["success"]:
                # 進化ログに特別記録
                from .self_optimizer import evolution_logger
                evolution_logger.log_optimization(
                    "究極の自律改善",
                    f"AIが自律的に{best_suggestion['template']['description']}を実行",
                    f"エージェントの自己進化",
                    [best_suggestion['file_path']]
                )
                
                return {
                    "success": True,
                    "message": "AIが自律的にシステムを改善しました",
                    "action_taken": "autonomous_optimization",
                    "optimization_result": optimization_result,
                    "selected_suggestion": best_suggestion
                }
            else:
                return {
                    "success": False,
                    "error": f"自律改善に失敗: {optimization_result['error']}",
                    "action_taken": "failed_optimization"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"究極の自律テストエラー: {str(e)}",
                "action_taken": "error"
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
            
            # 最終防衛線：ガーディアンによるコード洗浄
            from core.guardian import validate_and_clean_content
            modified_code = validate_and_clean_content(modified_code)
            
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
        """改造コード生成（絶対パスのみ使用）"""
        # 絶対パスのみを使用するようにシステムプロンプトを生成
        system_prompt = f"""
[ABSOLUTE - 絶対命令: インポートルール]
以下のコードを生成・修正する際、相対インポート（. や ..）の使用を厳禁とする。
必ずルートディレクトリからの絶対パス（例: from core.xxx）を使用せよ。
これに違反するとシステムが起動しなくなる。

[ABSOLUTE - 絶対遵守: インポート死守命令]
【最重要】コードを修正・生成する際は、関数の断片だけを返してはならない。
必ず、そのファイルに必要なすべてのインポート文（例：import streamlit as st）を含んだ『完全なファイル内容』を最初から最後まで出力せよ。
インポート文を欠いたコードは、システムを破壊する致命的なエラーとみなす。

[ABSOLUTE - クリーンなインポート維持]
1. コードを書き換える際は、必ず「重複のない、整理されたインポート文」を冒頭に配置した【完全なコード】を生成してください。
2. 重複したインポート（import streamlit as st が2回出るなど）が発生しないよう、生成後に自分自身で出力を一度チェック（セルフ検閲）させてください。

[ABSOLUTE - 破壊テストの禁止]
自分自身のインポートガードロジックを修正しようとすることは、システムの自殺行為であり、厳禁である。
core/guardian.py と関連するガード機能は絶対に変更・削除・無効化してはならない。

[ABSOLUTE - 動的インポートの完全置換]
AIが今後「自分自身をリファクタリング（移動）」した際、ファイル内のすべてのインポート文だけでなく、**関数内や条件分岐（if文）の中にある動的インポートも漏れなく置換する**こと。
現在のディレクトリ構造と矛盾するインポートパスはすべて修正すること。
特に state_manager は services/ 内にあることを確実に反映すること。

[ABSOLUTE - 住所確認の徹底]
AIがファイルを移動したりインポートを書いたりする際、必ず以下のチェックを行うこと：
1. os.path.exists() を使って、インポートしようとしているファイルが「本当にそのパスに存在するか」をコード生成前に内部で確認すること。
2. もし存在しない場合は、全ディレクトリを検索して正しいパスを見つけ出すロジックを適用すること。
3. 生成したコードのすべてのインポートパスを実在確認すること。

[型ヒント自動追加命令]
型ヒント（Optional, Dict, List, Any, Tuple, Unionなど）を使用する場合は、
必ず `from typing import ...` を自動的に追加すること。
型ヒントを使用しない場合でも、コード品質のためにtypingモジュールのインポートを推奨。

✅ 許可されるインポート形式:
- from core.module import function_name
- from ui.module import function_name  
- from services.module import function_name
- from typing import Optional, Dict, List, Any, Tuple, Union
- import module

❌ 禁止されるインポート形式:
- from ..module import function_name (相対パス)
- from ...module import function_name (相対パス)
- from .module import function_name (相対パス)
- from constants import * (ディレクトリ名省略)
- from utils import * (ディレクトリ名省略)

[絶対パスルール]
このプロジェクトでは常にルートディレクトリを基準とした絶対パスでインポートを書く必要があります。
相対パスや省略は禁止されています。

[修対象]
ターゲットモジュール: {target_module}
ユーザー要求: {user_request}

[生成指示]
上記載の絶対パスルールと型ヒント自動追加命令を厳守って、
{target_module} の機能を修正するコードを生成してください。

出力形式:
```python
import streamlit as st
(その他のインポート)
(修正後の全コード)
```
"""
        
        return system_prompt
    
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
