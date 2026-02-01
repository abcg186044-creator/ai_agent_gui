#!/usr/bin/env python3
"""
動作バージョン作成スクリプト
構文エラーを完全に修正した動作バージョンを作成
"""

def create_working_version():
    """構文エラーを完全に修正した動作バージョンを作成"""
    
    original_file = "ollama_vrm_integrated_app.py"
    working_file = "ollama_vrm_working.py"
    
    try:
        # 元のファイルを読み込み
        with open(original_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 新しいファイルを作成
        with open(working_file, 'w', encoding='utf-8') as f:
            for i, line in enumerate(lines):
                line_num = i + 1
                
                # 625行目まで: そのままコピー
                if line_num <= 625:
                    f.write(line)
                
                # 626-656行目: 音声入力の処理
                elif 626 <= line_num <= 656:
                    f.write(line)
                
                # 657行目: else文
                elif line_num == 657:
                    f.write(line)
                
                # 658-677行目: テキスト入力の処理
                elif 658 <= line_num <= 677:
                    f.write(line)
                
                # 678行目: elifをelseに変更
                elif line_num == 678:
                    f.write("        else:  # 自動応答\n")
                    print(f"✅ 作成: 行{line_num} - elif → else")
                
                # 679行目以降: 自動応答の処理
                elif line_num >= 679:
                    if line.strip():  # 空行でなければ
                        original_content = line.lstrip()
                        
                        # 679行目: if input_method == "🤖 自動応答":
                        if line_num == 679 and 'input_method == "🤖 自動応答"' in original_content:
                            f.write("            if input_method == \"🤖 自動応答\":\n")
                            print(f"✅ 作成: 行{line_num} - if文のインデントを修正")
                        
                        # 680行目以降: 16スペースのインデント
                        elif line_num >= 680:
                            f.write("                " + original_content + "\n")
                            if line_num <= 685:  # 最初の数行だけ表示
                                print(f"✅ 作成: 行{line_num} - インデントを16スペースに修正")
                    else:
                        f.write(line)
        
        print(f"✅ 動作バージョンを作成しました: {working_file}")
        
        # 構文チェック
        try:
            with open(working_file, 'r', encoding='utf-8') as f:
                test_content = f.read()
            compile(test_content, working_file, 'exec')
            print("✅ 動作バージョンのPython構文チェックに合格しました")
            return True
        except SyntaxError as e:
            print(f"❌ 動作バージョンの構文エラー: {e}")
            print(f"   行: {e.lineno}, 位置: {e.offset}")
            if e.text:
                print(f"   問題行: {repr(e.text)}")
            return False
        
    except Exception as e:
        print(f"❌ 動作バージョン作成中にエラーが発生: {str(e)}")
        return False

def replace_with_working():
    """元のファイルを作業バージョンで置換"""
    
    working_file = "ollama_vrm_working.py"
    original_file = "ollama_vrm_integrated_app.py"
    
    try:
        # 作業バージョンを読み込み
        with open(working_file, 'r', encoding='utf-8') as f:
            working_content = f.read()
        
        # 元のファイルに書き込み
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(working_content)
        
        print(f"✅ 元のファイルを作業バージョンで置換しました: {original_file}")
        
        # 構文チェック
        try:
            compile(working_content, original_file, 'exec')
            print("✅ 置換後のPython構文チェックに合格しました")
            return True
        except SyntaxError as e:
            print(f"❌ 置換後の構文エラー: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 置換中にエラーが発生: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 動作バージョン作成を開始します...")
    
    # 作業バージョンを作成
    success1 = create_working_version()
    
    if success1:
        print("\n🎉 作業バージョンの作成が完了しました！")
        
        # 元のファイルを置換
        success2 = replace_with_working()
        
        if success2:
            print("\n🎉 元のファイルの置換が完了しました！")
            print("✅ 構文エラーが完全に修正されました！")
        else:
            print("\n❌ 元のファイルの置換に失敗しました")
    else:
        print("\n❌ 作業バージョンの作成に失敗しました")
