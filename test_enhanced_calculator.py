#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強化版システムで電卓アプリ作成テスト
"""

from enhanced_timeout_responder import EnhancedTimeoutResponder
import time

def main():
    responder = EnhancedTimeoutResponder()

    # 電卓アプリ作成リクエスト
    prompt = 'PythonでGUIをクリックして操作できる電卓アプリを作成してください。Tkinterを使用して、基本的な四則演算ができる完全なコードを生成してください。'
    task_description = 'Python GUI電卓アプリ開発'

    print('🚀 強化版システムで電卓アプリ作成開始')
    print('=' * 60)

    result = responder.generate_response_with_split(prompt, task_description)

    if result['success']:
        print(f'✅ 分割処理開始: タスクID {result["task_id"]}')
        print(f'📋 サブタスク数: {result["subtasks"]}')
        print(f'💬 メッセージ: {result["message"]}')
        
        # 進捗を監視
        print('\n📊 進捗監視中...')
        for i in range(30):  # 最大90秒監視
            time.sleep(3)
            
            # 最新のレスポンスを確認
            if not responder.response_queue.empty():
                latest = list(responder.response_queue.queue)[-1]
                if latest.get('task_id') == result['task_id']:
                    print(f'📈 進捗: {latest.get("status", "不明")}')
                    
                    # 完了したか確認
                    if '完了' in latest.get('status', ''):
                        print('\n✅ タスク完了！')
                        if 'results' in latest:
                            print(f'📋 処理結果数: {len(latest["results"])}')
                        
                        # 結果を保存
                        with open('enhanced_calculator_result.txt', 'w', encoding='utf-8') as f:
                            f.write(f'タスクID: {result["task_id"]}\n')
                            f.write(f'サブタスク数: {result["subtasks"]}\n')
                            f.write(f'完了時刻: {time.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                            f.write('結果:\n')
                            f.write(str(latest))
                        
                        print('💾 結果を enhanced_calculator_result.txt に保存しました')
                        break
        
        print('\n🌐 Webインターフェース: http://127.0.0.1:8085')
        print('📊 リアルタイムで進捗を監視できます')
        
    else:
        print(f'❌ 失敗: {result.get("error", "不明なエラー")}')

if __name__ == "__main__":
    main()
