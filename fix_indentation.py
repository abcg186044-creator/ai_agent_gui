#!/usr/bin/env python3
"""
インデント修正スクリプト
ollama_vrm_integrated_app.pyのインデント問題を根本的に修正
"""

import re

def fix_indentation_issue():
    """インデントの問題を根本的に修正"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 行ごとに分割
        lines = content.split('\n')
        
        fixed_lines = []
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # 657行目: else文のインデントを確認
            if line_num == 657 and line.strip() == "else:  # テキスト入力":
                # 8スペースのインデントを確認
                if not line.startswith("        else:"):
                    fixed_line = "        else:  # テキスト入力"
                    fixed_lines.append(fixed_line)
                    print(f"✅ 修正: 行{line_num} - インデントを8スペースに修正")
                else:
                    fixed_lines.append(line)
            
            # 678行目: elif文のインデントを確認
            elif line_num == 678 and line.strip().startswith('elif input_method == "🤖 自動応答":'):
                # 8スペースのインデントを確認
                if not line.startswith("        elif"):
                    fixed_line = "        elif input_method == \"🤖 自動応答\":"
                    fixed_lines.append(fixed_line)
                    print(f"✅ 修正: 行{line_num} - インデントを8スペースに修正")
                else:
                    fixed_lines.append(line)
            
            # その他の行はそのまま
            else:
                fixed_lines.append(line)
        
        # 修正された内容を書き込み
        fixed_content = '\n'.join(fixed_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ {file_path} のインデント問題を修正しました")
        
        # 構文チェック
        try:
            compile(fixed_content, file_path, 'exec')
            print("✅ Python構文チェックに合格しました")
            return True
        except SyntaxError as e:
            print(f"❌ 構文エラーが残っています: {e}")
            print(f"   行: {e.lineno}, 位置: {e.offset}")
            print(f"   エラー: {e.text}")
            return False
        
    except Exception as e:
        print(f"❌ 修正中にエラーが発生: {str(e)}")
        return False

def check_indentation_around_line(target_line):
    """指定行の周辺のインデントを確認"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\n🔍 行{target_line}周辺のインデント確認:")
        start = max(0, target_line - 5)
        end = min(len(lines), target_line + 5)
        
        for i in range(start, end):
            line_num = i + 1
            line = lines[i].rstrip()
            
            # スペースの数をカウント
            space_count = len(line) - len(line.lstrip(' '))
            
            if line.strip():  # 空行でなければ表示
                marker = "→" if line_num == target_line else " "
                print(f"{marker} 行{line_num:3d}: {space_count:2d}スペース | {repr(line)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 確認中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 インデント問題の根本修正を開始します...")
    
    # まず現在の状態を確認
    print("\n" + "="*60)
    check_indentation_around_line(657)
    check_indentation_around_line(678)
    print("="*60 + "\n")
    
    # 修正を実行
    success = fix_indentation_issue()
    
    if success:
        print("\n🎉 インデント問題の修正が完了しました！")
        
        # 修正後の状態を確認
        print("\n" + "="*60)
        check_indentation_around_line(657)
        check_indentation_around_line(678)
        print("="*60 + "\n")
    else:
        print("\n❌ インデント問題の修正に失敗しました")
