#!/usr/bin/env python3
"""
構造デバッグスクリプト
if-else-elif構造の問題を詳細に分析
"""

def debug_structure():
    """if-else-elif構造を詳細に分析"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("🔍 if-else-elif構造の詳細分析:")
        print("="*60)
        
        # input_methodに関するif-else-elifを検出
        input_method_blocks = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            line_stripped = line.strip()
            
            # input_methodに関する条件文を検出
            if 'input_method' in line_stripped and line_stripped.startswith(('if ', 'else:', 'elif ')):
                space_count = len(line) - len(line.lstrip(' '))
                input_method_blocks.append({
                    'line_num': line_num,
                    'spaces': space_count,
                    'content': line_stripped,
                    'raw_line': line.rstrip()
                })
        
        # ブロックを表示
        for block in input_method_blocks:
            print(f"行{block['line_num']:3d}: {block['spaces']:2d}スペース | {block['content']}")
        
        print("="*60)
        
        # 構造の問題を分析
        print("🔧 構造の問題分析:")
        
        if len(input_method_blocks) >= 3:
            # 最初のif文
            first_if = input_method_blocks[0]
            print(f"✅ 最初のif文: 行{first_if['line_num']} ({first_if['spaces']}スペース)")
            
            # 2番目の文
            second = input_method_blocks[1]
            print(f"✅ 2番目の文: 行{second['line_num']} ({second['spaces']}スペース) - {second['content']}")
            
            # 3番目の文
            third = input_method_blocks[2]
            print(f"✅ 3番目の文: 行{third['line_num']} ({third['spaces']}スペース) - {third['content']}")
            
            # 問題を特定
            if third['content'].startswith('elif'):
                print("❌ 問題: elif文はelse文の後に来ることはできません")
                print("🔧 解決策: elifをelseに変更し、その中でif文を使用")
                
                # 修正案を提示
                print("\n🛠️ 修正案:")
                print(f"行{third['line_num']}: {third['raw_line']}")
                print("↓")
                print(f"行{third['line_num']}: {' ' * third['spaces']}else:")
                print(f"行{third['line_num']+1}: {' ' * (third['spaces'] + 4)}if {third['content'][5:]}")
                
                return True
        
        print("❌ 構造の問題を特定できませんでした")
        return False
        
    except Exception as e:
        print(f"❌ 分析中にエラーが発生: {str(e)}")
        return False

def apply_fix():
    """修正を適用"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 678行目のelifをelseに変更
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            if line_num == 678 and 'elif input_method == "🤖 自動応答":' in line:
                # elifをelseに変更
                spaces = len(line) - len(line.lstrip(' '))
                lines[i] = ' ' * spaces + 'else:  # 自動応答'
                print(f"✅ 修正: 行{line_num} - elif → else")
                break
        
        # 679行目以降のインデントを調整
        for i in range(678, len(lines)):
            line_num = i + 1
            if line_num > 678 and lines[i].strip():  # 空行でなければ
                original_spaces = len(lines[i]) - len(lines[i].lstrip(' '))
                new_spaces = original_spaces + 4
                lines[i] = ' ' * new_spaces + lines[i].lstrip()
        
        # 修正された内容を書き込み
        fixed_content = '\n'.join(lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ {file_path} に修正を適用しました")
        
        # 構文チェック
        try:
            compile(fixed_content, file_path, 'exec')
            print("✅ 修正後のPython構文チェックに合格しました")
            return True
        except SyntaxError as e:
            print(f"❌ 修正後の構文エラー: {e}")
            print(f"   行: {e.lineno}, 位置: {e.offset}")
            if e.text:
                print(f"   問題行: {repr(e.text)}")
            return False
        
    except Exception as e:
        print(f"❌ 修正適用中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 構造デバッグを開始します...")
    
    # 構造を分析
    debug_structure()
    
    # 修正を適用
    print("\n" + "="*60)
    success = apply_fix()
    
    if success:
        print("\n🎉 構造修正が完了しました！")
    else:
        print("\n❌ 構造修正に失敗しました")
