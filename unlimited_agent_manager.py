#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制限なし親友エージェントマネージャー
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from unlimited_agent_core import (
    ApproachInterface,
    OllamaApproach,
    StaticKnowledgeApproach,
    TemplateApproach,
    HeuristicApproach
)

class UnlimitedAgentManager:
    """制限なし親友エージェントマネージャー"""
    
    def __init__(self, timeout_threshold: int = 240):
        self.timeout_threshold = timeout_threshold
        self.approaches: List[ApproachInterface] = []
        self.solution_cache: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        # アプローチを初期化
        self._initialize_approaches()
    
    def _initialize_approaches(self):
        """アプローチを初期化"""
        self.approaches = [
            OllamaApproach(timeout=self.timeout_threshold, model="llama3.2:3b"),
            StaticKnowledgeApproach(),
            TemplateApproach(),
            HeuristicApproach()
        ]
    
    def generate_response_with_fallback(self, prompt: str, task_description: str = "", progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """フォールバック付き応答生成（ステップ進行ごとに報告）"""
        start_time = time.time()
        
        # 開始報告
        if progress_callback:
            progress_callback({
                "step": "🚀 処理を開始します",
                "progress": 0,
                "total_approaches": len(self.approaches)
            })
        
        # キャッシュをチェック
        if progress_callback:
            progress_callback({
                "step": "📋 キャッシュを確認中...",
                "progress": 5
            })
        
        cache_key = self._generate_cache_key(prompt, task_description)
        if cache_key in self.solution_cache:
            cached_result = self.solution_cache[cache_key]
            print(f"📋 キャッシュヒット: {cached_result['approach']}")
            
            if progress_callback:
                progress_callback({
                    "step": f"📋 キャッシュから応答を取得: {cached_result['approach']}",
                    "progress": 100,
                    "approach": cached_result['approach'],
                    "from_cache": True
                })
            
            return {
                "success": True,
                "approach": cached_result['approach'],
                "response": cached_result['response'],
                "elapsed_time": 0.1,
                "approach_index": 0,
                "from_cache": True
            }
        
        if progress_callback:
            progress_callback({
                "step": "🔄 各アプローチを試行します",
                "progress": 10
            })
        
        # 各アプローチを試行
        for approach_index, approach in enumerate(self.approaches):
            approach_name = approach.get_name()
            approach_progress = 10 + (approach_index / len(self.approaches)) * 80
            
            print(f"🔄 アプローチ {approach_index + 1}/{len(self.approaches)}: {approach_name}")
            
            if progress_callback:
                progress_callback({
                    "step": f"🔄 {approach_name} を試行中...",
                    "progress": approach_progress,
                    "approach": approach_name,
                    "approach_index": approach_index
                })
            
            try:
                response = approach.execute(prompt, task_description, progress_callback)
                
                if response and not response.startswith("エラー") and not response.startswith("Ollama APIエラー"):
                    elapsed = time.time() - start_time
                    print(f"✅ 成功: {approach_name} (所要時間: {elapsed:.2f}秒)")
                    
                    # 成功結果をキャッシュ
                    self._cache_solution(cache_key, approach_name, response)
                    
                    # 実行履歴を記録
                    self._record_execution(approach_name, True, elapsed, response)
                    
                    if progress_callback:
                        progress_callback({
                            "step": f"✅ {approach_name} で成功",
                            "progress": 100,
                            "approach": approach_name,
                            "approach_index": approach_index,
                            "success": True,
                            "elapsed": elapsed
                        })
                    
                    return {
                        "success": True,
                        "approach": approach_name,
                        "response": response,
                        "elapsed_time": elapsed,
                        "approach_index": approach_index,
                        "from_cache": False
                    }
                    
            except Exception as e:
                print(f"❌ {approach_name} でエラー: {str(e)}")
                self._record_execution(approach_name, False, time.time() - start_time, str(e))
                
                if progress_callback:
                    progress_callback({
                        "step": f"❌ {approach_name} でエラー: {str(e)}",
                        "progress": approach_progress + 10,
                        "approach": approach_name,
                        "error": str(e)
                    })
                
                continue
        
        # すべてのアプローチが失敗
        elapsed = time.time() - start_time
        print(f"❌ すべてのアプローチが失敗 (総時間: {elapsed:.2f}秒)")
        
        if progress_callback:
            progress_callback({
                "step": "❌ すべてのアプローチが失敗",
                "progress": 100,
                "error": "すべてのアプローチが失敗しました",
                "total_time": elapsed
            })
        
        return {
            "success": False,
            "error": "すべてのアプローチが失敗しました",
            "total_time": elapsed,
            "attempted_approaches": len(self.approaches),
            "from_cache": False
        }
    
    def _generate_cache_key(self, prompt: str, task_description: str) -> str:
        """キャッシュキーを生成"""
        import hashlib
        combined = f"{prompt}_{task_description}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _cache_solution(self, cache_key: str, approach: str, response: str):
        """解決策をキャッシュ"""
        self.solution_cache[cache_key] = {
            "approach": approach,
            "response": response,
            "timestamp": time.time(),
            "success_rate": 1.0
        }
    
    def _record_execution(self, approach: str, success: bool, elapsed_time: float, result: str):
        """実行履歴を記録"""
        self.execution_history.append({
            "approach": approach,
            "success": success,
            "elapsed_time": elapsed_time,
            "result": result,
            "timestamp": time.time()
        })
        
        # 履歴が多すぎる場合は古いものを削除
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]
    
    def add_custom_approach(self, approach: ApproachInterface):
        """カスタムアプローチを追加"""
        self.approaches.append(approach)
        print(f"✅ カスタムアプローチを追加: {approach.get_name()}")
    
    def remove_approach(self, approach_name: str) -> bool:
        """アプローチを削除"""
        for i, approach in enumerate(self.approaches):
            if approach.get_name() == approach_name:
                removed = self.approaches.pop(i)
                print(f"✅ アプローチを削除: {approach_name}")
                return True
        print(f"❌ アプローチが見つかりません: {approach_name}")
        return False
    
    def get_approach_statistics(self) -> Dict[str, Any]:
        """アプローチ統計を取得"""
        stats = {}
        
        for approach in self.approaches:
            approach_name = approach.get_name()
            executions = [e for e in self.execution_history if e["approach"] == approach_name]
            
            if executions:
                success_count = sum(1 for e in executions if e["success"])
                avg_time = sum(e["elapsed_time"] for e in executions) / len(executions)
                
                stats[approach_name] = {
                    "total_executions": len(executions),
                    "success_count": success_count,
                    "success_rate": success_count / len(executions),
                    "average_time": avg_time,
                    "last_execution": executions[-1]["timestamp"]
                }
            else:
                stats[approach_name] = {
                    "total_executions": 0,
                    "success_count": 0,
                    "success_rate": 0.0,
                    "average_time": 0.0,
                    "last_execution": None
                }
        
        return stats
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.solution_cache.clear()
        print("✅ キャッシュをクリアしました")
    
    def clear_history(self):
        """実行履歴をクリア"""
        self.execution_history.clear()
        print("✅ 実行履歴をクリアしました")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """キャッシュ情報を取得"""
        return {
            "cache_size": len(self.solution_cache),
            "cache_keys": list(self.solution_cache.keys()),
            "oldest_cache": min(self.solution_cache.values(), key=lambda x: x["timestamp"])["timestamp"] if self.solution_cache else None,
            "newest_cache": max(self.solution_cache.values(), key=lambda x: x["timestamp"])["timestamp"] if self.solution_cache else None
        }
    
    def export_cache(self, filepath: str):
        """キャッシュをエクスポート"""
        import json
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.solution_cache, f, ensure_ascii=False, indent=2, default=str)
            print(f"✅ キャッシュをエクスポートしました: {filepath}")
        except Exception as e:
            print(f"❌ キャッシュエクスポートエラー: {str(e)}")
    
    def import_cache(self, filepath: str):
        """キャッシュをインポート"""
        import json
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_cache = json.load(f)
            self.solution_cache.update(imported_cache)
            print(f"✅ キャッシュをインポートしました: {filepath}")
        except Exception as e:
            print(f"❌ キャッシュインポートエラー: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        return {
            "total_approaches": len(self.approaches),
            "approach_names": [a.get_name() for a in self.approaches],
            "cache_size": len(self.solution_cache),
            "execution_history_size": len(self.execution_history),
            "timeout_threshold": self.timeout_threshold,
            "statistics": self.get_approach_statistics(),
            "cache_info": self.get_cache_info()
        }
