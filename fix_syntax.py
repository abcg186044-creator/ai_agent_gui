#!/usr/bin/env python3
"""
SyntaxError修正スクリプト
ollama_vrm_integrated_app.pyのインデント問題を修正
"""

import re

def fix_syntax_error():
    """インデントと構文エラーを修正"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 問題箇所を特定して修正
        # 678行目あたりのelif文のインデント問題を修正
        lines = content.split('\n')
        
        fixed_lines = []
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # 678行目付近のelif文のインデントを修正
            if line_num == 678 and line.strip().startswith('elif input_method == "🤖 自動応答":'):
                # 正しいインデントに修正（8スペース）
                fixed_line = "        elif input_method == \"🤖 自動応答\":"
                fixed_lines.append(fixed_line)
                print(f"✅ 修正: 行{line_num} - {line.strip()} → {fixed_line.strip()}")
            else:
                fixed_lines.append(line)
        
        # 修正された内容を書き込み
        fixed_content = '\n'.join(fixed_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ {file_path} の構文エラーを修正しました")
        
        return True
        
    except Exception as e:
        print(f"❌ 修正中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 SyntaxError修正を開始します...")
    success = fix_syntax_error()
    
    if success:
        print("🎉 構文エラーの修正が完了しました！")
    else:
        print("❌ 構文エラーの修正に失敗しました")
