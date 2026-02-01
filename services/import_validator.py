"""
インポート不足検知と自動修正モジュール
AttributeErrorやImportErrorをキャッチし、自動的にインポートを修正
"""

import re
import ast
import importlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from core.constants import *

class ImportErrorDetector:
    """インポートエラー検知クラス"""
    
    def __init__(self):
        self.error_patterns = {
            'AttributeError': r"AttributeError: module '(\w+)' has no attribute '(\w+)'",
            'ImportError': r"ImportError: cannot import name '(\w+)' from '(\w+)'",
            'ModuleNotFoundError': r"ModuleNotFoundError: No module named '(\w+)'"
        }
    
    def analyze_error(self, error_message: str) -> Dict:
        """エラーメッセージを解析して不足しているインポートを特定"""
        for error_type, pattern in self.error_patterns.items():
            match = re.search(pattern, error_message)
            if match:
                if error_type == 'AttributeError':
                    module_name, missing_attribute = match.groups()
                    return {
                        'error_type': error_type,
                        'module_name': module_name,
                        'missing_name': missing_attribute,
                        'suggested_fix': f'from {module_name} import {missing_attribute}'
                    }
                elif error_type == 'ImportError':
                    missing_name, module_name = match.groups()
                    return {
                        'error_type': error_type,
                        'module_name': module_name,
                        'missing_name': missing_name,
                        'suggested_fix': f'from {module_name} import {missing_name}'
                    }
                elif error_type == 'ModuleNotFoundError':
                    module_name = match.groups()[0]
                    return {
                        'error_type': error_type,
                        'module_name': module_name,
                        'missing_name': None,
                        'suggested_fix': f'import {module_name}'
                    }
        
        return {'error_type': 'unknown', 'module_name': None, 'missing_name': None, 'suggested_fix': None}
    
    def find_missing_imports_in_file(self, file_path: str) -> List[Dict]:
        """ファイル内の潜在的なインポート不足を検出"""
        missing_imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST解析で使用されている関数/クラスを抽出
            tree = ast.parse(content)
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # module.function 形式の呼び出し
                    if isinstance(node.value, ast.Name):
                        used_names.add(f"{node.value.id}.{node.attr}")
            
            # 現在のインポートを取得
            current_imports = self._extract_current_imports(content)
            
            # 不足しているインポートを推定
            for name in used_names:
                if '.' in name:
                    module_part, attr_part = name.rsplit('.', 1)
                    if module_part in ['ui', 'core', 'services']:
                        if name not in current_imports:
                            missing_imports.append({
                                'missing_name': name,
                                'module_name': module_part,
                                'suggested_fix': f'from {module_part} import {attr_part}'
                            })
            
        except Exception as e:
            print(f"インポート不足検出エラー {file_path}: {e}")
        
        return missing_imports
    
    def _extract_current_imports(self, content: str) -> Set[str]:
        """現在のインポートを抽出"""
        imports = set()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.add(f"{module}.{alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
        
        return imports

class AutoImportFixer:
    """自動インポート修正クラス"""
    
    def __init__(self):
        self.detector = ImportErrorDetector()
        self.module_mappings = {
            'ui': ['styles', 'components'],
            'core': ['constants', 'llm_client', 'vrm_controller', 'file_map', 'self_mutation'],
            'services': ['app_generator', 'state_manager', 'backup_manager', 'import_sync']
        }
    
    def fix_import_error(self, error_info: Dict, target_file: str) -> Dict:
        """インポートエラーを自動修正"""
        try:
            if error_info['error_type'] == 'unknown':
                return {'success': False, 'error': '不明なエラータイプ'}
            
            # 修正候補を生成
            fix_candidates = self._generate_fix_candidates(error_info)
            
            for candidate in fix_candidates:
                result = self._apply_import_fix(target_file, candidate)
                if result['success']:
                    return {
                        'success': True,
                        'applied_fix': candidate,
                        'message': f"インポートを自動修正しました: {candidate}"
                    }
            
            return {'success': False, 'error': '適切な修正候補が見つかりません'}
            
        except Exception as e:
            return {'success': False, 'error': f"自動修正エラー: {str(e)}"}
    
    def _generate_fix_candidates(self, error_info: Dict) -> List[str]:
        """修正候補を生成"""
        candidates = []
        
        if error_info['suggested_fix']:
            candidates.append(error_info['suggested_fix'])
        
        # モジュール名から推定
        module_name = error_info['module_name']
        missing_name = error_info['missing_name']
        
        if module_name in self.module_mappings:
            for submodule in self.module_mappings[module_name]:
                candidates.append(f'from {module_name}.{submodule} import {missing_name}')
        
        return list(set(candidates))  # 重複を除去
    
    def _apply_import_fix(self, target_file: str, import_statement: str) -> Dict:
        """インポート修正を適用"""
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            updated_lines = []
            import_added = False
            
            # 適切な位置にインポートを追加
            for i, line in enumerate(lines):
                updated_lines.append(line)
                
                # 既存のインポート文の後に追加
                if line.strip().startswith(('import ', 'from ')) and not import_added:
                    # 次の行がインポート文でない場合に追加
                    if (i + 1 < len(lines) and 
                        not lines[i + 1].strip().startswith(('import ', 'from ', '#'))):
                        updated_lines.append(import_statement)
                        import_added = True
                elif line.strip() and not line.startswith('#') and not import_added:
                    # 最初の空行でない行の前に追加
                    updated_lines.insert(-1, import_statement)
                    updated_lines.insert(-1, '')
                    import_added = True
                    break
            
            # インポートが追加されなかった場合はファイル先頭に追加
            if not import_added:
                updated_lines.insert(0, import_statement)
                updated_lines.insert(1, '')
            
            # 修正された内容を保存
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_import_fix(self, target_file: str) -> Dict:
        """インポート修正の妥当性を検証"""
        try:
            # モジュールを動的にインポートして検証
            spec = importlib.util.spec_from_file_location("test_module", target_file)
            if spec and spec.loader:
                test_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_module)
                return {'success': True, 'message': 'インポート修正は正常です'}
            else:
                return {'success': False, 'error': 'モジュールの読み込みに失敗'}
                
        except Exception as e:
            return {'success': False, 'error': f'検証エラー: {str(e)}'}

