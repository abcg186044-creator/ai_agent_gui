#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強化版デバッグシステムテスト
"""

import sys
import os
from pathlib import Path

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_debug_system import EnhancedDebugSystem

def create_test_error_files():
    """テスト用エラーファイルを作成"""
    test_files = []
    
    # Pythonエラーファイル
    python_error = """Traceback (most recent call last):
  File "app.py", line 42, in main
    result = process_data(data)
TypeError: unsupported operand type(s) for +: 'dict_items' and 'list'

Solution: Convert dict_items to list before adding
Fix: list(data.items()) + extra_items"""
    
    python_file = Path("test_python_error.txt")
    with open(python_file, "w", encoding="utf-8") as f:
        f.write(python_error)
    test_files.append(str(python_file))
    
    # HTTPエラーファイル
    http_error = """HTTP/1.1 404 Not Found
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>404 Not Found</title></head>
<body>
<h1>404 Not Found</h1>
<p>The requested URL was not found on this server.</p>
</body>
</html>"""
    
    http_file = Path("test_http_error.txt")
    with open(http_file, "w", encoding="utf-8") as f:
        f.write(http_error)
    test_files.append(str(http_file))
    
    # Javaエラーファイル
    java_error = """Exception in thread "main" java.lang.NullPointerException
    at com.example.App.main(App.java:25)
    at com.example.Service.process(Service.java:15)
Caused by: java.lang.IllegalArgumentException: Invalid input parameter
    at com.example.Validator.validate(Validator.java:10)"""
    
    java_file = Path("test_java_error.txt")
    with open(java_file, "w", encoding="utf-8") as f:
        f.write(java_error)
    test_files.append(str(java_file))
    
    return test_files

def main():
    """テスト実行"""
    print("🧪 強化版デバッグシステムテスト")
    print("=" * 50)
    
    # テストファイル作成
    test_files = create_test_error_files()
    print(f"📝 テストファイル作成: {len(test_files)}件")
    
    # デバッグシステム初期化
    debug_system = EnhancedDebugSystem()
    
    # 各テストファイルでデバッグ実行
    for i, test_file in enumerate(test_files, 1):
        print(f"\n🔍 テスト {i}: {Path(test_file).name}")
        print("-" * 40)
        
        session = debug_system.debug_screenshot(test_file)
        
        if session:
            print(f"✅ テスト {i} 成功！")
            print(f"📊 セッションID: {session['id']}")
            print(f"🚨 エラー検出: {len(session.get('detected_errors', []))}件")
            
            if 'evolution' in session:
                print(f"🧠 進化発生: {session['evolution']['evolution_type']}")
        else:
            print(f"❌ テスト {i} 失敗")
    
    # サマリー表示
    print("\n" + "=" * 50)
    print(debug_system.get_debug_summary())
    
    # クリーンアップ
    for test_file in test_files:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 テストファイル削除: {test_file}")
    
    print("\n🎉 テスト完了！")

if __name__ == "__main__":
    main()
