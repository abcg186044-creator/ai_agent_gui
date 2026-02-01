#!/usr/bin/env python3
"""
Web Canvas プレビューシステム
AIと共同作業するリアルタイムWeb開発環境
"""

import streamlit as st
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import hashlib
import base64
import re
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp

class CanvasState(Enum):
    """Canvas状態"""
    IDLE = "idle"
    LOADING = "loading"
    RUNNING = "running"
    ERROR = "error"
    DEBUGGING = "debugging"

@dataclass
class ConsoleMessage:
    """コンソールメッセージ"""
    timestamp: datetime
    level: str  # log, warn, error, info
    message: str
    source: str = "canvas"

@dataclass
class CanvasProject:
    """Canvasプロジェクト"""
    name: str
    html_content: str = ""
    css_content: str = ""
    js_content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    version: int = 1
    screenshot: Optional[str] = None  # base64 encoded

class WebCanvasPreview:
    """Web Canvas プレビューシステム"""
    
    def __init__(self):
        self.name = "web_canvas_preview"
        self.description = "AIと共同作業するリアルタイムWeb開発環境"
        
        # プロジェクト管理
        self.current_project = None
        self.projects = {}
        
        # 状態管理
        self.canvas_state = CanvasState.IDLE
        self.console_messages = []
        self.error_logs = []
        
        # ファイル監視
        self.file_watcher_active = False
        self.last_file_hashes = {}
        
        # AI対話キュー
        self.ai_suggestions = queue.Queue()
        self.user_feedback = queue.Queue()
        
        # コンソール出力キュー
        self.console_queue = queue.Queue()
        
        # スクリーンショット機能
        self.screenshot_enabled = True
        
        # 初期化
        self._initialize_default_project()
    
    def _initialize_default_project(self):
        """デフォルトプロジェクトを初期化"""
        default_project = CanvasProject(
            name="default",
            html_content="""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canvas Preview</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        .status {
            color: #666;
            font-size: 1.1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Web Canvas Preview</h1>
        <p class="status">AIと共同作業するWeb開発環境</p>
        <p>コードを書いて、リアルタイムでプレビューしましょう！</p>
    </div>
</body>
</html>""",
            css_content="",
            js_content="// AIとの共同作業を開始しましょう！\nconsole.log('Canvas Preview Ready!');"
        )
        
        self.current_project = default_project
        self.projects["default"] = default_project
    
    def create_project(self, name: str) -> CanvasProject:
        """新しいプロジェクトを作成"""
        project = CanvasProject(name=name)
        self.projects[name] = project
        self.current_project = project
        return project
    
    def update_project_file(self, file_type: str, content: str) -> bool:
        """プロジェクトファイルを更新"""
        if not self.current_project:
            return False
        
        # ファイル内容を更新
        if file_type == "html":
            self.current_project.html_content = content
        elif file_type == "css":
            self.current_project.css_content = content
        elif file_type == "js":
            self.current_project.js_content = content
        else:
            return False
        
        # 更新時刻を記録
        self.current_project.last_modified = datetime.now()
        self.current_project.version += 1
        
        # コンソールメッセージを追加
        self._add_console_message("info", f"{file_type.upper()}ファイルを更新しました (バージョン {self.current_project.version})")
        
        return True
    
    def get_combined_html(self) -> str:
        """結合されたHTMLを取得"""
        if not self.current_project:
            return ""
        
        html = self.current_project.html_content
        
        # CSSを挿入
        if self.current_project.css_content:
            css_tag = f"<style>\n{self.current_project.css_content}\n</style>"
            if "</head>" in html:
                html = html.replace("</head>", f"{css_tag}\n</head>")
            else:
                html = f"{css_tag}\n{html}"
        
        # JavaScriptを挿入
        if self.current_project.js_content:
            js_tag = f"<script>\n{self.current_project.js_content}\n</script>"
            if "</body>" in html:
                html = html.replace("</body>", f"{js_tag}\n</body>")
            else:
                html = f"{html}\n{js_tag}"
        
        # エラーハンドリングとコンソールキャプチャを追加
        error_handling_script = """
<script>
// エラーハンドリング
window.addEventListener('error', function(e) {
    parent.postMessage({
        type: 'canvas_error',
        error: {
            message: e.message,
            filename: e.filename,
            lineno: e.lineno,
            colno: e.colno,
            stack: e.error ? e.error.stack : ''
        }
    }, '*');
});

// コンソールキャプチャ
const originalLog = console.log;
const originalWarn = console.warn;
const originalError = console.error;
const originalInfo = console.info;

function sendToParent(level, ...args) {
    parent.postMessage({
        type: 'console_message',
        level: level,
        message: args.map(arg => {
            if (typeof arg === 'object') {
                try {
                    return JSON.stringify(arg);
                } catch(e) {
                    return String(arg);
                }
            }
            return String(arg);
        }).join(' ')
    }, '*');
}

console.log = function(...args) {
    originalLog.apply(console, args);
    sendToParent('log', ...args);
};

console.warn = function(...args) {
    originalWarn.apply(console, args);
    sendToParent('warn', ...args);
};

console.error = function(...args) {
    originalError.apply(console, args);
    sendToParent('error', ...args);
};

console.info = function(...args) {
    originalInfo.apply(console, args);
    sendToParent('info', ...args);
};

// 準備完了を通知
parent.postMessage({type: 'canvas_ready'}, '*');
</script>
"""
        
        if "</body>" in html:
            html = html.replace("</body>", f"{error_handling_script}\n</body>")
        else:
            html = f"{html}\n{error_handling_script}"
        
        return html
    
    def _add_console_message(self, level: str, message: str, source: str = "canvas"):
        """コンソールメッセージを追加"""
        console_msg = ConsoleMessage(
            timestamp=datetime.now(),
            level=level,
            message=message,
            source=source
        )
        
        self.console_messages.append(console_msg)
        
        # メッセージ数を制限
        if len(self.console_messages) > 100:
            self.console_messages = self.console_messages[-50:]
    
    def handle_canvas_message(self, message_data: Dict):
        """Canvasからのメッセージを処理"""
        if message_data.get('type') == 'console_message':
            self._add_console_message(
                message_data.get('level', 'log'),
                message_data.get('message', ''),
                'canvas'
            )
        
        elif message_data.get('type') == 'canvas_error':
            error_info = message_data.get('error', {})
            self._add_console_message('error', f"JavaScriptエラー: {error_info.get('message', 'Unknown error')}")
            self.error_logs.append({
                'timestamp': datetime.now(),
                'error': error_info
            })
        
        elif message_data.get('type') == 'canvas_ready':
            self.canvas_state = CanvasState.RUNNING
            self._add_console_message('info', 'Canvas準備完了')
    
    def capture_screenshot(self) -> Optional[str]:
        """スクリーンショットをキャプチャ"""
        if not self.screenshot_enabled:
            return None
        
        # 実際のスクリーンショット取得はJavaScript側で実行
        screenshot_script = """
<script>
// html2canvasライブラリを使用してスクリーンショットを取得
if (typeof html2canvas !== 'undefined') {
    html2canvas(document.body).then(canvas => {
        canvas.toBlob(function(blob) {
            const reader = new FileReader();
            reader.onloadend = function() {
                parent.postMessage({
                    type: 'canvas_screenshot',
                    screenshot: reader.result
                }, '*');
            };
            reader.readAsDataURL(blob);
        });
    }).catch(function(error) {
        parent.postMessage({
            type: 'canvas_screenshot_error',
            error: error.message
        }, '*');
    });
} else {
    parent.postMessage({
        type: 'canvas_screenshot_error',
        error: 'html2canvasライブラリが読み込まれていません'
    }, '*');
}
</script>
"""
        
        return screenshot_script
    
    def handle_screenshot(self, screenshot_data: str):
        """スクリーンショットデータを処理"""
        if self.current_project:
            self.current_project.screenshot = screenshot_data
            self._add_console_message('info', 'スクリーンショットをキャプチャしました')
    
    def update_personality(self, personality: str):
        """人格を更新"""
        if personality in ["friend", "copy", "expert"]:
            self.current_personality = personality
            
            # Canvasに人格変更を通知
            if self.canvas_state == CanvasState.RUNNING:
                # JavaScript経由で人格変更を通知
                personality_script = f"""
<script>
if (window.parent && window.parent.postMessage) {{
    window.parent.postMessage({{
        type: 'personality_change',
        personality: '{personality}'
    }}, '*');
}}
</script>
"""
                # スクリプトを実行して人格変更を通知
                self._add_console_message("info", f"人格を{personality}に変更しました")
            
            return True
        return False
    
    def get_console_logs(self, level_filter: Optional[str] = None) -> List[ConsoleMessage]:
        """コンソールログを取得"""
        if level_filter:
            return [msg for msg in self.console_messages if msg.level == level_filter]
        return self.console_messages

