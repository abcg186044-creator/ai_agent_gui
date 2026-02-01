"""
ファイルマップとターゲット解決モジュール
プロジェクト内の全ファイルの役割を管理し、最適な修正対象を特定
"""

from typing import Dict, Optional, List
from pathlib import Path
from .constants import *

# プロジェクト内の全ファイルマップ
FILE_MAP = {
    # コアシステム
    "core/constants.py": {
        "role": "定数管理",
        "description": "パス設定、UIカラー、セッションキーなどの定数を定義",
        "categories": ["定数", "設定", "パス", "カラー"],
        "dependencies": [],
        "file_size": "small",
        "change_frequency": "low"
    },
    "core/llm_client.py": {
        "role": "LLM通信",
        "description": "Ollamaとの通信、自己進化ロジック、TODO抽出",
        "categories": ["AI", "LLM", "進化", "会話", "TODO"],
        "dependencies": ["constants.py", "self_mutation.py"],
        "file_size": "medium",
        "change_frequency": "medium"
    },
    "core/vrm_controller.py": {
        "role": "VRM制御",
        "description": "VRMモデルのロード、表示、表情制御",
        "categories": ["VRM", "アバター", "表情", "3D"],
        "dependencies": ["constants.py"],
        "file_size": "medium",
        "change_frequency": "low"
    },
    "core/self_mutation.py": {
        "role": "自己改造",
        "description": "モジュール対応の自己改造プロトコル",
        "categories": ["進化", "改造", "リファクタリング"],
        "dependencies": ["constants.py"],
        "file_size": "medium",
        "change_frequency": "low"
    },
    
    # UIコンポーネント
    "ui/styles.py": {
        "role": "UIスタイル",
        "description": "LINE風CSS、テーマ設定、デザイン一貫性",
        "categories": ["デザイン", "UI", "CSS", "スタイル", "テーマ"],
        "dependencies": ["constants.py"],
        "file_size": "medium",
        "change_frequency": "high"
    },
    "ui/components.py": {
        "role": "UIコンポーネント",
        "description": "チャット表示、ツール棚、TODO/メモパネル",
        "categories": ["UI", "コンポーネント", "チャット", "TODO", "メモ"],
        "dependencies": ["constants.py", "state_manager.py", "app_generator.py"],
        "file_size": "large",
        "change_frequency": "high"
    },
    
    # サービス層
    "services/app_generator.py": {
        "role": "アプリ生成",
        "description": "コード生成、アプリ実行、自己修復",
        "categories": ["生成", "アプリ", "コード", "実行", "修復"],
        "dependencies": ["constants.py"],
        "file_size": "medium",
        "change_frequency": "medium"
    },
    "services/state_manager.py": {
        "role": "状態管理",
        "description": "会話履歴、TODO、日記の保存・読み込み",
        "categories": ["データ", "保存", "状態", "永続化", "日記"],
        "dependencies": ["constants.py"],
        "file_size": "medium",
        "change_frequency": "medium"
    },
    
    # メインアプリケーション
    "main_app_new.py": {
        "role": "エントリーポイント",
        "description": "Streamlitメインループ、全機能の統合",
        "categories": ["メイン", "エントリー", "統合"],
        "dependencies": ["core/*", "ui/*", "services/*"],
        "file_size": "small",
        "change_frequency": "low"
    },
    
    # レガシーファイル（後方互換性）
    "ollama_vrm_integrated_app.py": {
        "role": "レガシーアプリ",
        "description": "単一ファイル版の完全なAIシステム",
        "categories": ["レガシー", "完全版", "互換性"],
        "dependencies": [],
        "file_size": "xlarge",
        "change_frequency": "none"
    }
}

# カテゴリからファイルへのマッピング
CATEGORY_TO_FILES = {
    "デザイン": ["ui/styles.py"],
    "UI": ["ui/styles.py", "ui/components.py"],
    "CSS": ["ui/styles.py"],
    "スタイル": ["ui/styles.py"],
    "テーマ": ["ui/styles.py"],
    
    "AI": ["core/llm_client.py"],
    "LLM": ["core/llm_client.py"],
    "進化": ["core/llm_client.py", "core/self_mutation.py"],
    "会話": ["core/llm_client.py", "ui/components.py"],
    "性格": ["core/llm_client.py"],
    "人格": ["core/llm_client.py"],
    
    "VRM": ["core/vrm_controller.py"],
    "アバター": ["core/vrm_controller.py"],
    "表情": ["core/vrm_controller.py"],
    "3D": ["core/vrm_controller.py"],
    
    "TODO": ["ui/components.py", "core/llm_client.py"],
    "メモ": ["ui/components.py"],
    "ツール": ["ui/components.py"],
    
    "生成": ["services/app_generator.py"],
    "アプリ": ["services/app_generator.py"],
    "コード": ["services/app_generator.py"],
    "実行": ["services/app_generator.py"],
    "修復": ["services/app_generator.py"],
    
    "データ": ["services/state_manager.py"],
    "保存": ["services/state_manager.py"],
    "状態": ["services/state_manager.py"],
    "永続化": ["services/state_manager.py"],
    "日記": ["services/state_manager.py"],
    
    "定数": ["core/constants.py"],
    "設定": ["core/constants.py"],
    "パス": ["core/constants.py"],
    "カラー": ["core/constants.py"],
    
    "改造": ["core/self_mutation.py"],
    "リファクタリング": ["core/self_mutation.py"],
    
    "メイン": ["main_app_new.py"],
    "エントリー": ["main_app_new.py"],
    "統合": ["main_app_new.py"]
}

