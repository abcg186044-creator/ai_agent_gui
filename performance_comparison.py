#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パフォーマンス比較テスト
"""

from unlimited_agent_main import UnlimitedFriendAgent
from fast_unlimited_agent import FastUnlimitedAgent
import time

def compare_performance():
    """パフォーマンス比較テスト"""
    print("🚀 パフォーマンス比較テスト")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        {
            "name": "電卓アプリ開発",
            "prompt": "PythonでGUIをクリックして操作できる電卓アプリを作成してください",
            "task": "Python GUI電卓アプリ開発"
        },
        {
            "name": "Webアプリ開発",
            "prompt": "HTMLで電卓アプリを作成してください",
            "task": "Web電卓アプリ開発"
        },
        {
            "name": "Androidアプリ開発",
            "prompt": "Androidで電卓アプリを開発してください",
            "task": "Android電卓アプリ開発"
        }
    ]
    
    # エージェントの準備
    standard_agent = UnlimitedFriendAgent()
    fast_agent = FastUnlimitedAgent()
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📋 テスト: {test_case['name']}")
        print("-" * 40)
        
        # 標準版テスト
        print("🐌 標準版実行中...")
        start_time = time.time()
        standard_result = standard_agent.generate_response_with_fallback(
            test_case['prompt'], 
            test_case['task']
        )
        standard_time = time.time() - start_time
        
        # 高速版テスト
        print("🚀 高速版実行中...")
        start_time = time.time()
        fast_result = fast_agent.generate_response_with_fallback(
            test_case['prompt'], 
            test_case['task']
        )
        fast_time = time.time() - start_time
        
        # 結果の記録
        test_result = {
            "name": test_case['name'],
            "standard_time": standard_time,
            "fast_time": fast_time,
            "standard_success": standard_result['success'],
            "fast_success": fast_result['success'],
            "standard_approach": standard_result.get('approach', 'N/A'),
            "fast_approach": fast_result.get('approach', 'N/A'),
            "improvement": ((standard_time - fast_time) / standard_time * 100) if standard_time > 0 else 0
        }
        results.append(test_result)
        
        # 結果表示
        print(f"📊 結果:")
        print(f"   標準版: {standard_time:.2f}秒 ({test_result['standard_approach']})")
        print(f"   高速版: {fast_time:.2f}秒 ({test_result['fast_approach']})")
        print(f"   改善率: {test_result['improvement']:.1f}%")
        
        if standard_time > fast_time:
            print(f"   ✅ 高速版が {standard_time - fast_time:.2f}秒 速い")
        else:
            print(f"   ❌ 標準版が {fast_time - standard_time:.2f}秒 速い")
    
    # 総合結果
    print(f"\n📊 総合パフォーマンス比較")
    print("=" * 60)
    
    total_standard_time = sum(r['standard_time'] for r in results)
    total_fast_time = sum(r['fast_time'] for r in results)
    overall_improvement = ((total_standard_time - total_fast_time) / total_standard_time * 100) if total_standard_time > 0 else 0
    
    print(f"🐌 標準版総時間: {total_standard_time:.2f}秒")
    print(f"🚀 高速版総時間: {total_fast_time:.2f}秒")
    print(f"📈 総合改善率: {overall_improvement:.1f}%")
    
    if total_standard_time > total_fast_time:
        print(f"✅ 高速版が全体で {total_standard_time - total_fast_time:.2f}秒 速い")
    else:
        print(f"❌ 標準版が全体で {total_fast_time - total_standard_time:.2f}秒 速い")
    
    # 詳細な比較
    print(f"\n📋 詳細比較:")
    print(f"{'テスト':<20} {'標準版':<12} {'高速版':<12} {'改善率':<10} {'勝者'}")
    print("-" * 70)
    
    for result in results:
        winner = "高速版" if result['fast_time'] < result['standard_time'] else "標準版"
        print(f"{result['name']:<20} {result['standard_time']:<12.2f} {result['fast_time']:<12.2f} {result['improvement']:<10.1f}% {winner}")
    
    return results

def test_model_performance():
    """モデル別パフォーマンステスト"""
    print(f"\n🤖 モデル別パフォーマンステスト")
    print("=" * 60)
    
    models = ["llama3.1:8b", "llama3.2:3b"]
    test_prompt = "Pythonで簡単な電卓アプリを作成してください"
    test_task = "Python電卓アプリ開発"
    
    results = {}
    
    for model in models:
        print(f"\n📋 モデル: {model}")
        print("-" * 40)
        
        # 高速エージェントでテスト
        agent = FastUnlimitedAgent(model=model)
        
        start_time = time.time()
        result = agent.generate_response_with_fallback(test_prompt, test_task)
        elapsed = time.time() - start_time
        
        results[model] = {
            "time": elapsed,
            "success": result['success'],
            "approach": result.get('approach', 'N/A'),
            "response_length": len(result.get('response', ''))
        }
        
        print(f"⏱️ 時間: {elapsed:.2f}秒")
        print(f"✅ 成功: {result['success']}")
        print(f"🔄 アプローチ: {result.get('approach', 'N/A')}")
        print(f"📝 応答長: {len(result.get('response', ''))}文字")
    
    # モデル比較
    print(f"\n📊 モデル比較:")
    print(f"{'モデル':<15} {'時間':<10} {'成功':<8} {'応答長':<10}")
    print("-" * 45)
    
    for model, data in results.items():
        print(f"{model:<15} {data['time']:<10.2f} {data['success']:<8} {data['response_length']:<10}")
    
    return results

if __name__ == "__main__":
    # パフォーマンス比較
    comparison_results = compare_performance()
    
    # モデル別テスト
    model_results = test_model_performance()
    
    print(f"\n🎉 パフォーマンステスト完了！")
    print(f"\n💡 最適化提案:")
    print(f"1. llama3.2:3bモデルを使用して速度を向上")
    print(f"2. タイムアウトを120秒に短縮")
    print(f"3. プロンプトを最適化して長さを制限")
    print(f"4. キャッシュを活用して再実行を高速化")
    print(f"5. 静的知識ベースを優先的に使用")
