import ast
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class VerificationProtocols:
    """
    コードの構文エラーと基本的な品質チェックを行う検証プロトコル
    """
    
    def __init__(self):
        self.error_patterns = {
            "syntax": [],
            "import": [],
            "logic": [],
            "style": []
        }
    
    def verify_file(self, file_path: str) -> Dict[str, any]:
        """
        単一ファイルの包括的検証を実行
        
        Args:
            file_path: 検証対象ファイルパス
            
        Returns:
            検証結果辞書
        """
        result = {
            "file": file_path,
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        if not Path(file_path).exists():
            result["valid"] = False
            result["errors"].append(f"ファイルが存在しません: {file_path}")
            return result
        
        # Pythonファイルの場合
        if file_path.endswith('.py'):
            return self._verify_python_file(file_path)
        
        # 他のファイルタイプの場合
        return self._verify_generic_file(file_path)
    
    def _verify_python_file(self, file_path: str) -> Dict[str, any]:
        """Pythonファイルの検証"""
        result = {
            "file": file_path,
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 1. 構文チェック
            syntax_result = self._check_syntax(content)
            if not syntax_result["valid"]:
                result["valid"] = False
                result["errors"].extend(syntax_result["errors"])
            
            # 2. インポートチェック
            import_result = self._check_imports(content)
            result["warnings"].extend(import_result["warnings"])
            
            # 3. 基本的な品質チェック
            quality_result = self._check_quality(content)
            result["warnings"].extend(quality_result["warnings"])
            result["metrics"] = quality_result["metrics"]
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"ファイル読み込みエラー: {e}")
        
        return result
    
    def _check_syntax(self, content: str) -> Dict[str, any]:
        """Python構文チェック"""
        result = {"valid": True, "errors": []}
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            result["valid"] = False
            result["errors"].append({
                "type": "syntax",
                "line": e.lineno,
                "column": e.offset,
                "message": str(e)
            })
        except Exception as e:
            result["valid"] = False
            result["errors"].append({
                "type": "parse",
                "message": f"解析エラー: {e}"
            })
        
        return result
    
    def _check_imports(self, content: str) -> Dict[str, any]:
        """インポート文のチェック"""
        result = {"valid": True, "warnings": []}
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not self._is_valid_import(alias.name):
                            result["warnings"].append({
                                "type": "import",
                                "message": f"不明なインポート: {alias.name}"
                            })
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not self._is_valid_import(node.module):
                        result["warnings"].append({
                            "type": "import",
                            "message": f"不明なインポート: {node.module}"
                        })
        
        except Exception:
            # 構文エラーがある場合はスキップ
            pass
        
        return result
    
    def _is_valid_import(self, module_name: str) -> bool:
        """インポートモジュールの妥当性チェック"""
        # 標準ライブラリのチェック
        standard_modules = {
            'os', 'sys', 'json', 're', 'datetime', 'pathlib', 'typing',
            'time', 'threading', 'subprocess', 'ast', 'shutil', 'collections'
        }
        
        # サードパーティライブラリのチェック
        third_party_modules = {
            'streamlit', 'numpy', 'pandas', 'requests', 'ollama',
            'sounddevice', 'pyttsx3', 'fastapi', 'uvicorn'
        }
        
        base_name = module_name.split('.')[0]
        
        return base_name in standard_modules or base_name in third_party_modules
    
    def _check_quality(self, content: str) -> Dict[str, any]:
        """コード品質チェック"""
        result = {"valid": True, "warnings": [], "metrics": {}}
        
        lines = content.split('\n')
        
        # 基本メトリクス
        result["metrics"] = {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
            "empty_lines": len([l for l in lines if not l.strip()])
        }
        
        # 品質警告
        if result["metrics"]["total_lines"] > 1000:
            result["warnings"].append({
                "type": "quality",
                "message": "ファイルが非常に大きいです（1000行以上）"
            })
        
        # インデントチェック
        for i, line in enumerate(lines, 1):
            if line.startswith('\t') and ' ' in line:
                result["warnings"].append({
                    "type": "style",
                    "line": i,
                    "message": "タブとスペースが混在しています"
                })
        
        return result
    
    def _verify_generic_file(self, file_path: str) -> Dict[str, any]:
        """一般的なファイルの検証"""
        result = {
            "file": file_path,
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 基本チェック
            if len(content) == 0:
                result["warnings"].append("ファイルが空です")
            
            # JSONファイルの場合
            if file_path.endswith('.json'):
                try:
                    import json
                    json.loads(content)
                except json.JSONDecodeError as e:
                    result["valid"] = False
                    result["errors"].append(f"JSON形式エラー: {e}")
            
            result["metrics"] = {
                "file_size": len(content),
                "line_count": len(content.split('\n'))
            }
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"ファイル検証エラー: {e}")
        
        return result
    
    def verify_project(self, project_path: str = ".") -> Dict[str, any]:
        """
        プロジェクト全体の検証を実行
        
        Args:
            project_path: プロジェクトルートパス
            
        Returns:
            プロジェクト検証結果
        """
        project_result = {
            "project_path": project_path,
            "valid": True,
            "files": [],
            "summary": {
                "total_files": 0,
                "valid_files": 0,
                "invalid_files": 0,
                "total_errors": 0,
                "total_warnings": 0
            }
        }
        
        project_dir = Path(project_path)
        
        # Pythonファイルを検索
        python_files = list(project_dir.glob("*.py"))
        
        for file_path in python_files:
            file_result = self.verify_file(str(file_path))
            project_result["files"].append(file_result)
            
            project_result["summary"]["total_files"] += 1
            
            if file_result["valid"]:
                project_result["summary"]["valid_files"] += 1
            else:
                project_result["summary"]["invalid_files"] += 1
                project_result["valid"] = False
            
            project_result["summary"]["total_errors"] += len(file_result["errors"])
            project_result["summary"]["total_warnings"] += len(file_result["warnings"])
        
        return project_result
    
    def run_pytest(self, test_path: str = "tests/") -> Dict[str, any]:
        """
        pytestを実行してテストを検証
        
        Args:
            test_path: テストファイルパス
            
        Returns:
            テスト実行結果
        """
        result = {
            "ran": False,
            "success": False,
            "output": "",
            "errors": []
        }
        
        if not Path(test_path).exists():
            result["errors"].append(f"テストディレクトリが存在しません: {test_path}")
            return result
        
        try:
            # pytestを実行
            process = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result["ran"] = True
            result["output"] = process.stdout
            result["success"] = process.returncode == 0
            
            if process.returncode != 0:
                result["errors"].append(process.stderr)
        
        except subprocess.TimeoutExpired:
            result["errors"].append("テスト実行がタイムアウトしました")
        except Exception as e:
            result["errors"].append(f"テスト実行エラー: {e}")
        
        return result
    
    def generate_report(self, verification_result: Dict) -> str:
        """
        検証結果のレポートを生成
        
        Args:
            verification_result: 検証結果
            
        Returns:
            レポート文字列
        """
        if "files" in verification_result:
            # プロジェクトレポート
            return self._generate_project_report(verification_result)
        else:
            # ファイルレポート
            return self._generate_file_report(verification_result)
    
    def _generate_project_report(self, result: Dict) -> str:
        """プロジェクト検証レポートを生成"""
        summary = result["summary"]
        
        report = f"""
# プロジェクト検証レポート

## 概要
- プロジェクトパス: {result['project_path']}
- 総ファイル数: {summary['total_files']}
- 有効ファイル: {summary['valid_files']}
- 無効ファイル: {summary['invalid_files']}
- エラー総数: {summary['total_errors']}
- 警告総数: {summary['total_warnings']}

## 結論
"""
        
        if result["valid"]:
            report += "✅ プロジェクトは検証に合格しました"
        else:
            report += "❌ プロジェクトには問題があります"
        
        return report
    
    def _generate_file_report(self, result: Dict) -> str:
        """ファイル検証レポートを生成"""
        report = f"""
# ファイル検証レポート

## ファイル: {result['file']}
- 状態: {'✅ 有効' if result['valid'] else '❌ 無効'}
- エラー数: {len(result['errors'])}
- 警告数: {len(result['warnings'])}

"""
        
        if result["errors"]:
            report += "## エラー\n"
            for error in result["errors"]:
                report += f"- {error}\n"
        
        if result["warnings"]:
            report += "## 警告\n"
            for warning in result["warnings"]:
                report += f"- {warning}\n"
        
        if result["metrics"]:
            report += "## メトリクス\n"
            for key, value in result["metrics"].items():
                report += f"- {key}: {value}\n"
        
        return report
