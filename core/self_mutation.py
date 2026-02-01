"""
自己改造マネージャー
分割後のモジュール群を対象にした自己改造プロトコル
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class ModularSelfMutationManager:
    def __init__(self):
        self.module_mapping = {
            "デザイン": "ui/styles.py",
            "UI": "ui/styles.py",
            "見た目": "ui/styles.py",
            "スタイル": "ui/styles.py",
            "AIの性格": "core/llm_client.py",
            "人格": "core/llm_client.py",
            "進化": "core/llm_client.py",
            "VRM": "core/vrm_controller.py",
            "アバター": "core/vrm_controller.py",
            "表情": "core/vrm_controller.py",
            "TODO": "ui/components.py",
            "ツール": "ui/components.py",
            "アプリ": "services/app_generator.py",
            "生成": "services/app_generator.py",
            "状態": "services/state_manager.py",
            "保存": "services/state_manager.py"
        }
        
        self.file_structure = {
            "core/": ["constants.py", "llm_client.py", "vrm_controller.py"],
            "ui/": ["styles.py", "components.py"],
            "services/": ["app_generator.py", "state_manager.py"]
        }
    
    def detect_target_module(self, user_request: str) -> Optional[str]:
        """ユーザー要求から対象モジュールを特定"""
        for keyword, module in self.module_mapping.items():
            if keyword in user_request:
                return module
        return None
    
    def get_all_python_files(self) -> List[str]:
        """すべてのPythonファイルを取得"""
        files = []
        for dir_path, file_list in self.file_structure.items():
            for file_name in file_list:
                files.append(dir_path + file_name)
        return files
    
    def analyze_file_complexity(self, file_path: str) -> Dict:
        """ファイルの複雑さを分析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = len(content.split('\n'))
            functions = len(re.findall(r'def\s+\w+', content))
            classes = len(re.findall(r'class\s+\w+', content))
            imports = len(re.findall(r'import\s+\w+|from\s+\w+', content))
            
            return {
                "lines": lines,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "complexity_score": lines + functions * 10 + classes * 20
            }
        except Exception as e:
            return {"error": str(e)}
    
    def suggest_refactoring(self) -> List[Dict]:
        """リファクタリング提案"""
        suggestions = []
        
        for file_path in self.get_all_python_files():
            analysis = self.analyze_file_complexity(file_path)
            
            if "error" not in analysis:
                if analysis["lines"] > 500:
                    suggestions.append({
                        "file": file_path,
                        "reason": f"行数が{analysis['lines']}行を超えています",
                        "action": "サブモジュールへの分割を検討",
                        "priority": "high"
                    })
                elif analysis["complexity_score"] > 300:
                    suggestions.append({
                        "file": file_path,
                        "reason": f"複雑度スコアが{analysis['complexity_score']}を超えています",
                        "action": "関数の分割を検討",
                        "priority": "medium"
                    })
        
        return suggestions
    
    def auto_add_imports(self, file_path: str, new_code: str) -> Tuple[str, List[str]]:
        """必要なimport文を自動追加"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 新コードから必要なライブラリを検出
            required_imports = self._extract_required_imports(new_code)
            existing_imports = self._extract_existing_imports(original_content)
            
            missing_imports = required_imports - existing_imports
            
            if missing_imports:
                import_lines = []
                for imp in sorted(missing_imports):
                    if imp.startswith("from"):
                        import_lines.append(f"{imp}")
                    else:
                        import_lines.append(f"import {imp}")
                
                # ファイル先頭にimportを追加
                import_section = "\n".join(import_lines) + "\n\n"
                updated_content = import_section + original_content
                
                return updated_content, list(missing_imports)
            
            return original_content, []
            
        except Exception as e:
            return new_code, [f"インポート追加エラー: {str(e)}"]
    
    def _extract_required_imports(self, code: str) -> set:
        """コードから必要なimportを抽出"""
        imports = set()
        
        # 標準ライブラリの簡単な検出
        std_libs = ["os", "sys", "json", "re", "datetime", "pathlib", "time", "random"]
        
        for lib in std_libs:
            if lib in code and f"import {lib}" not in code:
                imports.add(lib)
        
        return imports
    
    def _extract_existing_imports(self, content: str) -> set:
        """既存のimportを抽出"""
        imports = set()
        
        import_lines = re.findall(r'^(import\s+\w+|from\s+\w+\s+import\s+.+)', content, re.MULTILINE)
        for line in import_lines:
            if line.startswith("import "):
                imports.add(line.replace("import ", "").strip())
            elif line.startswith("from "):
                imports.add(line.strip())
        
        return imports
    
    def update_requirements_txt(self, new_imports: List[str]) -> bool:
        """requirements.txtを更新"""
        try:
            req_file = Path("requirements.txt")
            existing_packages = set()
            
            if req_file.exists():
                with open(req_file, 'r', encoding='utf-8') as f:
                    existing_packages = set(line.strip() for line in f if line.strip())
            
            # 新しいパッケージを追加
            for imp in new_imports:
                if imp not in existing_packages:
                    existing_packages.add(imp)
            
            # 保存
            with open(req_file, 'w', encoding='utf-8') as f:
                for package in sorted(existing_packages):
                    f.write(f"{package}\n")
            
            return True
            
        except Exception as e:
            print(f"requirements.txt更新エラー: {e}")
            return False