class CanvasPreviewGUI:
    """CanvasプレビューGUI"""

    def __init__(self, canvas_preview: WebCanvasPreview):
        self.canvas_preview = canvas_preview

    def render(self):
        """GUIを描画"""
        st.subheader("🎨 Web Canvas プレビュー")

        # プロジェクト情報
        stats = self.canvas_preview.get_project_stats()

        # ステータス表示
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "プロジェクト",
                stats.get('project_name', 'None'),
                help="現在のプロジェクト名"
            )

        with col2:
            st.metric(
                "バージョン",
                stats.get('version', 0),
                help="プロジェクトのバージョン"
            )

        with col3:
            st.metric(
                "コンソール",
                stats.get('console_messages', 0),
                help="コンソールメッセージ数"
            )

        with col4:
            state_emoji = {
                'idle': '⏸️',
                'loading': '⏳',
                'running': '▶️',
                'error': '❌',
                'debugging': '🔧'
            }
            st.metric(
                "状態",
                f"{state_emoji.get(stats.get('canvas_state', 'idle'), '⏸️')} {stats.get('canvas_state', 'idle').title()}",
                help="Canvasの現在の状態"
            )

        # メインレイアウト
        col1, col2 = st.columns([1, 1])

        with col1:
            self._render_code_editor()

        with col2:
            self._render_canvas_preview()

        # コンソールログ
        self._render_console_logs()

        # AI対話
        self._render_ai_dialogue()

    def _render_code_editor(self):
        """コードエディターを描画"""
        st.write("**📝 コードエディター**")

        if not self.canvas_preview.current_project:
            st.warning("プロジェクトが選択されていません")
            return

        project = self.canvas_preview.current_project

        # ファイル選択
        file_type = st.selectbox(
            "ファイルタイプ",
            ["html", "css", "js"],
            format_func=lambda x: x.upper()
        )

        # コードエディター
        if file_type == "html":
            content = st.text_area(
                "HTMLコード",
                value=project.html_content,
                height=300,
                key="html_editor"
            )
        elif file_type == "css":
            content = st.text_area(
                "CSSコード",
                value=project.css_content,
                height=300,
                key="css_editor"
            )
        else:  # js
            content = st.text_area(
                "JavaScriptコード",
                value=project.js_content,
                height=300,
                key="js_editor"
            )

        # 更新ボタン
        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 更新", type="primary"):
                if self.canvas_preview.update_project_file(file_type, content):
                    st.success(f"✅ {file_type.upper()}ファイルを更新しました")
                    st.rerun()
                else:
                    st.error("❌ 更新に失敗しました")

        with col2:
            if st.button("🔄 リロード"):
                st.rerun()

        # プロジェクト操作
        st.write("**🗂️ プロジェクト操作**")

        col1, col2, col3 = st.columns(3)

        with col1:
            new_project_name = st.text_input("新規プロジェクト名", key="new_project")
            if st.button("➕ 作成") and new_project_name:
                self.canvas_preview.create_project(new_project_name)
                st.success(f"✅ プロジェクト '{new_project_name}' を作成しました")
                st.rerun()

        with col2:
            if st.button("📋 統計"):
                st.json(self.canvas_preview.get_project_stats())

        with col3:
            if st.button("🗑️ コンソールクリア"):
                self.canvas_preview.clear_console()
                st.success("✅ コンソールをクリアしました")
                st.rerun()

    def _render_canvas_preview(self):
        """Canvasプレビューを描画"""
        st.write("**🖼️ Canvas プレビュー**")

        if not self.canvas_preview.current_project:
            st.warning("プロジェクトが選択されていません")
            return

        # HTMLを取得
        html_content = self.canvas_preview.get_combined_html()

        # Canvasプレビュー
        components.html(
            html_content,
            height=500,
            scrolling=True
        )

        # スクリーンショットボタン
        if st.button("📸 スクリーンショット"):
            screenshot_script = self.canvas_preview.capture_screenshot()
            if screenshot_script:
                st.components.v1.html(screenshot_script, height=0)

        # プレビュー制御
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 強制リロード"):
                st.rerun()

        with col2:
            if st.button("🔍 デバッグモード"):
                self.canvas_preview.canvas_state = CanvasState.DEBUGGING
                st.info("🔧 デバッグモードを有効にしました")

    def _render_console_logs(self):
        """コンソールログを描画"""
        st.write("**📋 コンソールログ**")

        # フィルター
        col1, col2 = st.columns(2)

        with col1:
            log_filter = st.selectbox(
                "ログレベル",
                ["すべて", "log", "warn", "error", "info"],
                key="console_filter"
            )

        with col2:
            auto_scroll = st.checkbox("自動スクロール", value=True, key="auto_scroll")

        # ログ表示
        logs = self.canvas_preview.get_console_logs()

        if log_filter != "すべて":
            logs = [log for log in logs if log.level == log_filter]

        if logs:
            # 最新のログから表示
            display_logs = logs[-20:] if auto_scroll else logs

            for log in display_logs:
                level_emoji = {
                    'log': '📝',
                    'warn': '⚠️',
                    'error': '❌',
                    'info': 'ℹ️'
                }

                level_color = {
                    'log': 'blue',
                    'warn': 'orange',
                    'error': 'red',
                    'info': 'green'
                }

                st.markdown(
                    f"{level_emoji.get(log.level, '📝')} "
                    f"`{log.timestamp.strftime('%H:%M:%S')}` "
                    f"<span style='color: {level_color.get(log.level, 'black')}'>"
                    f"[{log.level.upper()}]</span> "
                    f"{log.message}",
                    unsafe_allow_html=True
                )
        else:
            st.info("コンソールログがありません")

    def _render_ai_dialogue(self):
        """AI対話を描画"""
        st.write("**🤖 AI対話**")

        # AI提案の表示
        ai_suggestions = self.canvas_preview.get_ai_suggestions()

        if ai_suggestions:
            st.write("**AIからの提案:**")
            for suggestion in ai_suggestions:
                st.info(f"💡 {suggestion}")

        # ユーザーフィードバック
        user_feedback = st.text_area(
            "AIへのフィードバック",
            placeholder="例：背景を赤に変えて、もう少し明るくして",
            key="user_feedback"
        )

        if st.button("📤 フィードバックを送信") and user_feedback:
            self.canvas_preview.user_feedback.put(user_feedback)
            st.success("✅ フィードバックを送信しました")
            st.rerun()

        # AI提案の追加
        ai_suggestion = st.text_area(
            "AI提案を追加",
            placeholder="例：Canvasの背景を青に変えてみたよ。どうかな？",
            key="ai_suggestion"
        )

        if st.button("💡 AI提案を追加") and ai_suggestion:
            self.canvas_preview.add_ai_suggestion(ai_suggestion)
            st.success("✅ AI提案を追加しました")
            st.rerun()

# メイン関数
def create_web_canvas_gui(canvas_preview: WebCanvasPreview):
    """Web Canvas GUIを作成"""
    gui = CanvasPreviewGUI(canvas_preview)
    gui.render()
