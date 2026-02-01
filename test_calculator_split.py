#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分割版システムで電卓アプリ作成テスト
"""

from ollama_client import OllamaClient

def main():
    print("🚀 分割版Ollamaクライアントで電卓アプリ作成開始")
    print("=" * 60)
    
    client = OllamaClient(timeout=60)
    
    # 電卓アプリ作成リクエスト
    prompt = """PythonでGUIをクリックして操作できる電卓アプリを作成してください。
Tkinterを使用して、基本的な四則演算ができる完全なコードを生成してください。
以下の機能を含めてください：
1. 数字ボタン（0-9）
2. 演算子ボタン（+、-、*、/）
3. イコールボタン
4. クリアボタン
5. 小数点ボタン
6. 表示画面
7. エラー処理
8. キーボード入力対応
完全な実行可能なコードを生成してください。"""
    
    print(f"🔍 プロンプト長: {len(prompt)} 文字")
    print("🔍 Ollama API呼び出し開始...")
    
    response = client.generate_response(prompt)
    
    print("\n🔧 生成されたコード:")
    print("-" * 40)
    print(response)
    
    # ファイルに保存
    with open("split_calculator_app.py", "w", encoding="utf-8") as f:
        f.write(response)
    
    print("\n💾 コードを split_calculator_app.py に保存しました")
    
    if response and not response.startswith("AI応答がタイムアウトしました"):
        print("✅ 電卓アプリの生成に成功しました！")
        print("🚀 実行方法: python split_calculator_app.py")
    else:
        print("❌ 電卓アプリの生成に失敗しました")

if __name__ == "__main__":
    main()
