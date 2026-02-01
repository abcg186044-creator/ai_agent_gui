"""
UIスタイルモジュール
LINE風CSSやテーマ設定（ベージュ・茶色）を管理
"""

import streamlit as st
from ui.constants import UI_COLORS, UI_STYLES, COMPONENT_STYLES, THEMES

def get_gliding_mode_css():
    """滑空モードのCSSを取得"""
    return f"""
    <style>
    .gliding-mode {{
        background: linear-gradient(135deg, #87CEEB 0%, #98FB98 50%, #F0E68C 100%);
        animation: gliding-gradient 8s ease-in-out infinite;
        transition: all 0.5s ease;
    }}
    
    @keyframes gliding-gradient {{
        0% {{ background-position: 0% 50%; }}
        25% {{ background-position: 100% 50%; }}
        50% {{ background-position: 100% 100%; }}
        75% {{ background-position: 0% 100%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    .gliding-avatar {{
        animation: gliding-float 3s ease-in-out infinite;
        transform-origin: center bottom;
    }}
    
    @keyframes gliding-float {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        25% {{ transform: translateY(-10px) rotate(-2deg); }}
        75% {{ transform: translateY(-5px) rotate(2deg); }}
    }}
    
    .gliding-chat {{
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(135, 206, 235, 0.5);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
    }}
    
    .gliding-button {{
        background: linear-gradient(45deg, #87CEEB, #98FB98);
        border: none;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    
    .gliding-button:hover {{
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(135, 206, 235, 0.4);
    }}
    </style>
    """

def apply_gliding_mode():
    """滑空モードを適用"""
    css = get_gliding_mode_css()
    st.markdown(css, unsafe_allow_html=True)
    
    # VRMアバターに滑空アニメーションを適用
    if 'vrm_controller' in st.session_state:
        vrm_controller = st.session_state['vrm_controller']
        vrm_controller.set_expression("happy")  # 滑空中は楽しい表情
    
    # 背景を滑空モードに設定
    st.markdown('<div class="gliding-mode">', unsafe_allow_html=True)
    
    return True

def disable_gliding_mode():
    """滑空モードを無効化"""
    # 通常のCSSに戻す
    css = get_line_chat_css()
    st.markdown(css, unsafe_allow_html=True)
    
    # VRMアバターを通常表情に戻す
    if 'vrm_controller' in st.session_state:
        vrm_controller = st.session_state['vrm_controller']
        vrm_controller.set_expression("neutral")
    
    return True
    """LINE風チャットのCSSを取得"""
    return f"""
    <style>
    .line-chat-container {{
        background-color: #E5DDD5;
        border-radius: 18px;
        padding: 20px;
        margin: 10px 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    
    .chat-message {{
        display: flex;
        margin-bottom: 15px;
        max-width: 100%;
    }}
    
    .user-message {{
        justify-content: flex-end;
    }}
    
    .ai-message {{
        justify-content: flex-start;
    }}
    
    .message-content {{
        max-width: 70%;
        display: flex;
        flex-direction: column;
    }}
    
    .user-message .message-content {{
        align-items: flex-end;
    }}
    
    .ai-message .message-content {{
        align-items: flex-start;
    }}
    
    .message-bubble {{
        padding: 12px 16px;
        border-radius: 18px;
        word-wrap: break-word;
        margin-bottom: 4px;
    }}
    
    .user-bubble {{
        background-color: #00C300;
        color: white;
        border-bottom-right-radius: 4px;
    }}
    
    .ai-bubble {{
        background-color: white;
        color: #333;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}
    
    .message-avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin: 0 10px;
    }}
    
    .user-avatar {{
        background-color: #E5DDD5;
        order: 2;
    }}
    
    .ai-avatar {{
        background-color: #FFF;
        border: 1px solid #DDD;
    }}
    
    .message-time {{
        font-size: 12px;
        color: #666;
        margin: 0 10px;
    }}
    
    .read-indicator {{
        font-size: 12px;
        color: #4FC3F7;
        margin-left: 4px;
    }}
    
    /* ツールパネルスタイル */
    .tool-panel {{
        background-color: {UI_COLORS['background']};
        border-radius: {UI_STYLES['border_radius']};
        padding: {UI_STYLES['padding']};
        margin-bottom: 15px;
        border: {UI_STYLES['border']};
        box-shadow: {UI_STYLES['shadow']};
    }}
    
    .tool-panel h3 {{
        color: {UI_COLORS['accent']};
        margin-bottom: 10px;
        font-size: 16px;
    }}
    
    .tool-panel h4 {{
        color: {UI_COLORS['secondary']};
        margin-bottom: 8px;
        font-size: 14px;
    }}
    
    /* Streamlitコンポーネントのスタイルオーバーライド */
    .stTextInput > div > div > input {{
        border-radius: 12px;
        border: 1px solid {UI_COLORS['accent']};
        background-color: #FAFAFA;
    }}
    
    .stButton > button {{
        border-radius: 12px;
        background-color: {UI_COLORS['accent']};
        color: white;
        border: none;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {UI_COLORS['secondary']};
    }}
    
    .stTextArea > div > div > textarea {{
        border-radius: 12px;
        border: 1px solid {UI_COLORS['accent']};
        background-color: #FAFAFA;
    }}
    
    /* タブスタイル */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {UI_COLORS['background']};
        border-radius: {UI_STYLES['border_radius']};
        padding: 8px;
        border: {UI_STYLES['border']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        background-color: transparent;
        color: {UI_COLORS['accent']};
        font-weight: bold;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {UI_COLORS['accent']};
        color: white;
    }}
    
    /* エキスパンダースタイル */
    .streamlit-expanderHeader {{
        background-color: {UI_COLORS['background']};
        border-radius: 12px;
        border: 1px solid {UI_COLORS['accent']};
    }}
    
    /* 日記エントリースタイル */
    .diary-entry {{
        background-color: #FAFAFA;
        border-radius: 12px;
        padding: 10px;
        margin: 5px 0;
        border-left: 4px solid {UI_COLORS['accent']};
    }}
    
    /* チャット入力コンテナ */
    .chat-input-container {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: {UI_COLORS['background']};
        padding: 15px;
        border-top: {UI_STYLES['border']};
        z-index: 999;
    }}
    
    /* レスポンシブデザイン */
    @media (max-width: 768px) {{
        .message-bubble {{
            max-width: 85%;
        }}
        
        .tool-panel {{
            padding: 10px;
        }}
    }}
    </style>
    """