class CircularDependencyChecker:
    """循環参照チェッカー"""
    
    def __init__(self):
        self.dependency_graph = {}
        self.build_dependency_graph()
    
    def build_dependency_graph(self):
        """依存関係グラフを構築"""
        # プロジェクトの依存関係を定義
        self.dependency_graph = {
            'main_app_new': ['ui.styles', 'ui.components', 'core.constants', 'core.llm_client', 
                           'core.vrm_controller', 'services.app_generator', 'services.state_manager'],
            'ui.styles': ['core.constants'],
            'ui.components': ['core.constants', 'services.state_manager', 'services.app_generator'],
            'core.llm_client': ['core.constants', 'core.self_mutation', 'core.file_map'],
            'core.vrm_controller': ['core.constants'],
            'services.app_generator': ['core.constants', 'services.backup_manager'],
            'services.state_manager': ['core.constants', 'core.file_map'],
            'services.import_sync': ['core.constants'],
            'services.backup_manager': [],
            'core.file_map': [],
            'core.self_mutation': ['core.constants']
        }
    
    def check_circular_dependencies(self) -> Dict:
        """循環参照をチェック"""
        try:
            visited = set()
            rec_stack = set()
            circular_deps = []
            
            def dfs(node, path):
                if node in rec_stack:
                    # 循環を検出
                    cycle_start = path.index(node)
                    circular_deps.append(path[cycle_start:] + [node])
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in self.dependency_graph.get(node, []):
                    dfs(neighbor, path + [node])
                
                rec_stack.remove(node)
            
            # すべてのノードでDFSを実行
            for node in self.dependency_graph:
                if node not in visited:
                    dfs(node, [])
            
            if circular_deps:
                return {
                    'has_circular': True,
                    'circular_dependencies': circular_deps,
                    'message': f'{len(circular_deps)}個の循環参照が検出されました'
                }
            else:
                return {
                    'has_circular': False,
                    'circular_dependencies': [],
                    'message': '循環参照はありません'
                }
                
        except Exception as e:
            return {
                'has_circular': True,
                'circular_dependencies': [],
                'error': f'循環参照チェックエラー: {str(e)}'
            }
    
    def suggest_dependency_fixes(self) -> List[str]:
        """依存関係の修正提案"""
        suggestions = []
        
        # main_app_newがハブとなる構造を推奨
        suggestions.append("main_app_newを中央ハブとし、他モジュール間の直接依存を避けてください")
        suggestions.append("coreモジュールは他モジュールに依存しない独立した設計を維持してください")
        suggestions.append("uiモジュールはservicesに直接依存せず、main_app_new経由で連携してください")
        
        return suggestions

# グローバルインスタンス
import_error_detector = ImportErrorDetector()
auto_import_fixer = AutoImportFixer()
circular_dependency_checker = CircularDependencyChecker()
