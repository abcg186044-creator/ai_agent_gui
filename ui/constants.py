"""
UIモジュールの定数設定
エゾモモンガ風の配色と基本スタイルを定義
"""

# エゾモモンガ風の配色
UI_COLORS = {
    "background": "#F5F5DC",  # ベージュ
    "accent": "#8B4513",      # 茶色
    "secondary": "#A0522D",    # 濃い茶色
    "text": "#333333",        # テキスト色
    "white": "#FFFFFF",        # 白色
    "light_beige": "#FAFAFA",  # 薄いベージュ
    "dark_brown": "#654321",   # 濃い茶色
    "squirrel_fur": "#8B7355",  # リスの毛色
    "nut_brown": "#8B6914",    # ナの色
    "tree_green": "#228B22"    # 木の緑
}

# 基本スタイル設定
UI_STYLES = {
    "border_radius": "18px",
    "padding": "15px",
    "margin": "10px",
    "border": f"2px solid {UI_COLORS['accent']}",
    "shadow": f"0 4px 8px rgba(139, 69, 19, 0.2)",
    "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "font_size": "14px",
    "transition": "all 0.3s ease"
}

# コンポーネント固有スタイル
COMPONENT_STYLES = {
    "button": {
        "border_radius": "12px",
        "padding": "8px 16px",
        "font_weight": "bold",
        "background": UI_COLORS["accent"],
        "color": UI_COLORS["white"],
        "border": "none",
        "cursor": "pointer"
    },
    "input": {
        "border_radius": "12px",
        "padding": "10px 12px",
        "border": f"1px solid {UI_COLORS['accent']}",
        "background": UI_COLORS["light_beige"],
        "font_size": "14px"
    },
    "card": {
        "border_radius": UI_STYLES["border_radius"],
        "padding": UI_STYLES["padding"],
        "background": UI_COLORS["white"],
        "border": UI_STYLES["border"],
        "shadow": UI_STYLES["shadow"]
    },
    "chat_bubble": {
        "border_radius": "18px",
        "padding": "12px 16px",
        "max_width": "70%",
        "margin": "8px 0"
    }
}

# レスポンシブデザイン設定
RESPONSIVE_STYLES = {
    "mobile_max_width": "768px",
    "tablet_max_width": "1024px",
    "desktop_min_width": "1025px"
}

# アニメーション設定
ANIMATIONS = {
    "fade_in": "opacity 0; animation: fadeIn 0.3s ease-in-out forwards;",
    "slide_up": "transform: translateY(20px); animation: slideUp 0.3s ease-out forwards;",
    "pulse": "animation: pulse 2s infinite;"
}

# テーマ設定
THEMES = {
    "ezomomonga": {
        "name": "エゾモモンガ",
        "primary": UI_COLORS["background"],
        "secondary": UI_COLORS["accent"],
        "accent": UI_COLORS["secondary"],
        "text": UI_COLORS["text"]
    },
    "forest": {
        "name": "森",
        "primary": "#2E7D32",
        "secondary": "#388E3C",
        "accent": "#4CAF50",
        "text": "#1B5E20"
    },
    "ocean": {
        "name": "海",
        "primary": "#0277BD",
        "secondary": "#0288D1",
        "accent": "#03A9F4",
        "text": "#01579B"
    }
}

# Z-index設定
Z_INDEX = {
    "dropdown": 1000,
    "modal": 1050,
    "tooltip": 1100,
    "notification": 1200
}
