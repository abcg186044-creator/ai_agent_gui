#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高頻度タイムアウト防止システムテスト
"""

from timeout_responder import TimeoutResponder
import time

def main():
    responder = TimeoutResponder()

    # 長時間タスクで高頻度報告をテスト
    prompt = '機械学習モデルの構築からデプロイまでの完全なパイプラインを詳細に説明してください。Pythonコード例と共に、データ前処理、モデル訓練、評価、本番環境へのデプロイ手順を含めてください。'
    task_description = '機械学習モデル開発パイプライン'

    print('🚀 高頻度タイムアウト防止システムテスト開始')
    print('=' * 60)
    print('📈 進捗報告間隔: 3秒（高頻度モード）')
    print('🌐 Web更新間隔: 2秒')
    print('=' * 60)

    result = responder.generate_response_with_progress(prompt, task_description)

    if result['success']:
        print(f'✅ 成功: タスクID {result["task_id"]}')
        print(f'📊 進捗報告数: {len(result["progress_reports"])}')
        print(f'💬 中間レスポンス数: {len(result["intermediate_responses"])}')
        print(f'🤖 AI応答長: {len(result["response"])}文字')
        
        # 進捗報告の詳細を表示
        print('\n📋 詳細な進捗報告:')
        print('-' * 40)
        for i, report in enumerate(result['progress_reports'], 1):
            print(f'{i}. {report["progress_percent"]}% - {report["status"]}')
        
        print('\n💬 中間レスポンス例:')
        print('-' * 40)
        for i, response in enumerate(result['intermediate_responses'][:3], 1):
            print(f'{i}. {response["message"][:100]}...')
        
    else:
        print(f'❌ 失敗: {result["error"]}')

if __name__ == "__main__":
    main()
