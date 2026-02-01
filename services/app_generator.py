"""
アプリジェネレーターモジュール
外部ファイルの生成・インポート・実行管理を担当
"""

import os
import re
import importlib.util
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, List, Any
from core.constants import *
from services.backup_manager import backup_manager

class CodeExtractor:
    """コード抽出クラス"""
    
    @staticmethod
    def extract_functions(file_path: str, target_functions: List[str] = None) -> Dict:
        """ファイルから関数を抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = {}
            lines = content.split('\n')
            
            current_function = None
            function_lines = []
            indent_level = 0
            
            for line_num, line in enumerate(lines, 1):
                # 関数定義を検出
                func_match = re.match(r'^(\s*)def\s+(\w+)\s*\(', line)
                if func_match:
                    # 前の関数を保存
                    if current_function:
                        functions[current_function] = {
                            'code': '\n'.join(function_lines),
                            'start_line': function_start,
                            'indent': indent_level
                        }
                    
                    # 新しい関数を開始
                    current_function = func_match.group(2)
                    function_lines = [line]
                    function_start = line_num
                    indent_level = len(func_match.group(1))
                    
                    # ターゲット関数でない場合はスキップ
                    if target_functions and current_function not in target_functions:
                        current_function = None
                        continue
                elif current_function:
                    # 関数の終了を検出（同じかより浅いインデント）
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                        functions[current_function] = {
                            'code': '\n'.join(function_lines),
                            'start_line': function_start,
                            'indent': indent_level
                        }
                        current_function = None
                        function_lines = []
                    else:
                        function_lines.append(line)
            
            # 最後の関数を保存
            if current_function:
                functions[current_function] = {
                    'code': '\n'.join(function_lines),
                    'start_line': function_start,
                    'indent': indent_level
                }
            
            return functions
            
        except Exception as e:
            print(f"関数抽出エラー: {e}")
            return {}
    
    @staticmethod
    def extract_classes(file_path: str, target_classes: List[str] = None) -> Dict:
        """ファイルからクラスを抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            classes = {}
            lines = content.split('\n')
            
            current_class = None
            class_lines = []
            class_indent = 0
            
            for line_num, line in enumerate(lines, 1):
                # クラス定義を検出
                class_match = re.match(r'^(\s*)class\s+(\w+)', line)
                if class_match:
                    # 前のクラスを保存
                    if current_class:
                        classes[current_class] = {
                            'code': '\n'.join(class_lines),
                            'start_line': class_start,
                            'indent': class_indent
                        }
                    
                    # 新しいクラスを開始
                    current_class = class_match.group(2)
                    class_lines = [line]
                    class_start = line_num
                    class_indent = len(class_match.group(1))
                    
                    # ターゲットクラスでない場合はスキップ
                    if target_classes and current_class not in target_classes:
                        current_class = None
                        continue
                elif current_class:
                    # クラスの終了を検出
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() and current_indent <= class_indent and not line.strip().startswith('#'):
                        classes[current_class] = {
                            'code': '\n'.join(class_lines),
                            'start_line': class_start,
                            'indent': class_indent
                        }
                        current_class = None
                        class_lines = []
                    else:
                        class_lines.append(line)
            
            # 最後のクラスを保存
            if current_class:
                classes[current_class] = {
                    'code': '\n'.join(class_lines),
                    'start_line': class_start,
                    'indent': class_indent
                }
            
            return classes
            
        except Exception as e:
            print(f"クラス抽出エラー: {e}")
            return {}
    
    @staticmethod
    def extract_imports(file_path: str) -> List[str]:
        """ファイルからimport文を抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
            
            return imports
            
        except Exception as e:
            print(f"import抽出エラー: {e}")
            return []

class PartialMutationManager:
    """局所的な自己書き換えマネージャー"""
    
    def __init__(self):
        self.code_extractor = CodeExtractor()
    
    def apply_partial_mutation(self, file_path: str, new_code: str, target_function: str = None, target_class: str = None) -> Dict:
        """指定されたファイルの一部のみを書き換え"""
        try:
            # バックアップを作成
            backup_path = backup_manager.create_backup(file_path)
            
            if not backup_path:
                return {
                    "success": False,
                    "error": "バックアップ作成に失敗しました"
                }
            
            # ファイルを読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # ターゲットを特定して置換
            if target_function:
                success, modified_content = self._replace_function(original_content, target_function, new_code)
            elif target_class:
                success, modified_content = self._replace_class(original_content, target_class, new_code)
            else:
                # ファイル全体に追加
                modified_content = original_content + '\n\n' + new_code
                success = True
            
            if success:
                # 物理ガード（プレフィックス強制）：ファイル書き込み直前にインポートをチェック・注入
                protected_content = self._apply_streamlit_prefix_guard(modified_content)
                
                # 変更を保存
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(protected_content)
                
                return {
                    "success": True,
                    "backup_path": backup_path,
                    "modified_content": modified_content,
                    "message": f"{file_path} の一部を正常に書き換えました"
                }
            else:
                return {
                    "success": False,
                    "error": "ターゲットの置換に失敗しました",
                    "backup_path": backup_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"局所的書き換えエラー: {str(e)}"
            }
    
    def _apply_streamlit_prefix_guard(self, content: str) -> str:
        """物理ガード（プレフィックス強制）：streamlitインポートを強制注入"""
        try:
            # 書き込もうとしている文字列をチェック
            if 'import streamlit as st' not in content:
                print(f"🛡️ 物理ガード：streamlitインポートを強制注入")
                print(f"   元の文字列長: {len(content)}文字")
                
                # 強制注入：先頭にstreamlitインポートを結合
                protected_content = 'import streamlit as st\n' + content
                
                print(f"   注入後の文字列長: {len(protected_content)}文字")
                return protected_content
            else:
                print(f"✅ 物理ガード：streamlitインポートを確認")
                return content
                
        except Exception as e:
            print(f"⚠️ 物理ガードエラー: {e}")
            # エラー時でもstreamlitインポートを強制注入
            return 'import streamlit as st\n' + content
    
    def _replace_function(self, content: str, function_name: str, new_code: str) -> tuple:
        """関数を置換"""
        try:
            functions = self.code_extractor.extract_functions(content, [function_name])
            
            if function_name not in functions:
                return False, content
            
            func_info = functions[function_name]
            old_func_code = func_info['code']
            
            # 置換
            modified_content = content.replace(old_func_code, new_code)
            
            return True, modified_content
            
        except Exception as e:
            print(f"関数置換エラー: {e}")
            return False, content
    
    def _replace_class(self, content: str, class_name: str, new_code: str) -> tuple:
        """クラスを置換"""
        try:
            classes = self.code_extractor.extract_classes(content, [class_name])
            
            if class_name not in classes:
                return False, content
            
            class_info = classes[class_name]
            old_class_code = class_info['code']
            
            # 置換
            modified_content = content.replace(old_class_code, new_code)
            
            return True, modified_content
            
        except Exception as e:
            print(f"クラス置換エラー: {e}")
            return False, content
    
    def generate_focused_prompt(self, file_path: str, user_request: str, target_function: str = None) -> str:
        """修正が必要な部分のみを抽出して最適化されたプロンプトを生成"""
        try:
            # import文を取得
            imports = self.code_extractor.extract_imports(file_path)
            
            # ターゲットコードを抽出
            if target_function:
                functions = self.code_extractor.extract_functions(file_path, [target_function])
                target_code = functions.get(target_function, {}).get('code', '')
                context_info = f"関数: {target_function}"
            else:
                # ファイル全体の先頭部分を取得
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                target_code = ''.join(lines[:50])  # 先頭50行
                context_info = "ファイル先頭部分"
            
            # 最適化されたプロンプトを生成
            prompt = f"""
