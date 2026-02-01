#!/usr/bin/env python3
"""
改行コード修正スクリプト
Windows (CRLF) → Unix (LF) に変換
"""

import os
import sys
import glob

def fix_line_endings(file_path):
    """ファイルの改行コードをCRLFからLFに変換"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # CRLFをLFに変換
        content = content.replace(b'\r\n', b'\n')
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        print(f"✅ 修正完了: {file_path}")
        return True
    except Exception as e:
        print(f"❌ 修正失敗: {file_path} - {e}")
        return False

def main():
    """メイン処理"""
    print("🔧 改行コード修正スクリプト")
    print("========================")
    
    # 対象ファイルのリスト
    target_files = [
        'scripts/ollama_entrypoint.sh',
        'scripts/start_optimized.sh',
        'scripts/setup_vrm.sh',
        'scripts/preload_models.py',
        'scripts/preload_models_persistent.py',
        'scripts/setup_ollama_models.py'
    ]
    
    # ワイルドカードで検索
    shell_files = glob.glob('scripts/*.sh')
    python_files = glob.glob('scripts/*.py')
    
    all_files = list(set(target_files + shell_files + python_files))
    
    print(f"📁 対象ファイル数: {len(all_files)}")
    print()
    
    success_count = 0
    total_count = len(all_files)
    
    for file_path in all_files:
        if os.path.exists(file_path):
            if fix_line_endings(file_path):
                success_count += 1
        else:
            print(f"⚠️ ファイルが存在しません: {file_path}")
    
    print()
    print(f"📊 修正結果: {success_count}/{total_count} ファイル")
    
    if success_count == total_count:
        print("🎉 すべてのファイルの改行コードを修正しました")
        return 0
    else:
        print("⚠️ 一部のファイルでエラーが発生しました")
        return 1

if __name__ == "__main__":
    exit(main())
