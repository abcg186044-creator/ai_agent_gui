#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制限なし親友エージェントの包括的テスト
"""

from unlimited_agent_main import UnlimitedFriendAgent
import time

def test_agent():
    """エージェントの包括的テスト"""
    agent = UnlimitedFriendAgent()
    
    print("🧪 制限なし親友エージェント包括的テスト")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        {
            "name": "電卓アプリ開発",
            "prompt": "PythonでGUIをクリックして操作できる電卓アプリを作成してください",
            "task": "Python GUI電卓アプリ開発"
        },
        {
            "name": "Androidアプリ開発",
            "prompt": "Androidで電卓アプリを開発してください",
            "task": "Android電卓アプリ開発"
        },
        {
            "name": "Webアプリ開発",
            "prompt": "HTMLで電卓アプリを作成してください",
            "task": "Web電卓アプリ開発"
        },
        {
            "name": "機械学習パイプライン",
            "prompt": "機械学習の分類モデルを作成してください",
            "task": "機械学習分類モデル開発"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 テスト {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 40)
        
        start_time = time.time()
        result = agent.generate_response_with_fallback(
            test_case['prompt'], 
            test_case['task']
        )
        elapsed = time.time() - start_time
        
        test_result = {
            "test_name": test_case['name'],
            "success": result['success'],
            "approach": result.get('approach', 'N/A'),
            "elapsed_time": elapsed,
            "response_length": len(result.get('response', '')),
            "from_cache": result.get('from_cache', False)
        }
        results.append(test_result)
        
        print(f"✅ 成功: {test_result['success']}")
        print(f"🔄 アプローチ: {test_result['approach']}")
        print(f"⏱️ 時間: {test_result['elapsed_time']:.2f}秒")
        print(f"📝 長さ: {test_result['response_length']}文字")
        print(f"📋 キャッシュ: {test_result['from_cache']}")
    
    # キャッシュテスト（同じリクエストを再実行）
    print(f"\n📋 キャッシュテスト: 電卓アプリ（再実行）")
    print("-" * 40)
    
    start_time = time.time()
    cache_result = agent.generate_response_with_fallback(
        test_cases[0]['prompt'], 
        test_cases[0]['task']
    )
    cache_elapsed = time.time() - start_time
    
    print(f"✅ 成功: {cache_result['success']}")
    print(f"🔄 アプローチ: {cache_result.get('approach', 'N/A')}")
    print(f"⏱️ 時間: {cache_elapsed:.2f}秒")
    print(f"📋 キャッシュ使用: {cache_result.get('from_cache', False)}")
    
    # 統計サマリー
    print(f"\n📊 テスト統計サマリー")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['success'])
    total_time = sum(r['elapsed_time'] for r in results)
    avg_time = total_time / len(results) if results else 0
    
    print(f"✅ 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    print(f"⏱️ 総時間: {total_time:.2f}秒")
    print(f"📊 平均時間: {avg_time:.2f}秒")
    
    # アプローチ別統計
    approach_stats = {}
    for result in results:
        approach = result['approach']
        if approach not in approach_stats:
            approach_stats[approach] = {'count': 0, 'success': 0}
        approach_stats[approach]['count'] += 1
        if result['success']:
            approach_stats[approach]['success'] += 1
    
    print(f"\n🔄 アプローチ別統計:")
    for approach, stats in approach_stats.items():
        success_rate = stats['success'] / stats['count'] * 100 if stats['count'] > 0 else 0
        print(f"  {approach}: {stats['success']}/{stats['count']} ({success_rate:.1f}%)")
    
    # システムステータス
    print(f"\n📊 最終システムステータス:")
    status = agent.get_system_status()
    print(f"🔧 総アプローチ数: {status['total_approaches']}")
    print(f"📋 キャッシュサイズ: {status['cache_size']}")
    print(f"📈 実行履歴: {status['execution_history_size']}件")
    
    # キャッシュエクスポートテスト
    print(f"\n💾 キャッシュエクスポートテスト:")
    try:
        agent.export_cache("test_cache_export.json")
        print("✅ キャッシュエクスポート成功")
    except Exception as e:
        print(f"❌ キャッシュエクスポート失敗: {str(e)}")
    
    return results

if __name__ == "__main__":
    test_results = test_agent()
    print(f"\n🎉 テスト完了！")
