#!/usr/bin/env python3
"""
最終修正スクリプト
構文エラーを完全に修正
"""

def final_syntax_fix():
    """構文エラーを完全に修正"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 問題の箇所を特定して修正
        # 678行目: else:  # 自動応答
        # 679行目: if input_method == "🤖 自動応答":
        
        # 678行目のelse文を修正
        lines = content.split('\n')
        
        # 678行目のelse文を修正
        for i, line in enumerate(lines):
            line_num = i + 1
            
            if line_num == 678 and line.strip() == "else:  # 自動応答":
                # 正しいインデントでelse文を修正
                lines[i] = "        else:  # 自動応答"
                print(f"✅ 修正: 行{line_num} - else文のインデントを修正")
                break
        
        # 679行目以降のインデントを調整
        for i in range(678, len(lines)):
            line_num = i + 1
            
            if line_num > 678 and lines[i].strip():  # 空行でなければ
                # インデントを調整
                original_spaces = len(lines[i]) - len(lines[i].lstrip(' '))
                
                # 679行目: 16スペース → 12スペース
                if line_num == 679:
                    lines[i] = ' ' * 12 + lines[i].lstrip()
                    print(f"✅ 調整: 行{line_num} - インデントを12スペースに修正")
                
                # 680行目以降: 20スペース → 16スペース
                elif line_num >= 680:
                    lines[i] = ' ' * 16 + lines[i].lstrip()
                    if line_num <= 685:  # 最初の数行だけ表示
                        print(f"✅ 調整: 行{line_num} - インデントを16スペースに修正")
        
        # 修正された内容を書き込み
        fixed_content = '\n'.join(lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ {file_path} の最終修正が完了しました")
        
        # 構文チェック
        try:
            compile(fixed_content, file_path, 'exec')
            print("✅ 最終修正後のPython構文チェックに合格しました")
            return True
        except SyntaxError as e:
            print(f"❌ 最終修正後の構文エラー: {e}")
            print(f"   行: {e.lineno}, 位置: {e.offset}")
            if e.text:
                print(f"   問題行: {repr(e.text)}")
            return False
        
    except Exception as e:
        print(f"❌ 最終修正中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 最終構文修正を開始します...")
    
    # 修正を実行
    success = final_syntax_fix()
    
    if success:
        print("\n🎉 最終構文修正が完了しました！")
    else:
        print("\n❌ 最終構文修正に失敗しました")
