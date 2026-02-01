#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高速版制限なし親友エージェント
"""

from unlimited_agent_main import UnlimitedFriendAgent

class FastUnlimitedAgent(UnlimitedFriendAgent):
    """高速版制限なし親友エージェント"""
    
    def __init__(self, timeout_threshold: int = 120, model: str = "llama3.2:3b"):
        # タイムアウトを短く設定
        super().__init__(timeout_threshold)
        
        # 高速モデルを使用
        self.manager.approaches[0].model = model
        self.manager.approaches[0].timeout = timeout_threshold
    
    def generate_response_with_fallback(self, prompt: str, task_description: str = "", progress_callback=None):
        """高速応答生成"""
        # プロンプトを最適化
        optimized_prompt = self._optimize_prompt(prompt, task_description)
        
        return super().generate_response_with_fallback(
            optimized_prompt, 
            task_description, 
            progress_callback
        )
    
    def _optimize_prompt(self, prompt: str, task_description: str) -> str:
        """プロンプトを最適化して高速化"""
        # 簡潔なプロンプトに変換
        if len(prompt) > 200:
            # 重要な部分だけを抽出
            prompt_parts = prompt.split()
            prompt = " ".join(prompt_parts[:50]) + "..."
        
        # タスク説明を追加して明確化
        if task_description:
            prompt = f"{task_description}について: {prompt}"
        
        return prompt

# テスト用
if __name__ == "__main__":
    agent = FastUnlimitedAgent()
    
    test_prompt = "PythonでGUIをクリックして操作できる電卓アプリを作成してください"
    test_task = "Python GUI電卓アプリ開発"
    
    print("🚀 高速版制限なし親友エージェントテスト開始")
    print("=" * 60)
    
    def progress_callback(progress_info):
        print(f"📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        if 'elapsed' in progress_info:
            print(f"   ⏱️ 経過時間: {progress_info['elapsed']:.1f}秒")
        if 'approach' in progress_info:
            print(f"   🔄 アプローチ: {progress_info['approach']}")
        print("-" * 30)
    
    import time
    start_time = time.time()
    
    result = agent.generate_response_with_fallback(test_prompt, test_task, progress_callback)
    
    elapsed = time.time() - start_time
    
    print("\n📊 結果:")
    print(f"✅ 成功: {result['success']}")
    if result['success']:
        print(f"🔄 使用アプローチ: {result['approach']}")
        print(f"⏱️ 所要時間: {elapsed:.2f}秒")
        print(f"📝 応答長: {len(result['response'])}文字")
        print(f"📋 キャッシュ使用: {result.get('from_cache', False)}")
    else:
        print(f"❌ エラー: {result['error']}")
        print(f"⏱️ 総時間: {elapsed:.2f}秒")
        print(f"🔄 試行アプローチ数: {result['attempted_approaches']}")
    
    # システムステータスを表示
    print("\n📊 システムステータス:")
    status = agent.get_system_status()
    print(f"🔧 総アプローチ数: {status['total_approaches']}")
    print(f"📋 キャッシュサイズ: {status['cache_size']}")
    print(f"📈 実行履歴: {status['execution_history_size']}件")
