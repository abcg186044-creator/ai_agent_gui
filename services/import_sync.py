"""
インポート同期モジュール
モジュール間の依存関係を検出し、インポート文を自動修正
"""

import re
import ast
import importlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from core.constants import *

class ImportAnalyzer:
    """インポート分析クラス"""
    
    @staticmethod
    def extract_imports(file_path: str) -> Dict[str, List[str]]:
        """ファイルからインポート情報を抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            imports = {
                'direct_imports': [],  # import module
                'from_imports': {},    # from module import name
                'functions': set(),   # 定義されている関数
                'classes': set()       # 定義されているクラス
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports['direct_imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        if module not in imports['from_imports']:
                            imports['from_imports'][module] = []
                        imports['from_imports'][module].append(alias.name)
                
                elif isinstance(node, ast.FunctionDef):
                    imports['functions'].add(node.name)
                
                elif isinstance(node, ast.ClassDef):
                    imports['classes'].add(node.name)
            
            return imports
            
        except Exception as e:
            print(f"インポート分析エラー {file_path}: {e}")
            return {'direct_imports': [], 'from_imports': {}, 'functions': set(), 'classes': set()}
    
    @staticmethod
    def find_function_calls(file_path: str) -> Set[str]:
        """ファイル内の関数呼び出しを検出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 関数呼び出しパターンを検出
            patterns = [
                r'(\w+)\s*\(',           # function()
                r'(\w+)\s*\.',           # module.function
                r'from\s+(\w+)\s+import', # from module import
                r'import\s+(\w+)',        # import module
            ]
            
            called_names = set()
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        called_names.update(match)
                    else:
                        called_names.add(match)
            
            return called_names
            
        except Exception as e:
            print(f"関数呼び出し検出エラー {file_path}: {e}")
            return set()

