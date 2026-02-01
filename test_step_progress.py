#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ステップ進行ごとの途中報告テスト
"""

from unlimited_agent_main import UnlimitedFriendAgent
import time

def test_step_progress():
    """ステップ進行ごとの途中報告テスト"""
    agent = UnlimitedFriendAgent()
    
    print("🧪 ステップ進行ごとの途中報告テスト")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        {
            "name": "静的知識ベーステスト",
            "prompt": "電卓アプリ",
            "task": "Python GUI電卓アプリ開発"
        },
        {
            "name": "テンプレート応答テスト",
            "prompt": "一般的なアプリ開発",
            "task": "汎用アプリケーション開発"
        },
        {
            "name": "ヒューリスティクス推論テスト",
            "prompt": "複雑なシステム設計",
            "task": "エンタープライズシステム設計"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 テスト {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 40)
        
        # 途中報告を記録
        progress_reports = []
        
        def progress_callback(progress_info):
            progress_reports.append(progress_info)
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] 📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
            
            if 'approach' in progress_info:
                print(f"           🔄 アプローチ: {progress_info['approach']}")
            
            if 'elapsed' in progress_info:
                print(f"           ⏱️ 経過時間: {progress_info['elapsed']:.1f}秒")
            
            if 'from_cache' in progress_info and progress_info['from_cache']:
                print(f"           📋 キャッシュ使用: {progress_info['from_cache']}")
            
            print("-" * 30)
        
        start_time = time.time()
        result = agent.generate_response_with_fallback(
            test_case['prompt'], 
            test_case['task'],
            progress_callback
        )
        elapsed = time.time() - start_time
        
        print(f"\n📊 テスト結果:")
        print(f"✅ 成功: {result['success']}")
        print(f"🔄 アプローチ: {result['approach']}")
        print(f"⏱️ 時間: {elapsed:.2f}秒")
        print(f"📊 途中報告数: {len(progress_reports)}件")
        
        # 途中報告の分析
        if progress_reports:
            steps = [r['step'] for r in progress_reports]
            progress_values = [r['progress'] for r in progress_reports]
            approaches_reported = set(r.get('approach', 'N/A') for r in progress_reports if 'approach' in r)
            
            print(f"📈 進捗範囲: {min(progress_values):.1f}% - {max(progress_values):.1f}%")
            print(f"🔄 報告されたアプローチ: {approaches_reported}")
            
            print(f"📋 実行されたステップ:")
            for i, step in enumerate(steps, 1):
                print(f"   {i}. {step}")
        
        print("\n" + "=" * 60)

def test_cache_step_progress():
    """キャッシュ時のステップ進行テスト"""
    agent = UnlimitedFriendAgent()
    
    print("📋 キャッシュ時のステップ進行テスト")
    print("=" * 60)
    
    # 同じリクエストを2回実行
    prompt = "PythonでGUIをクリックして操作できる電卓アプリを作成してください"
    task = "Python GUI電卓アプリ開発"
    
    progress_reports_first = []
    progress_reports_second = []
    
    def progress_callback_first(progress_info):
        progress_reports_first.append(progress_info)
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] 📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        print("-" * 30)
    
    def progress_callback_second(progress_info):
        progress_reports_second.append(progress_info)
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] 📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        print("-" * 30)
    
    print("🚀 1回目の実行:")
    print("-" * 40)
    start_time = time.time()
    result1 = agent.generate_response_with_fallback(prompt, task, progress_callback_first)
    elapsed1 = time.time() - start_time
    
    print(f"\n🚀 2回目の実行（キャッシュ）:")
    print("-" * 40)
    start_time = time.time()
    result2 = agent.generate_response_with_fallback(prompt, task, progress_callback_second)
    elapsed2 = time.time() - start_time
    
    print(f"\n📊 比較結果:")
    print(f"1回目: {len(progress_reports_first)}件の報告, {elapsed1:.2f}秒")
    print(f"2回目: {len(progress_reports_second)}件の報告, {elapsed2:.2f}秒")
    print(f"改善率: {((elapsed1 - elapsed2) / elapsed1 * 100):.1f}%")
    
    print(f"\n📋 1回目のステップ:")
    for i, report in enumerate(progress_reports_first, 1):
        print(f"   {i}. {report['step']} ({report['progress']:.1f}%)")
    
    print(f"\n📋 2回目のステップ:")
    for i, report in enumerate(progress_reports_second, 1):
        print(f"   {i}. {report['step']} ({report['progress']:.1f}%)")

if __name__ == "__main__":
    # 基本的なステップ進行テスト
    test_step_progress()
    
    print("\n" + "=" * 80)
    
    # キャッシュ時のステップ進行テスト
    test_cache_step_progress()
    
    print(f"\n🎉 ステップ進行ごとの途中報告テスト完了！")
