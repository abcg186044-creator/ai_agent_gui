#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI電卓アプリ作成リクエストテスト
"""

from timeout_responder import TimeoutResponder
import time

def main():
    responder = TimeoutResponder()

    # GUI電卓アプリ作成リクエスト
    prompt = 'PythonでGUIをクリックして操作できる電卓アプリを作成してください。Tkinterを使用して、基本的な四則演算ができる完全なコードを生成してください。'
    task_description = 'Python GUI電卓アプリ開発'

    print('🚀 GUI電卓アプリ作成リクエスト開始')
    print('=' * 60)

    result = responder.generate_response_with_progress(prompt, task_description)

    if result['success']:
        print(f'✅ 成功: タスクID {result["task_id"]}')
        print(f'📊 進捗報告数: {len(result["progress_reports"])}')
        print(f'💬 中間レスポンス数: {len(result["intermediate_responses"])}')
        print(f'🤖 AI応答長: {len(result["response"])}文字')
        print('\n🔧 生成されたコード:')
        print('-' * 40)
        print(result['response'])
        
        # 生成されたコードをファイルに保存
        with open('calculator_app.py', 'w', encoding='utf-8') as f:
            f.write(result['response'])
        print('\n💾 コードを calculator_app.py に保存しました')
        
    else:
        print(f'❌ 失敗: {result["error"]}')

if __name__ == "__main__":
    main()
