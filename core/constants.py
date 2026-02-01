"""
定数設定ファイル
パス設定や共通定数を管理
"""

import os
from pathlib import Path

# ベースディレクトリ
BASE_DIR = Path(__file__).parent.parent

# データディレクトリ
DATA_DIR = BASE_DIR / "data"
GENERATED_APPS_DIR = BASE_DIR / "generated_apps"

# ファイルパス定数
WORKSPACE_STATE_FILE = DATA_DIR / "workspace_state.json"
AGENT_DIARY_FILE = DATA_DIR / "agent_diary.json"
PERSONALITIES_FILE = BASE_DIR / "personalities.json"
PERSONALITIES_CUSTOM_FILE = BASE_DIR / "personalities_custom.json"

# VRM関連
VRM_FILE = BASE_DIR / "vrm" / "AliciaSolid_state.vrm"

# UIデザイン定数
UI_COLORS = {
    "background": "#F5F5DC",  # ベージュ
    "accent": "#8B4513",      # 茶色
    "secondary": "#A0522D",    # 濃い茶色
    "text": "#333333",        # テキスト色
    "white": "#FFFFFF"        # 白色
}

UI_STYLES = {
    "border_radius": "18px",
    "padding": "15px",
    "border": f"2px solid {UI_COLORS['accent']}",
    "shadow": f"0 4px 8px rgba(139, 69, 19, 0.2)"
}

# セッション状態キー
SESSION_KEYS = {
    "conversation_history": "conversation_history",
    "current_personality": "current_personality",
    "ollama": "ollama",
    "vrm_controller": "vrm_controller",
    "todo_list": "todo_list",
    "quick_memos": "quick_memos",
    "active_app": "active_app",
    "show_app_inline": "show_app_inline"
}
