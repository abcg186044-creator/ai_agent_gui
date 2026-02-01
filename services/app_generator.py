"""
アプリジェネレーターモジュール
外部ファイルの生成・インポート・実行管理を担当
"""

import os
import re
import importlib.util
from pathlib import Path
from ..core.constants import *

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
