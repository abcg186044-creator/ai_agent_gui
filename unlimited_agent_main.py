#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制限なし親友エージェントメイン
"""

from unlimited_agent_manager import UnlimitedAgentManager

class UnlimitedFriendAgent:
    """制限なし親友エージェント"""
    
    def __init__(self, timeout_threshold: int = 240):
        self.manager = UnlimitedAgentManager(timeout_threshold)
    
    def generate_response_with_fallback(self, prompt: str, task_description: str = "", progress_callback=None):
        """フォールバック付き応答生成（途中報告付き）"""
        return self.manager.generate_response_with_fallback(prompt, task_description, progress_callback)
    
    def get_system_status(self):
        """システムステータスを取得"""
        return self.manager.get_system_status()
    
    def clear_cache(self):
        """キャッシュをクリア"""
        return self.manager.clear_cache()
    
    def export_cache(self, filepath: str):
        """キャッシュをエクスポート"""
        return self.manager.export_cache(filepath)

# テスト用
if __name__ == "__main__":
    agent = UnlimitedFriendAgent()
    
    test_prompt = "PythonでGUIをクリックして操作できる電卓アプリを作成してください"
    test_task = "Python GUI電卓アプリ開発"
    
    print("🚀 分割版制限なし親友エージェントテスト開始（途中報告付き）")
    print("=" * 60)
    
    # 途中報告コールバック関数
    def progress_callback(progress_info):
        print(f"📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        if 'elapsed' in progress_info:
            print(f"   ⏱️ 経過時間: {progress_info['elapsed']:.1f}秒")
        if 'approach' in progress_info:
            print(f"   🔄 アプローチ: {progress_info['approach']}")
        print("-" * 50)
    
    result = agent.generate_response_with_fallback(test_prompt, test_task, progress_callback)
    
    print("\n📊 結果:")
    print(f"✅ 成功: {result['success']}")
    if result['success']:
        print(f"🔄 使用アプローチ: {result['approach']}")
        print(f"⏱️ 所要時間: {result['elapsed_time']:.2f}秒")
        print(f"📝 応答長: {len(result['response'])}文字")
        print(f"📋 キャッシュ使用: {result.get('from_cache', False)}")
    else:
        print(f"❌ エラー: {result['error']}")
        print(f"⏱️ 総時間: {result['total_time']:.2f}秒")
        print(f"🔄 試行アプローチ数: {result['attempted_approaches']}")
    
    # システムステータスを表示
    print("\n📊 システムステータス:")
    status = agent.get_system_status()
    print(f"🔧 総アプローチ数: {status['total_approaches']}")
    print(f"📋 キャッシュサイズ: {status['cache_size']}")
    print(f"📈 実行履歴: {status['execution_history_size']}件")
