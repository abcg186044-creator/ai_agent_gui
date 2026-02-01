#!/usr/bin/env python3
"""
完全な構文修正スクリプト
ollama_vrm_integrated_app.pyの構文エラーを完全に修正
"""

def fix_complete_syntax():
    """構文エラーを完全に修正"""
    
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
            
            # 657行目: else文の前のif文を確認
            if line_num == 657 and line.strip() == "else:  # テキスト入力":
                # このelse文が正しい位置にあるか確認
                # 前のif文が656行目で終わっているはず
                fixed_lines.append(line)
            
            # 678行目: elif文の問題を修正
            elif line_num == 678 and line.strip().startswith('elif input_method == "🤖 自動応答":'):
                # elif文はif文と同じレベルにあるべき
                # 657行目のelseと同じレベル（8スペース）
                fixed_line = "        elif input_method == \"🤖 自動応答\":"
                fixed_lines.append(fixed_line)
                print(f"✅ 修正: 行{line_num} - elif文のインデントを修正")
            
            else:
                fixed_lines.append(line)
        
        # 修正された内容を書き込み
        fixed_content = '\n'.join(fixed_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ {file_path} の構文を修正しました")
        
        # 構文チェック
        try:
            compile(fixed_content, file_path, 'exec')
            print("✅ Python構文チェックに合格しました")
            return True
        except SyntaxError as e:
            print(f"❌ 構文エラー: {e}")
            print(f"   行: {e.lineno}, 位置: {e.offset}")
            if e.text:
                print(f"   問題行: {repr(e.text)}")
            return False
        
    except Exception as e:
        print(f"❌ 修正中にエラーが発生: {str(e)}")
        return False

def analyze_if_else_structure():
    """if-else-elif構造を分析"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("🔍 if-else-elif構造の分析:")
        
        for i, line in enumerate(lines):
            line_num = i + 1
            line_stripped = line.strip()
            
            # if-else-elif文を検出
            if line_stripped.startswith(('if ', 'else:', 'elif ')):
                space_count = len(line) - len(line.lstrip(' '))
                print(f"行{line_num:3d}: {space_count:2d}スペース | {line_stripped}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 完全な構文修正を開始します...")
    
    # 構造を分析
    print("\n" + "="*60)
    analyze_if_else_structure()
    print("="*60 + "\n")
    
    # 修正を実行
    success = fix_complete_syntax()
    
    if success:
        print("\n🎉 構文修正が完了しました！")
        
        # 修正後の構造を確認
        print("\n" + "="*60)
        analyze_if_else_structure()
        print("="*60 + "\n")
    else:
        print("\n❌ 構文修正に失敗しました")