class ImportSynchronizer:
    """インポート同期クラス"""
    
    def __init__(self):
        self.analyzer = ImportAnalyzer()
        self.file_map = {
            "main_app_new.py": ["ui/styles", "ui/components", "core/*", "services/*"],
            "ui/components.py": ["core/constants", "services/state_manager", "services/app_generator"],
            "ui/styles.py": ["core/constants"],
            "core/llm_client.py": ["core/constants", "core/self_mutation", "core/file_map"],
            "core/vrm_controller.py": ["core/constants"],
            "services/app_generator.py": ["core/constants", "services/backup_manager"],
            "services/state_manager.py": ["core/constants", "core/file_map"]
        }
    
    def sync_imports_after_mutation(self, modified_file: str) -> Dict:
        """モジュール修正後のインポート同期"""
        try:
            sync_results = {
                "success": True,
                "modified_files": [],
                "errors": [],
                "synced_imports": []
            }
            
            # 修正されたファイルの新しいエクスポートを取得
            modified_imports = self.analyzer.extract_imports(modified_file)
            
            # このファイルをインポートしているファイルを特定
            dependent_files = self._find_dependent_files(modified_file)
            
            for dependent_file in dependent_files:
                try:
                    # 依存ファイルの現在のインポートを分析
                    current_imports = self.analyzer.extract_imports(dependent_file)
                    
                    # 同期が必要かチェック
                    needed_sync = self._check_sync_needed(
                        dependent_file, modified_file, current_imports, modified_imports
                    )
                    
                    if needed_sync:
                        # インポート文を修正
                        sync_result = self._update_imports(
                            dependent_file, modified_file, needed_sync
                        )
                        
                        if sync_result["success"]:
                            sync_results["modified_files"].append(dependent_file)
                            sync_results["synced_imports"].extend(sync_result["updated_imports"])
                        else:
                            sync_results["errors"].append(
                                f"{dependent_file}: {sync_result['error']}"
                            )
                
                except Exception as e:
                    sync_results["errors"].append(f"{dependent_file}: {str(e)}")
            
            if sync_results["errors"]:
                sync_results["success"] = len(sync_results["errors"]) == 0
            
            return sync_results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"インポート同期エラー: {str(e)}",
                "modified_files": [],
                "errors": [str(e)],
                "synced_imports": []
            }
    
    def _find_dependent_files(self, modified_file: str) -> List[str]:
        """修正されたファイルに依存するファイルを検出"""
        dependent_files = []
        
        # ファイルマップから逆引き
        modified_module = self._path_to_module(modified_file)
        
        for file_path, modules in self.file_map.items():
            for module in modules:
                if self._module_matches(modified_module, module):
                    dependent_files.append(file_path)
        
        return dependent_files
    
    def _path_to_module(self, file_path: str) -> str:
        """ファイルパスをモジュール名に変換"""
        if file_path.endswith('.py'):
            file_path = file_path[:-3]
        return file_path.replace('/', '.')
    
    def _module_matches(self, target_module: str, pattern: str) -> bool:
        """モジュールパターンマッチング"""
        if pattern == target_module:
            return True
        elif pattern.endswith('*'):
            base_pattern = pattern[:-1]
            return target_module.startswith(base_pattern)
        return False
    
    def _check_sync_needed(self, dependent_file: str, modified_file: str, 
                          current_imports: Dict, modified_imports: Dict) -> Dict:
        """同期が必要かチェック"""
        sync_needed = {}
        
        modified_module = self._path_to_module(modified_file)
        
        # 新しく追加された関数/クラスをチェック
        new_functions = modified_imports.get('functions', set())
        new_classes = modified_imports.get('classes', set())
        
        # 現在のインポートをチェック
        from_imports = current_imports.get('from_imports', {})
        
        if modified_module in from_imports:
            current_imported = set(from_imports[modified_module])
            needed_imports = new_functions | new_classes
            
            missing_imports = needed_imports - current_imported
            if missing_imports:
                sync_needed['add_imports'] = list(missing_imports)
        
        return sync_needed
    
    def _update_imports(self, dependent_file: str, modified_file: str, 
                       sync_needed: Dict) -> Dict:
        """インポート文を更新"""
        try:
            with open(dependent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified_module = self._path_to_module(modified_file)
            
            # インポート文を更新
            if 'add_imports' in sync_needed:
                content = self._add_to_import_statement(
                    content, modified_module, sync_needed['add_imports']
                )
            
            # 更新された内容を保存
            with open(dependent_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "updated_imports": sync_needed.get('add_imports', [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _add_to_import_statement(self, content: str, module: str, imports: List[str]) -> str:
        """既存のimport文に追加"""
        lines = content.split('\n')
        updated_lines = []
        import_updated = False
        
        for line in lines:
            updated_lines.append(line)
            
            # from module import ... を検出
            if line.strip().startswith(f'from {module} import'):
                # 既存のimport文に追加
                existing_imports = line.strip().split('import')[1].strip()
                if existing_imports:
                    all_imports = existing_imports.split(',') + imports
                    all_imports = [imp.strip() for imp in all_imports if imp.strip()]
                    all_imports = sorted(list(set(all_imports)))
                    
                    new_import_line = f"from {module} import {', '.join(all_imports)}"
                    updated_lines[-1] = new_import_line
                    import_updated = True
                    break
        
        # 該当するimport文が見つからない場合は新規追加
        if not import_updated:
            # ファイルの先頭に追加
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_pos = i + 1
                elif line.strip() and not line.startswith('#'):
                    break
            
            new_import_line = f"from {module} import {', '.join(sorted(imports))}"
            updated_lines.insert(insert_pos, new_import_line)
        
        return '\n'.join(updated_lines)

class ModuleValidator:
    """モジュールバリデーションクラス"""
    
    @staticmethod
    def validate_all_modules() -> Dict:
        """すべてのモジュールのバリデーション"""
        validation_results = {
            "success": True,
            "valid_modules": [],
            "invalid_modules": [],
            "errors": []
        }
        
        # 検証対象モジュールリスト
        modules_to_check = [
            "core.constants",
            "core.file_map", 
            "core.llm_client",
            "core.vrm_controller",
            "core.self_mutation",
            "ui.styles",
            "ui.components",
            "services.app_generator",
            "services.state_manager",
            "services.backup_manager",
            "main_app_new"
        ]
        
        for module_name in modules_to_check:
            try:
                # モジュールをインポートして検証
                module = importlib.import_module(module_name)
                
                # モジュールの基本属性をチェック
                if hasattr(module, '__file__') and module.__file__:
                    validation_results["valid_modules"].append(module_name)
                else:
                    validation_results["invalid_modules"].append(module_name)
                    validation_results["errors"].append(f"{module_name}: モジュールファイルが見つかりません")
                
            except ImportError as e:
                validation_results["invalid_modules"].append(module_name)
                validation_results["errors"].append(f"{module_name}: {str(e)}")
            except Exception as e:
                validation_results["invalid_modules"].append(module_name)
                validation_results["errors"].append(f"{module_name}: {str(e)}")
        
        validation_results["success"] = len(validation_results["invalid_modules"]) == 0
        
        return validation_results
    
    @staticmethod
    def validate_specific_module(module_name: str) -> Dict:
        """特定のモジュールのバリデーション"""
        try:
            module = importlib.import_module(module_name)
            
            return {
                "success": True,
                "module_name": module_name,
                "file_path": getattr(module, '__file__', None),
                "message": f"{module_name} は正常にロードできました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "module_name": module_name,
                "error": str(e),
                "message": f"{module_name} のロードに失敗しました: {str(e)}"
            }

# グローバルインスタンス
import_synchronizer = ImportSynchronizer()
module_validator = ModuleValidator()
