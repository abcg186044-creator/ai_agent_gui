#!/usr/bin/env python3
"""
構造再構築スクリプト
if-else-elif構造を完全に再構築
"""

def rebuild_structure():
    """if-else-elif構造を完全に再構築"""
    
    file_path = "ollama_vrm_integrated_app.py"
    
    try:
        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 新しい構造を構築
        new_lines = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # 625行目まで: そのまま
            if line_num <= 625:
                new_lines.append(line)
            
            # 626-656行目: 音声入力の処理
            elif 626 <= line_num <= 656:
                new_lines.append(line)
            
            # 657行目: else文
            elif line_num == 657:
                new_lines.append(line)
            
            # 658-677行目: テキスト入力の処理
            elif 658 <= line_num <= 677:
                new_lines.append(line)
            
            # 678行目: elifを削除してelseに
            elif line_num == 678:
                # 元の行を削除して新しいelse文を追加
                new_lines.append("        else:  # 自動応答\n")
                print(f"✅ 再構築: 行{line_num} - elif → else")
            
            # 679行目以降: 自動応答の処理
            elif line_num >= 679:
                if line.strip():  # 空行でなければ
                    # インデントを調整
                    original_content = line.lstrip()
                    
                    # 679行目: if input_method == "🤖 自動応答":
                    if line_num == 679 and 'input_method == "🤖 自動応答"' in original_content:
                        new_lines.append("            if input_method == \"🤖 自動応答\":\n")
                        print(f"✅ 再構築: 行{line_num} - if文のインデントを修正")
                    
                    # 680行目以降: 16スペースのインデント
                    elif line_num >= 680:
                        new_lines.append("                " + original_content + "\n")
                        if line_num <= 685:  # 最初の数行だけ表示
                            print(f"✅ 再構築: 行{line_num} - インデントを16スペースに修正")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
        
        # 修正された内容を書き込み
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ {file_path} の構造再構築が完了しました")
        
        # 構文チェック
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                test_content = f.read()
            compile(test_content, file_path, 'exec')
            print("✅ 再構築後のPython構文チェックに合格しました")
            return True
        except SyntaxError as e:
            print(f"❌ 再構築後の構文エラー: {e}")
            print(f"   行: {e.lineno}, 位置: {e.offset}")
            if e.text:
                print(f"   問題行: {repr(e.text)}")
            return False
        
    except Exception as e:
        print(f"❌ 再構築中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 構造再構築を開始します...")
    
    # 再構築を実行
    success = rebuild_structure()
    
    if success:
        print("\n🎉 構造再構築が完了しました！")
    else:
        print("\n❌ 構造再構築に失敗しました")
