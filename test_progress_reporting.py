#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
途中報告機能のテスト
"""

from unlimited_agent_main import UnlimitedFriendAgent
import time

def test_progress_reporting():
    """途中報告機能のテスト"""
    agent = UnlimitedFriendAgent()
    
    print("🧪 途中報告機能テスト")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        {
            "name": "静的知識ベーステスト",
            "prompt": "電卓アプリ",
            "task": "Python GUI電卓アプリ開発",
            "expected_approach": "static_knowledge"
        },
        {
            "name": "テンプレート応答テスト",
            "prompt": "一般的なアプリ開発",
            "task": "汎用アプリケーション開発",
            "expected_approach": "template_response"
        },
        {
            "name": "ヒューリスティクス推論テスト",
            "prompt": "複雑なシステム設計",
            "task": "エンタープライズシステム設計",
            "expected_approach": "heuristic_reasoning"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 テスト {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 40)
        
        # 途中報告を記録
        progress_reports = []
        
        def progress_callback(progress_info):
            progress_reports.append(progress_info)
            print(f"📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
            if 'approach' in progress_info:
                print(f"   🔄 アプローチ: {progress_info['approach']}")
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
            max_progress = max(r['progress'] for r in progress_reports)
            approaches_reported = set(r.get('approach', 'N/A') for r in progress_reports if 'approach' in r)
            
            print(f"📈 最大進捗: {max_progress:.1f}%")
            print(f"🔄 報告されたアプローチ: {approaches_reported}")
        
        print("\n" + "=" * 60)

def test_ollama_progress():
    """Ollama APIの途中報告テスト"""
    agent = UnlimitedFriendAgent()
    
    print("🤖 Ollama API途中報告テスト")
    print("=" * 60)
    
    progress_reports = []
    
    def detailed_progress_callback(progress_info):
        progress_reports.append(progress_info)
        timestamp = time.strftime("%H:%M:%S")
        
        print(f"[{timestamp}] 📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        
        if 'elapsed' in progress_info:
            print(f"           ⏱️ 経過時間: {progress_info['elapsed']:.1f}秒")
        
        if 'approach' in progress_info:
            print(f"           🔄 アプローチ: {progress_info['approach']}")
        
        if 'success' in progress_info:
            print(f"           ✅ 成功: {progress_info['success']}")
        
        if 'error' in progress_info:
            print(f"           ❌ エラー: {progress_info['error']}")
        
        print("-" * 50)
    
    print("🚀 Ollama APIで電卓アプリ生成（途中報告付き）")
    print("-" * 60)
    
    start_time = time.time()
    result = agent.generate_response_with_fallback(
        "PythonでGUIをクリックして操作できる電卓アプリを作成してください",
        "Python GUI電卓アプリ開発",
        detailed_progress_callback
    )
    elapsed = time.time() - start_time
    
    print(f"\n🎯 最終結果:")
    print(f"✅ 成功: {result['success']}")
    print(f"🔄 アプローチ: {result['approach']}")
    print(f"⏱️ 総時間: {elapsed:.2f}秒")
    print(f"📊 途中報告数: {len(progress_reports)}件")
    print(f"📝 応答長: {len(result['response'])}文字")
    
    # 途中報告の詳細分析
    if progress_reports:
        print(f"\n📊 途中報告分析:")
        
        # 時間分布
        time_intervals = []
        for i in range(1, len(progress_reports)):
            if 'elapsed' in progress_reports[i] and 'elapsed' in progress_reports[i-1]:
                interval = progress_reports[i]['elapsed'] - progress_reports[i-1]['elapsed']
                time_intervals.append(interval)
        
        if time_intervals:
            avg_interval = sum(time_intervals) / len(time_intervals)
            print(f"   📊 平均報告間隔: {avg_interval:.1f}秒")
        
        # 進捗分布
        progress_values = [r['progress'] for r in progress_reports]
        if progress_values:
            print(f"   📈 進捗範囲: {min(progress_values):.1f}% - {max(progress_values):.1f}%")
        
        # アプローチ別報告
        approach_counts = {}
        for report in progress_reports:
            approach = report.get('approach', 'general')
            approach_counts[approach] = approach_counts.get(approach, 0) + 1
        
        print(f"   🔄 アプローチ別報告数:")
        for approach, count in approach_counts.items():
            print(f"      {approach}: {count}件")

if __name__ == "__main__":
    # 基本的な途中報告テスト
    test_progress_reporting()
    
    print("\n" + "=" * 80)
    
    # Ollama APIの詳細テスト
    test_ollama_progress()
    
    print(f"\n🎉 途中報告機能テスト完了！")
