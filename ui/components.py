"""
UIコンポーネントモジュール
チャット表示、ツール棚（TODO/メモ）の描画関数を管理
"""

import streamlit as st
import datetime
from collections import defaultdict
from ..core.constants import *
from ..core.llm_client import extract_todos_from_text
from ..services.state_manager import save_workspace_state, load_workspace_state, write_agent_diary, read_agent_diary, cleanup_temp_files
from ..services.app_generator import scan_generated_apps, execute_app_inline, self_repair_app
from .styles import get_tool_panel_style

def render_line_chat(conversation_history):
    """LINE風チャットUIを描画"""
    if not conversation_history:
        return
    
    # LINE風コンテナ
    st.markdown('<div class="line-chat-container">', unsafe_allow_html=True)
    
    for i, conv in enumerate(conversation_history):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        # ユーザーメッセージ
        st.markdown(f'''
        <div class="chat-message user-message">
            <div class="message-content">
                <div class="message-bubble user-bubble">
                    {conv["user"]}
                </div>
                <div class="message-time">
                    {timestamp}
                    <span class="read-indicator">既読</span>
                </div>
            </div>
            <div class="message-avatar user-avatar">👤</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # AIメッセージ（エゾモモンガ）
        st.markdown(f'''
        <div class="chat-message ai-message">
            <div class="message-avatar ai-avatar">🐿️</div>
            <div class="message-content">
                <div class="message-bubble ai-bubble">
                    {conv["assistant"]}
                </div>
                <div class="message-time">{timestamp}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 自動スクロール用JavaScript
    st.markdown("""
    <script>
    setTimeout(function() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
    </script>
    """, unsafe_allow_html=True)

def render_tool_panel():
    """ツール棚を描画"""
    # ツールパネルヘッダー
    st.markdown(get_tool_panel_style(), unsafe_allow_html=True)
    
    # ツール棚をtabsで整理
    tool_tabs = st.tabs(["📝 TODO", "📋 メモ", "🚀 アプリ", "📖 日記"])
    
    with tool_tabs[0]:
        render_todo_tab()
    
    with tool_tabs[1]:
        render_memo_tab()
    
    with tool_tabs[2]:
        render_apps_tab()
    
    with tool_tabs[3]:
        render_diary_tab()

def render_todo_tab():
    """TODOタブを描画"""
    st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
    st.markdown("#### 📝 TODOリスト")
    
    # TODOリストの初期化
    if SESSION_KEYS['todo_list'] not in st.session_state:
        st.session_state[SESSION_KEYS['todo_list']] = []
    
    # 新しいTODO追加
    new_todo = st.text_input("✏️ 新しいTODO", key="new_todo_input")
    if st.button("➕ 追加", key="add_todo"):
        if new_todo.strip():
            st.session_state[SESSION_KEYS['todo_list']].append({
                'task': new_todo.strip(),
                'completed': False,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("✅ TODOを追加しました")
            save_workspace_state()
            st.rerun()
    
    # TODOリスト表示
    if st.session_state[SESSION_KEYS['todo_list']]:
        for i, todo in enumerate(st.session_state[SESSION_KEYS['todo_list']]):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                completed = st.checkbox(todo['task'], key=f"todo_{i}", value=todo['completed'])
                if completed != todo['completed']:
                    st.session_state[SESSION_KEYS['todo_list']][i]['completed'] = completed
                    save_workspace_state()
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_todo_{i}"):
                    st.session_state[SESSION_KEYS['todo_list']].pop(i)
                    st.success("🗑️ TODOを削除しました")
                    save_workspace_state()
                    st.rerun()
            with col3:
                st.caption(todo['timestamp'])
    
    # 自動TODO検出機能
    st.markdown("#### 🤖 自動TODO検出")
    if st.button("🔍 会話からTODOを抽出", key="extract_todos"):
        if SESSION_KEYS['conversation_history'] in st.session_state and st.session_state[SESSION_KEYS['conversation_history']]:
            todos_extracted = []
            for conv in st.session_state[SESSION_KEYS['conversation_history']][-5:]:
                user_text = conv.get('user', '')
                if any(keyword in user_text for keyword in ['明日', 'する', 'やる']):
                    todos_extracted.append(user_text)
            
            if todos_extracted:
                for todo in todos_extracted:
                    st.session_state[SESSION_KEYS['todo_list']].append({
                        'task': f"[自動検出] {todo}",
                        'completed': False,
                        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                st.success(f"✅ {len(todos_extracted)}件のTODOを自動検出しました")
                save_workspace_state()
                st.rerun()
            else:
                st.info("📝 検出されたTODOはありませんでした")
        else:
            st.warning("⚠️ 会話履歴がありません")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_memo_tab():
    """メモタブを描画"""
    st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
    st.markdown("#### 📋 クイックメモ")
    
    # クイックメモの初期化
    if SESSION_KEYS['quick_memos'] not in st.session_state:
        st.session_state[SESSION_KEYS['quick_memos']] = []
    
    # 新しいメモ追加
    new_memo = st.text_area("📝 新しいメモ", key="new_memo_input", height=100)
    if st.button("💾 保存", key="save_memo"):
        if new_memo.strip():
            st.session_state[SESSION_KEYS['quick_memos']].append({
                'content': new_memo.strip(),
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'type': 'manual'
            })
            st.success("💾 メモを保存しました")
            save_workspace_state()
            st.rerun()
    
    # メモ一覧表示
    if st.session_state[SESSION_KEYS['quick_memos']]:
        for i, memo in enumerate(st.session_state[SESSION_KEYS['quick_memos']][-5:]):
            with st.expander(f"📋 {memo['timestamp']} - {memo['type']}", expanded=False):
                st.write(memo['content'])
                if st.button("🗑️ 削除", key=f"delete_memo_{i}"):
                    st.session_state[SESSION_KEYS['quick_memos']].pop(i)
                    st.success("🗑️ メモを削除しました")
                    save_workspace_state()
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_apps_tab():
    """アプリタブを描画"""
    st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
    st.markdown("#### 🚀 生成済みアプリ")
    
    # アプリをスキャン
    available_apps = scan_generated_apps()
    
    if available_apps:
        for app in available_apps:
            with st.expander(f"🚀 {app['name']}", expanded=False):
                # アプリ情報
                if app['description']:
                    st.caption(f"📝 {app['description']}")
                
                if app['functions']:
                    st.caption(f"🔧 関数: {', '.join(app['functions'])}")
                
                st.caption(f"📅 更新: {datetime.datetime.fromtimestamp(app['modified']).strftime('%Y-%m-%d %H:%M')}")
                
                # 起動ボタン
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🚀 起動", key=f"launch_{app['name']}"):
                        st.session_state[SESSION_KEYS['active_app']] = app
                        st.session_state[SESSION_KEYS['show_app_inline']] = True
                        st.success(f"🚀 {app['name']} を起動しました！")
                        st.rerun()
                
                with col2:
                    if st.button(f"📄 コード表示", key=f"show_code_{app['name']}"):
                        try:
                            with open(app['path'], 'r', encoding='utf-8') as f:
                                code_content = f.read()
                            st.code(code_content, language='python')
                        except Exception as e:
                            st.error(f"❌ コード読み込みエラー: {e}")
        
        # アプリインライン表示エリア
        if (SESSION_KEYS['show_app_inline'] in st.session_state and 
            st.session_state[SESSION_KEYS['show_app_inline']] and 
            SESSION_KEYS['active_app'] in st.session_state):
            render_inline_app()
    
    else:
        st.info("📝 生成済みアプリがありません。AIに「〇〇を作って」と依頼してみてください。")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_inline_app():
    """インラインアプリを描画"""
    st.markdown("---")
    st.markdown("#### 🎯 アプリ実行エリア")
    
    active_app = st.session_state[SESSION_KEYS['active_app']]
    
    # アプリ情報
    st.info(f"🚀 現在実行中: {active_app['name']}")
    
    # アプリを実行
    try:
        result = execute_app_inline(active_app['path'], active_app['name'])
        if isinstance(result, str):
            if "❌" in result:
                # エラーが発生した場合、自己修復を試みる
                st.error(f"⚠️ アプリ実行エラー: {result}")
                
                with st.spinner("🔧 自己修復中..."):
                    repair_success, repair_log = self_repair_app(
                        active_app['path'], 
                        active_app['name'], 
                        result
                    )
                    
                    if repair_success:
                        st.success("🔧 自己修復完了！")
                        for log in repair_log:
                            st.caption(f"• {log}")
                        
                        # 日記に記録
                        write_agent_diary(
                            "アプリ作成", 
                            f"{active_app['name']}の自己修復を実行: {', '.join(repair_log)}"
                        )
                        
                        # 再実行
                        try:
                            result = execute_app_inline(active_app['path'], active_app['name'])
                            st.write(result)
                            st.success("✅ 修復後のアプリを実行しました")
                        except Exception as e:
                            st.error(f"❌ 修復後もエラー: {e}")
                    else:
                        st.error("❌ 自己修復に失敗しました")
                        for log in repair_log:
                            st.caption(f"• {log}")
            else:
                st.write(result)
        else:
            # Streamlitコンポーネントの場合
            st.write("✅ アプリを起動しました")
            
            # 日記に記録
            write_agent_diary(
                "アプリ作成", 
                f"{active_app['name']}を正常に起動しました"
            )
    except Exception as e:
        st.error(f"❌ アプリ実行エラー: {e}")
        
        # 自己修復を試みる
        with st.spinner("🔧 自己修復中..."):
            repair_success, repair_log = self_repair_app(
                active_app['path'], 
                active_app['name'], 
                str(e)
            )
            
            if repair_success:
                st.success("🔧 自己修復完了！")
                write_agent_diary(
                    "アプリ作成", 
                    f"{active_app['name']}の自己修復を実行: {', '.join(repair_log)}"
                )
            else:
                st.error("❌ 自己修復に失敗しました")
    
    # 閉じるボタン
    if st.button("❌ アプリを閉じる", key="close_app"):
        st.session_state[SESSION_KEYS['show_app_inline']] = False
        st.session_state[SESSION_KEYS['active_app']] = None
        st.rerun()

def render_diary_tab():
    """日記タブを描画"""
    st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
    st.markdown("#### 📖 エージェント日記")
    
    # 日記エントリーの追加
    with st.expander("✍️ 今日の学びを記録", expanded=False):
        entry_type = st.selectbox("種類", ["学習", "アプリ作成", "ルール追加", "進化", "その他"])
        diary_content = st.text_area("内容", key="diary_content", height=100)
        
        if st.button("📝 日記に書く", key="write_diary"):
            if diary_content.strip():
                if write_agent_diary(entry_type, diary_content.strip()):
                    st.success("✅ 日記を書き込みました")
                    st.rerun()
                else:
                    st.error("❌ 日記の書き込みに失敗しました")
    
    # 日記一覧の表示
    diary_entries = read_agent_diary()
    
    if diary_entries:
        st.markdown("##### 📚 最近の日記")
        
        # 日付ごとにグループ化
        entries_by_date = defaultdict(list)
        for entry in diary_entries:
            entries_by_date[entry['date']].append(entry)
        
        # 最新の日付から表示
        for date in sorted(entries_by_date.keys(), reverse=True)[:7]:
            with st.expander(f"📅 {date}", expanded=False):
                for entry in entries_by_date[date]:
                    type_emoji = {
                        "学習": "📚",
                        "アプリ作成": "🚀", 
                        "ルール追加": "📜",
                        "進化": "🧬",
                        "その他": "📝"
                    }.get(entry['type'], "📝")
                    
                    st.markdown(f"""
                    <div class="diary-entry">
                        <strong>{type_emoji} {entry['type']}</strong> - {entry['timestamp'][-8:-3]}
                        <br>{entry['content']}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📝 日記がありません。今日の学びを記録しましょう！")
    
    # セルフメンテナンス
    st.markdown("##### 🧹 セルフメンテナンス")
    if st.button("🧹 一時ファイルを整理", key="cleanup_files"):
        with st.spinner("🧹 ファイルを整理中..."):
            cleanup_log = cleanup_temp_files()
            if cleanup_log:
                st.success(f"✅ {len(cleanup_log)}件のファイルを整理しました")
                for log in cleanup_log:
                    st.caption(f"• {log}")
            else:
                st.info("🧹 整理するファイルはありませんでした")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_vrm_controls(vrm_controller):
    """VRM制御パネルを描画"""
    st.markdown("### 🎭 VRMアバター制御")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👁️ 表示/非表示"):
            vrm_controller.toggle_visibility()
    
    with col2:
        scale = st.slider("📏 スケール", 0.1, 3.0, vrm_controller.vrm_scale)
        vrm_controller.set_scale(scale)
    
    with col3:
        rotation = st.slider("🔄 回転", 0, 360, vrm_controller.vrm_rotation)
        vrm_controller.set_rotation(rotation)
    
    # 表情選択
    expressions = ["neutral", "happy", "sad", "angry", "surprised"]
    selected_expression = st.selectbox("😊 表情", expressions, index=expressions.index(vrm_controller.vrm_expression))
    vrm_controller.set_expression(selected_expression)
    
    # ステータス表示
    status = vrm_controller.get_status()
    st.json(status)