class FileMapResolver:
    """ファイルマップ解決クラス"""
    
    def __init__(self):
        self.file_map = FILE_MAP
        self.category_map = CATEGORY_TO_FILES
    
    def resolve_target_file(self, category: str) -> Optional[str]:
        """カテゴリから最適なファイルパスを解決"""
        # 直接カテゴリマッチ
        if category in self.category_map:
            files = self.category_map[category]
            # 優先度順に返す（最初のファイルを最優先）
            return files[0] if files else None
        
        # 部分一致検索
        for cat_key, files in self.category_map.items():
            if category in cat_key or cat_key in category:
                return files[0] if files else None
        
        # ファイルマップ内のカテゴリ検索
        for file_path, file_info in self.file_map.items():
            if category in file_info["categories"]:
                return file_path
        
        return None
    
    def get_file_info(self, file_path: str) -> Dict:
        """ファイル情報を取得"""
        return self.file_map.get(file_path, {})
    
    def get_files_by_category(self, category: str) -> List[str]:
        """カテゴリに属する全ファイルを取得"""
        files = []
        
        # 直接マッチ
        if category in self.category_map:
            files.extend(self.category_map[category])
        
        # 部分一致
        for cat_key, cat_files in self.category_map.items():
            if category in cat_key or cat_key in category:
                files.extend(cat_files)
        
        # 重複を除去して返す
        return list(set(files))
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """ファイルの依存関係を取得"""
        file_info = self.get_file_info(file_path)
        return file_info.get("dependencies", [])
    
    def get_change_frequency(self, file_path: str) -> str:
        """ファイルの変更頻度を取得"""
        file_info = self.get_file_info(file_path)
        return file_info.get("change_frequency", "unknown")
    
    def suggest_files_for_request(self, user_request: str) -> List[str]:
        """ユーザー要求から関連ファイルを提案"""
        suggested_files = []
        request_lower = user_request.lower()
        
        # キーワードマッチング
        for file_path, file_info in self.file_map.items():
            for category in file_info["categories"]:
                if category.lower() in request_lower:
                    suggested_files.append(file_path)
                    break
        
        return suggested_files
    
    def get_file_loading_priority(self, file_path: str) -> int:
        """ファイルの読み込み優先度を取得（1=最高優先度）"""
        file_info = self.get_file_info(file_path)
        change_freq = file_info.get("change_frequency", "medium")
        file_size = file_info.get("file_size", "medium")
        
        # 変更頻度が高いほど優先度が高い
        if change_freq == "high":
            base_priority = 1
        elif change_freq == "medium":
            base_priority = 2
        else:
            base_priority = 3
        
        # ファイルサイズが小さいほど優先度が高い
        if file_size == "small":
            size_modifier = 0
        elif file_size == "medium":
            size_modifier = 1
        else:
            size_modifier = 2
        
        return base_priority + size_modifier
    
    def optimize_loading_order(self, file_paths: List[str]) -> List[str]:
        """ファイル読み込み順序を最適化"""
        return sorted(file_paths, key=lambda x: self.get_file_loading_priority(x))

# グローバルインスタンス
file_resolver = FileMapResolver()

def resolve_target_file(category: str) -> Optional[str]:
    """カテゴリから最適なファイルパスを返す（簡易関数）"""
    return file_resolver.resolve_target_file(category)

def get_relevant_files(user_request: str) -> List[str]:
    """ユーザー要求に関連するファイルを取得"""
    return file_resolver.suggest_files_for_request(user_request)

def should_load_file(file_path: str, user_request: str) -> bool:
    """ファイルを読み込むべきか判断"""
    relevant_files = get_relevant_files(user_request)
    return file_path in relevant_files
