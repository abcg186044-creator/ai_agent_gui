#!/usr/bin/env python3
"""
手動構文修正スクリプト
if-else-elif構造を手動で修正
"""

def manual_fix():
    """手動でif-else-elif構造を修正"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 問題の行を特定して修正
        fixed_lines = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # 625行目: if input_method == "🎙️ 音声入力":
            if line_num == 625:
                fixed_lines.append(line)
                print(f"✅ 保持: 行{line_num} - {line.strip()}")
            
            # 657行目: else:  # テキスト入力
            elif line_num == 657:
                fixed_lines.append(line)
                print(f"✅ 保持: 行{line_num} - {line.strip()}")
            
            # 678行目: elif input_method == "🤖 自動応答":
            elif line_num == 678:
                # このelifをelseに変更
                original_line = line.strip()
                fixed_line = "        else:  # 自動応答\n"
                fixed_lines.append(fixed_line)
                print(f"✅ 修正: 行{line_num} - {original_line} → {fixed_line.strip()}")
            
            # 679行目以降: インデントを調整
            elif line_num >= 679:
                # インデントを4スペース増やす
                if line.strip():  # 空行でなければ
                    original_spaces = len(line) - len(line.lstrip(' '))
                    new_spaces = original_spaces + 4
                    new_line = ' ' * new_spaces + line.lstrip()
                    fixed_lines.append(new_line)
                    if line_num <= 685:  # 最初の数行だけ表示
                        print(f"✅ 調整: 行{line_num} - インデントを+4スペース")
                else:
                    fixed_lines.append(line)
            
            else:
                fixed_lines.append(line)
        
        # 修正された内容を書き込み
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"✅ {file_path} の手動修正が完了しました")
        
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

if __name__ == "__main__":
    print("🔧 手動構文修正を開始します...")
    
    # 修正を実行
    success = manual_fix()
    
    if success:
        print("\n🎉 手動構文修正が完了しました！")
    else:
        print("\n❌ 手動構文修正に失敗しました")