# コード修正タスク

## ファイル情報
- ファイルパス: {file_path}
- 修正対象: {context_info}
- ユーザー要求: {user_request}

## 現在のコード
```python
# Import文
{chr(10).join(imports)}

# 修正対象コード
{target_code}
```

## 修正指示
以下の要件に従ってコードを修正してください：

1. ユーザーの要求: {user_request}
2. 既存の機能を維持すること
3. エラーハンドリングを追加すること
4. コードスタイルを統一すること

## 出力形式
修正後のコードのみを出力してください。説明は不要です。
"""
            
            return prompt
            
        except Exception as e:
            print(f"プロンプト生成エラー: {e}")
            return f"コード修正: {user_request}"

# グローバルインスタンス
partial_mutation_manager = PartialMutationManager()

class MultiLanguageCodeGenerator:
    def __init__(self):
        self.supported_languages = {
            'python': {'extension': '.py', 'template': self._get_python_template},
            'javascript': {'extension': '.js', 'template': self._get_js_template},
            'html': {'extension': '.html', 'template': self._get_html_template},
            'css': {'extension': '.css', 'template': self._get_css_template},
        }
    
    def generate_code_from_instruction(self, instruction, filename="generated_app"):
        """指示からコードを生成"""
        try:
            # 言語を検出
            detected_language = self._detect_language(instruction)
            
            # コードを生成
            code = self._generate_code(instruction, detected_language)
            
            if code:
                # ファイルに保存
                file_path = self._save_code_file(code, filename, detected_language)
                return code, detected_language, f"✅ {detected_language}コードを生成しました: {file_path}"
            else:
                return None, detected_language, "❌ コード生成に失敗しました"
        
        except Exception as e:
            return None, 'python', f"❌ コード生成エラー: {str(e)}"
    
    def _detect_language(self, instruction):
        """指示から言語を検出"""
        instruction_lower = instruction.lower()
        
        if any(keyword in instruction_lower for keyword in ['python', 'パイソン']):
            return 'python'
        elif any(keyword in instruction_lower for keyword in ['javascript', 'js', 'ジャバスクリプト']):
            return 'javascript'
        elif any(keyword in instruction_lower for keyword in ['html', 'ウェブ']):
            return 'html'
        elif any(keyword in instruction_lower for keyword in ['css', 'スタイル']):
            return 'css'
        else:
            return 'python'  # デフォルト
    
    def _generate_code(self, instruction, language):
        """コードを生成"""
        if language == 'python':
            return self._generate_python_code(instruction)
        elif language == 'javascript':
            return self._generate_js_code(instruction)
        elif language == 'html':
            return self._generate_html_code(instruction)
        elif language == 'css':
            return self._generate_css_code(instruction)
        else:
            return None
    
    def _generate_python_code(self, instruction):
        """Pythonコードを生成"""
        if '電卓' in instruction or '計算機' in instruction:
            return '''
def calculator():
    """簡単な電卓"""
    print("=== 簡単な電卓 ===")
    
    while True:
        try:
            num1 = float(input("最初の数字を入力: "))
            op = input("演算子 (+, -, *, /): ")
            num2 = float(input("次の数字を入力: "))
            
            if op == '+':
                result = num1 + num2
            elif op == '-':
                result = num1 - num2
            elif op == '*':
                result = num1 * num2
            elif op == '/':
                if num2 != 0:
                    result = num1 / num2
                else:
                    print("エラー: 0で割ることはできません")
                    continue
            else:
                print("無効な演算子です")
                continue
            
            print(f"結果: {num1} {op} {num2} = {result}")
            
        except ValueError:
            print("エラー: 有効な数字を入力してください")
        except Exception as e:
            print(f"エラー: {e}")
        
        another = input("続けますか？ (y/n): ")
        if another.lower() != 'y':
            break

if __name__ == "__main__":
    calculator()
'''
        else:
            return f'''
# {instruction}
def main():
    """生成されたアプリケーション"""
    print("{instruction}を実行します")
    
    # ここにアプリケーションロジックを実装
    pass

if __name__ == "__main__":
    main()
'''
    
    def _generate_js_code(self, instruction):
        """JavaScriptコードを生成"""
        return f'''
// {instruction}
function main() {{
    console.log("{instruction}を実行します");
    
    // ここにアプリケーションロジックを実装
}}

main();
'''
    
    def _generate_html_code(self, instruction):
        """HTMLコードを生成"""
        return f'''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{instruction}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{instruction}</h1>
        <p>ここにコンテンツを実装します</p>
    </div>
</body>
</html>
'''
    
    def _generate_css_code(self, instruction):
        """CSSコードを生成"""
        return f'''
/* {instruction} */
.container {{
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}

.header {{
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
    color: #333;
}}

.content {{
    line-height: 1.6;
    color: #666;
}}
'''
    
    def _save_code_file(self, code, filename, language):
        """コードをファイルに保存"""
        try:
            # generated_appsディレクトリを作成
            GENERATED_APPS_DIR.mkdir(exist_ok=True)
            
            # ファイル名を生成
            extension = self.supported_languages[language]['extension']
            file_path = GENERATED_APPS_DIR / f"{filename}{extension}"
            
            # ファイルに保存
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return str(file_path)
        
        except Exception as e:
            print(f"ファイル保存エラー: {e}")
            return None
    
    def create_file_from_instruction(self, instruction, filename):
        """指示からファイルを作成"""
        return self.generate_code_from_instruction(instruction, filename)

def scan_generated_apps():
    """generated_appsフォルダ内のPythonファイルをスキャン"""
    try:
        apps = []
        if not GENERATED_APPS_DIR.exists():
            return apps
        
        for py_file in GENERATED_APPS_DIR.glob("*.py"):
            try:
                # ファイルのメタデータを取得
                file_stat = py_file.stat()
                app_info = {
                    'name': py_file.stem,
                    'path': str(py_file),
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime,
                    'description': '',
                    'functions': []
                }
                
                # ファイル内容をスキャンして関数を取得
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 関数抽出
                functions = re.findall(r'def\s+(\w+)\s*\(', content)
                app_info['functions'] = functions[:5]
                
                # ファイルの先頭コメントを説明として取得
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('#') and not line.strip().startswith('#!'):
                        app_info['description'] = line.strip('#').strip()
                        break
                
                apps.append(app_info)
                
            except Exception as e:
                print(f"アプリスキャンエラー {py_file}: {e}")
                continue
        
        return sorted(apps, key=lambda x: x['modified'], reverse=True)
    
    except Exception as e:
        print(f"アプリスキャン全体エラー: {e}")
        return []

def execute_app_inline(app_path, app_name):
    """アプリをインラインで実行"""
    try:
        # アプリファイルを動的にインポート
        spec = importlib.util.spec_from_file_location(app_name, app_path)
        app_module = importlib.util.module_from_spec(spec)
        
        # グローバル変数をクリーンにするための準備
        original_globals = {}
        
        try:
            # Streamlitのグローバル変数を一時保存
            for key in ['st', 'streamlit']:
                if key in globals():
                    original_globals[key] = globals()[key]
            
            # アプリモジュールを実行
            spec.loader.exec_module(app_module)
            
            # main関数があれば実行
            if hasattr(app_module, 'main'):
                return app_module.main()
            
            return f"✅ {app_name} を読み込みました"
            
        except Exception as app_error:
            return f"❌ アプリ実行エラー: {str(app_error)}"
        finally:
            # グローバル変数を復元
            for key, value in original_globals.items():
                globals()[key] = value
                
    except Exception as e:
        return f"❌ アプリ読み込みエラー: {str(e)}"

def self_repair_app(app_path, app_name, error_message):
    """アプリの自己修復機能"""
    try:
        # コードを読み込み
        with open(app_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        repaired_code = original_code
        repair_log = []
        
        # NameError修正
        if 'NameError' in error_message:
            match = re.search(r'NameError: name \'(\w+)\' is not defined', error_message)
            if match:
                var_name = match.group(1)
                init_line = f"{var_name} = 0  # 修復：未定義変数を初期化\n"
                repaired_code = init_line + repaired_code
                repair_log.append(f"未定義変数 '{var_name}' を初期化")
        
        # ZeroDivisionError修正
        elif 'ZeroDivisionError' in error_message:
            repaired_code = re.sub(r'(/|//|%)\s*(\w+)', r'\1 (0 if \2 == 0 else \2)', repaired_code)
            repair_log.append("ゼロ除算エラーを防止")
        
        # 修復されたコードを保存
        if repaired_code != original_code:
            # バックアップを作成
            backup_path = app_path.replace('.py', '_backup.py')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(repaired_code)
            
            return True, repair_log
        
        return False, ["修復不要"]
        
    except Exception as e:
        return False, [f"修復エラー: {str(e)}"]
