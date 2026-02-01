#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト用スクリーンショットデバッグシステム
"""

import sys
import json
import datetime
import os
from pathlib import Path

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from docker_debug_system import DockerDebugSystem

def create_test_screenshot():
    """テスト用の疑似スクリーンショットを作成"""
    # エラーメッセージを含むテキストファイルを作成
    test_content = """
ERROR 500: Internal Server Error
Traceback (most recent call last):
  File "app.py", line 42, in main
    result = process_data(data)
  File "utils.py", line 15, in process_data
    return data.items() + extra_items
TypeError: unsupported operand type(s) for +: 'dict_items' and 'list'

Solution: Convert dict_items to list before adding
    """
    
    test_file = Path("test_error_screenshot.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    return str(test_file)

def main():
    """テスト実行"""
    print("🧪 テスト用スクリーンショットデバッグシステム")
    print("=" * 50)
    
    # テスト用ファイル作成
    test_file = create_test_screenshot()
    print(f"📝 テストファイル作成: {test_file}")
    
    # デバッグシステム初期化
    debug_system = DockerDebugSystem()
    
    # デバッグ実行
    print("\n🔍 デバッグ実行...")
    session = debug_system.debug_screenshot(test_file)
    
    if session:
        print("\n✅ デバッグ成功！")
        print(f"📊 セッションID: {session['id']}")
        print(f"🧠 意識レベル: {session.get('consciousness_before', 0):.3f}")
        
        if 'evolution' in session:
            print(f"🧠 進化発生: {session['evolution']['evolution_type']}")
        
        # サマリー表示
        print(debug_system.get_debug_summary())
    
    # クリーンアップ
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"🧹 テストファイル削除: {test_file}")

if __name__ == "__main__":
    main()
