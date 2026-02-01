#!/usr/bin/env python3
"""
最終構文修正スクリプト
if-else-elif構造の問題を完全に修正
"""

def fix_final_syntax():
    """if-else-elif構造の問題を完全に修正"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 問題の箇所を特定して修正
        # 625行目: if input_method == "🎙️ 音声入力":
        # 657行目: else:  # テキスト入力
        # 678行目: elif input_method == "🤖 自動応答":
        
        # 678行目のelifをelseに変更して、その中でif文にする
        content = content.replace(
            '        elif input_method == "🤖 自動応答":',
            '        else:\n            if input_method == "🤖 自動応答":'
        )
        
        # 修正された内容を書き込み
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_path} のif-else-elif構造を修正しました")
        
        # 構文チェック
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                test_content = f.read()
            compile(test_content, file_path, 'exec')
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

def show_structure_around_lines():
    """問題行周辺の構造を表示"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("🔍 問題行周辺の構造:")
        
        # 625行目周辺
        print("\n--- 625行目周辺（音声入力） ---")
        for i in range(623, min(628, len(lines))):
            line_num = i + 1
            line = lines[i].rstrip()
            space_count = len(line) - len(line.lstrip(' '))
            marker = "→" if line_num in [625, 657, 678] else " "
            print(f"{marker} 行{line_num:3d}: {space_count:2d}スペース | {repr(line)}")
        
        # 657行目周辺
        print("\n--- 657行目周辺（テキスト入力） ---")
        for i in range(655, min(660, len(lines))):
            line_num = i + 1
            line = lines[i].rstrip()
            space_count = len(line) - len(line.lstrip(' '))
            marker = "→" if line_num in [625, 657, 678] else " "
            print(f"{marker} 行{line_num:3d}: {space_count:2d}スペース | {repr(line)}")
        
        # 678行目周辺
        print("\n--- 678行目周辺（自動応答） ---")
        for i in range(676, min(681, len(lines))):
            line_num = i + 1
            line = lines[i].rstrip()
            space_count = len(line) - len(line.lstrip(' '))
            marker = "→" if line_num in [625, 657, 678] else " "
            print(f"{marker} 行{line_num:3d}: {space_count:2d}スペース | {repr(line)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 表示中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 最終構文修正を開始します...")
    
    # 修正前の構造を確認
    print("\n" + "="*60)
    show_structure_around_lines()
    print("="*60 + "\n")
    
    # 修正を実行
    success = fix_final_syntax()
    
    if success:
        print("\n🎉 最終構文修正が完了しました！")
        
        # 修正後の構造を確認
        print("\n" + "="*60)
        show_structure_around_lines()
        print("="*60 + "\n")
    else:
        print("\n❌ 最終構文修正に失敗しました")