def get_ui_consistency_prompt():
    """UIデザイン一貫性プロンプトを取得"""
    return f"""
[UIデザイン統一ルール - 絶対遵守]
アプリやUIコンポーネントを生成する際は、必ず以下のデザインシステムを適用すること：

1. カラーパレット（エゾモモンガ配色）：
   - 背景色: {UI_COLORS['background']} (ベージュ)
   - アクセント色: {UI_COLORS['accent']} (茶色)
   - 二次アクセント: {UI_COLORS['secondary']} (濃い茶色)
   - テキスト色: #333333
   - 白色: #FFFFFF

2. デザイン原則：
   - 角丸: {UI_STYLES['border_radius']}
   - パディング: {UI_STYLES['padding']}
   - ボーダー: {UI_STYLES['border']}
   - シャドウ: {UI_STYLES['shadow']}

3. Streamlitコンポーネントスタイル：
   ```css
   .stButton > button {{
       border-radius: 12px;
       background-color: {UI_COLORS['accent']};
       color: white;
       border: none;
       font-weight: bold;
   }}
   .stTextInput > div > div > input {{
       border-radius: 12px;
       border: 1px solid {UI_COLORS['accent']};
       background-color: #FAFAFA;
   }}
   ```

4. HTML/CSS生成時のテンプレート：
   ```html
   <div style="background-color: {UI_COLORS['background']}; border-radius: {UI_STYLES['border_radius']}; padding: {UI_STYLES['padding']}; border: {UI_STYLES['border']}; box-shadow: {UI_STYLES['shadow']};">
       <!-- コンテンツ -->
   </div>
   ```

[絶対命令]: どのようなアプリを生成する場合でも、上記のデザインルールを100%適用すること。これに違反するコードは生成してはならない。
"""

def apply_custom_css():
    """カスタムCSSを適用"""
    import streamlit as st
    st.markdown(get_line_chat_css(), unsafe_allow_html=True)

def get_tool_panel_style():
    """ツールパネルのスタイルを取得"""
    return f"""
    <div class="tool-panel">
        <div style="color: {UI_COLORS['accent']}; font-weight: bold; margin-bottom: 10px;">
            🛠️ AIアシスタント・ツール棚
        </div>
    </div>
    """
