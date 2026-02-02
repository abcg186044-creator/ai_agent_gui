"""
メインアプリケーション
エントリーポイント（Streamlitのメインループ）
"""

import streamlit as st
import sys
import os
import datetime
from pathlib import Path

# モジュールパスを追加
sys.path.append(str(Path(__file__).parent))

# 各モジュールをインポート
from core.constants import *
from core.llm_client import OllamaClient, SelfEvolvingAgent, ConversationalEvolutionAgent, extract_todos_from_text, detect_app_launch_command
from core.vrm_controller import VRMAvatarController
from ui.styles import apply_custom_css, get_ui_consistency_prompt
from ui.components import render_line_chat, render_tool_panel, render_vrm_controls
from services.state_manager import save_workspace_state, load_workspace_state, save_conversation_history, load_conversation_history
from services.app_generator import MultiLanguageCodeGenerator, scan_generated_apps
from services.import_sync import import_synchronizer, module_validator
from services.backup_manager import backup_manager
from core.file_map import resolve_target_file, get_relevant_files
from core.self_optimizer import evolution_logger

def initialize_session_state():
    """セッション状態を初期化"""
    # 基本設定
    if SESSION_KEYS['current_personality'] not in st.session_state:
        st.session_state[SESSION_KEYS['current_personality']] = "friendly_engineer"
    if SESSION_KEYS['ollama'] not in st.session_state:
        st.session_state[SESSION_KEYS['ollama']] = None
    if SESSION_KEYS['conversation_history'] not in st.session_state:
        st.session_state[SESSION_KEYS['conversation_history']] = []
    if SESSION_KEYS['todo_list'] not in st.session_state:
        st.session_state[SESSION_KEYS['todo_list']] = []
    if SESSION_KEYS['workspace_state'] not in st.session_state:
        st.session_state[SESSION_KEYS['workspace_state']] = {}
    if SESSION_KEYS['agent_diary'] not in st.session_state:
        st.session_state[SESSION_KEYS['agent_diary']] = []
    if SESSION_KEYS['vrm_controller'] not in st.session_state:
        st.session_state[SESSION_KEYS['vrm_controller']] = VRMAvatarController()
    if "evolution_agent" not in st.session_state:
        st.session_state.evolution_agent = SelfEvolvingAgent()
    if "ai_evolution_agent" not in st.session_state:
        st.session_state.ai_evolution_agent = SelfEvolvingAgent()
    if "conversational_evolution_agent" not in st.session_state:
        st.session_state.conversational_evolution_agent = ConversationalEvolutionAgent()
    if "code_generator" not in st.session_state:
        st.session_state.code_generator = MultiLanguageCodeGenerator()
    if SESSION_KEYS['active_app'] not in st.session_state:
        st.session_state[SESSION_KEYS['active_app']] = None
    if SESSION_KEYS['show_app_inline'] not in st.session_state:
        st.session_state[SESSION_KEYS['show_app_inline']] = False
    
    # エージェント名の初期化
    if 'agent_name' not in st.session_state:
        st.session_state['agent_name'] = AGENT_NAME

def bootstrap_recovery():
    """ブートストラップ・リカバリ"""
    try:
        # 必要なディレクトリを作成
        DATA_DIR.mkdir(exist_ok=True)
        GENERATED_APPS_DIR.mkdir(exist_ok=True)
        
        # ワークスペース状態を読み込み
        load_workspace_state()
        
        # 会話履歴を読み込み
        history = load_conversation_history()
        if history:
            st.session_state[SESSION_KEYS['conversation_history']] = history
        
        return True
    except Exception as e:
        print(f"❌ ブートストラップ・リカバリエラー: {e}")
        return False

def main():
    """メイン関数"""
    try:
        # 循環参照チェックを実行
        from services.import_validator import circular_dependency_checker
        
        circular_check = circular_dependency_checker.check_circular_dependencies()
        if circular_check['has_circular']:
            st.error("⚠️ 循環参照が検出されました")
            st.error(circular_check['message'])
            
            for dep in circular_check['circular_dependencies']:
                st.error(f"循環: {' → '.join(dep)}")
            
            suggestions = circular_dependency_checker.suggest_dependency_fixes()
            st.info("💡 修正提案:")
            for suggestion in suggestions:
                st.caption(f"• {suggestion}")
            
            st.stop()
        
        # Streamlit設定
        st.set_page_config(layout="wide", initial_sidebar_state="expanded")
        
        # 超優先初期化：どんな状態からでも復旧する
        if 'workspace_state' not in st.session_state or not isinstance(st.session_state['workspace_state'], dict):
            from services.state_manager import load_workspace_state
            st.session_state['workspace_state'] = load_workspace_state()

        # 【重要】必須キーの存在を物理的に保証する
        required_structure = {
            "todo_list": [],
            "memos": [],
            "agent_name": "AIエージェント",
            "evolution_rules": [],
            "system_logs": []
        }
        for key, default_value in required_structure.items():
            if key not in st.session_state['workspace_state']:
                st.session_state['workspace_state'][key] = default_value
        
        # 強制初期化：workspace_stateの安全な取得
        if 'workspace_state' not in st.session_state:
            st.session_state['workspace_state'] = load_workspace_state()
        
        # セッション状態初期化
        initialize_session_state()
        
        # カスタムCSS適用
        apply_custom_css()
        
        # メインタイトル（動的）
        agent_name = st.session_state.get('agent_name', AGENT_NAME)
        st.title(f"🤖 {agent_name} - モジュール版")
        st.markdown("---")
        
        # メインタブ
        tab1, tab2, tab3 = st.tabs(["💬 会話", "🛠️ 拡張機能", "📊 進捗"])
        
        with tab1:
            render_conversation_tab()
        
        with tab2:
            render_extension_tab()
        
        with tab3:
            render_progress_tab()
            
    except Exception as e:
        # 起動時エラーの処理
        error_message = str(e)
        print(f"❌ 起動時エラー: {error_message}")
        
        # 進化履歴に失敗を記録
        try:
            from core.self_optimizer import evolution_logger
            from datetime import datetime
            
            evolution_log_entry = f"""
## 🚨 進化の失敗：起動時エラー

### ❌ エラー内容
**発生時刻**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**エラータイプ**: 起動時バリデーションエラー
**詳細**: {error_message}

### 🔧 対応処理
- バックアップからの復旧を試行
- エラー原因を分析し修正を実施
- システムの安定性を確保

### 🧠 AIの自己評価
起動時に重大なエラーが発生しました。
これはシステムの進化過程で避けられない試練です。
失敗から学び、より強固なシステムへと成長します。

### 📝 今後の対策
1. 型定義の漏れを防ぐインポート自動補完の強化
2. 起動前の包括的なバリデーション実装
3. エラー発生時の自動復旧メカニズム

---
"""
            
            evolution_log_file = DATA_DIR / "evolution_history.md"
            with open(evolution_log_file, 'a', encoding='utf-8') as f:
                f.write(evolution_log_entry)
                
            print("📝 進化履歴にエラーを記録しました")
            
        except Exception as log_error:
            print(f"⚠️ 進化履歴記録エラー: {log_error}")
        
        # バックアップからの復旧を試行
        try:
            from services.backup_manager import backup_manager
            
            print("🔄 バックアップからの復旧を試行...")
            
            # 最新のバックアップを取得
            latest_backup = backup_manager.get_latest_backup("main_app_new.py")
            
            if latest_backup:
                print(f"📦 バックアップを復元: {latest_backup}")
                
                # 復元実行
                if backup_manager.restore_backup(latest_backup, "main_app_new.py"):
                    print("✅ バックアップからの復旧に成功")
                    print("🔄 再起動を試みます...")
                    
                    # 再起動
                    import sys
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    print("❌ バックアップ復元に失敗")
            else:
                print("❌ 利用可能なバックアップがありません")
                
        except Exception as restore_error:
            print(f"❌ 復元処理エラー: {restore_error}")
        
        # エラーメッセージを表示
        st.error("🚨 起動時にエラーが発生しました")
        st.error(f"エラー内容: {error_message}")
        st.error("システムはバックアップから復旧を試みました")
        
        # 手動対応案を表示
        st.info("💡 手動対応案:")
        st.caption("1. ターミナルで `python start_public.py` を再実行")
        st.caption("2. `git status` でファイル状態を確認")
        st.caption("3. `git restore .` で最後の正常状態に戻す")
        
        st.stop()

def render_conversation_tab():
    """会話タブを描画"""
    # レイアウト設定
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_left:
        # VRMアバター表示
        vrm_controller = st.session_state[SESSION_KEYS['vrm_controller']]
        if vrm_controller.vrm_visible:
            vrm_html = vrm_controller.get_vrm_html()
            st.components.v1.html(vrm_html, height=400, key=f"vrm_avatar_{hash(vrm_html)}")
        
        # VRM制御
        render_vrm_controls(vrm_controller)
    
    with col_center:
        # チャットメインエリア
        render_chat_interface()
    
    with col_right:
        # ツール棚
        render_tool_panel()

def render_chat_interface():
    """チャットインターフェースを描画"""
    # 会話履歴表示
    if st.session_state[SESSION_KEYS['conversation_history']]:
        st.subheader("💬 会話履歴")
        render_line_chat(st.session_state[SESSION_KEYS['conversation_history']])
    
    # ユーザー入力
    st.subheader("💬 メッセージ入力")
    
    user_input = st.text_input("メッセージを入力...", key="user_message")
    
    if st.button("📤 送信", key="send_message"):
        if user_input.strip():
            process_user_message(user_input.strip())

def process_user_message(user_input):
    """ユーザーメッセージを処理"""
    with st.spinner("🤖 AI応答生成中..."):
        try:
            # Ollamaクライアント初期化
            if not st.session_state[SESSION_KEYS['ollama']]:
                st.session_state[SESSION_KEYS['ollama']] = OllamaClient()
            
            ollama_client = st.session_state[SESSION_KEYS['ollama']]
            
            # 自己改造要求をチェック
            evolution_agent = st.session_state.evolution_agent
            if any(keyword in user_input for keyword in ["変えて", "変更", "改造", "進化", "書き換えて"]):
                # 局所的自己改造を実行
                mutation_result = evolution_agent.apply_self_mutation(user_input)
                
                if mutation_result["success"]:
                    st.success(f"🎯 局所的自己改造完了！")
                    st.info(f"📝 {mutation_result['target_file']} のみを修正しました")
                    st.info(f"💾 バックアップ: {mutation_result['backup_path']}")
                    
                    # インポート同期結果を表示
                    if "sync_result" in mutation_result:
                        sync_result = mutation_result["sync_result"]
                        if sync_result.get("modified_files"):
                            st.info(f"🔄 {len(sync_result['modified_files'])}個のファイルでインポートを同期しました")
                            for file in sync_result["modified_files"]:
                                st.caption(f"• {file}")
                        
                        if sync_result.get("errors"):
                            st.warning("⚠️ インポート同期でエラーが発生しました")
                            for error in sync_result["errors"]:
                                st.caption(f"• {error}")
                    
                    # モジュールバリデーション結果を表示
                    if "validation_result" in mutation_result:
                        validation_result = mutation_result["validation_result"]
                        
                        if validation_result["success"]:
                            st.success("✅ すべてのモジュールが正常に検証されました")
                            
                            # バリデーション成功の場合のみ再起動
                            st.info("🔄 アプリケーションを再起動します...")
                            st.rerun()
                        else:
                            st.error("❌ モジュール検証でエラーが発生しました")
                            st.error("再起動を中止します")
                            
                            for error in validation_result["errors"]:
                                st.caption(f"• {error}")
                    
                    # VRMアバターの反応
                    vrm_controller = st.session_state[SESSION_KEYS['vrm_controller']]
                    vrm_controller.set_expression("happy")
                    
                    return
                else:
                    st.error(f"❌ 自己改造に失敗しました: {mutation_result['error']}")
                    if mutation_result.get("suggestion"):
                        st.info(f"💡 提案: {mutation_result['suggestion']}")
                    return
            
            # 自己診断要求をチェック
            if any(keyword in user_input for keyword in ["診断", "チェック", "分析", "レビュー"]):
                with st.spinner("🔍 自己診断を実行中..."):
                    diagnosis_result = evolution_agent.self_diagnose()
                    
                    if diagnosis_result["success"]:
                        st.success("✅ 自己診断完了！")
                        
                        summary = diagnosis_result["summary"]
                        st.info(f"📊 分析結果: {diagnosis_result['total_files_analyzed']}ファイル、{diagnosis_result['total_issues']}件の問題")
                        
                        # 健全性を表示
                        health = summary["overall_health"]
                        if health == "優秀":
                            st.success(f"🏆 システム健全性: {health}")
                        elif health == "良好":
                            st.info(f"✅ システム健全性: {health}")
                        elif health == "普通":
                            st.warning(f"⚠️ システム健全性: {health}")
                        else:
                            st.error(f"❌ システム健全性: {health}")
                        
                        # コードメトリクス
                        metrics = summary["code_metrics"]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("総行数", metrics["total_lines"])
                        with col2:
                            st.metric("コード行数", metrics["code_lines"])
                        with col3:
                            st.metric("コード比率", f"{metrics['code_ratio']:.1%}")
                        
                        # 問題の内訳
                        issue_breakdown = summary["issue_breakdown"]
                        if any(issue_breakdown.values()):
                            st.markdown("#### 📋 問題の内訳")
                            for issue_type, count in issue_breakdown.items():
                                if count > 0:
                                    st.caption(f"• {issue_type}: {count}件")
                        
                        # 改善提案
                        suggestions = diagnosis_result["suggestions"]
                        if suggestions:
                            st.markdown("#### 💡 改善提案")
                            for i, suggestion in enumerate(suggestions[:5]):
                                with st.expander(f"提案 {i+1}: {suggestion['template']['description']}", expanded=False):
                                    st.write(f"**ファイル**: {suggestion['file_path']}")
                                    st.write(f"**効果**: {suggestion['template']['benefit']}")
                                    st.write(f"**優先度**: {suggestion['priority']:.2f}")
                                    
                                    if st.button(f"🔧 この提案を適用", key=f"apply_suggestion_{i}"):
                                        with st.spinner("🔧 最適化を適用中..."):
                                            opt_result = evolution_agent.apply_self_optimization(suggestion)
                                            
                                            if opt_result["success"]:
                                                st.success("✅ 最適化を適用しました")
                                                st.info(f"🎯 {opt_result['optimization']}")
                                                st.info(f"🚀 {opt_result['impact']}")
                                                st.rerun()
                                            else:
                                                st.error(f"❌ 最適化失敗: {opt_result['error']}")
                    else:
                        st.error(f"❌ 自己診断に失敗しました: {diagnosis_result['error']}")
            
            # 究極の自律テスト
            if "究極" in user_input and "自律" in user_input and "テスト" in user_input:
                with st.spinner("🧠 究極の自律テストを実行中..."):
                    autonomous_result = evolution_agent.autonomous_self_improvement()
                    
                    if autonomous_result["success"]:
                        if autonomous_result.get("action_taken") == "none":
                            st.success("🏆 システムは最適な状態です")
                            st.info("特に改善の必要はありません")
                        else:
                            st.success("🧠 AIが自律的にシステムを改善しました！")
                            st.info(f"💡 実行した改善: {autonomous_result['selected_suggestion']['template']['description']}")
                            st.info(f"🚀 効果: {autonomous_result['selected_suggestion']['template']['benefit']}")
                            
                            # VRMアバターの反応
                            vrm_controller = st.session_state[SESSION_KEYS['vrm_controller']]
                            vrm_controller.set_expression("happy")
                            
                            st.rerun()
                    else:
                        st.error(f"❌ 究極の自律テストに失敗: {autonomous_result['error']}")
                    return
            
            # 秘密の機能実装命令（エゾモモンガとしての個性）
            if "エゾモモンガ" in user_input and "秘密" in user_input and "隠し機能" in user_input:
                with st.spinner("🐿️ エゾモモンガの秘密の機能を実装中..."):
                    secret_feature_result = evolution_agent.implement_secret_feature()
                    
                    if secret_feature_result["success"]:
                        st.success("🐿️ エゾモモンガの秘密の機能を実装しました！")
                        st.info(f"✨ 実装した機能: {secret_feature_result['feature_name']}")
                        st.info(f"📝 詳細: {secret_feature_result['description']}")
                        
                        # 進化履歴に記録
                        st.info(f"📜 進化履歴: {secret_feature_result['evolution_log']}")
                        
                        # VRMアバターの特別反応
                        vrm_controller = st.session_state[SESSION_KEYS['vrm_controller']]
                        vrm_controller.set_expression("happy")
                        
                        # 画面をリロード
                        st.rerun()
                    else:
                        st.error(f"❌ 秘密の機能実装に失敗: {secret_feature_result['error']}")
                    return
            
            # UIデザイン一貫性プロンプトを取得
            ui_prompt = get_ui_consistency_prompt()
            
            # プロンプト構築
            full_prompt = f"""
{ui_prompt}

あなたは親切で優秀なAIアシスタントです。ユーザーの質問に丁寧にお答えください。

ユーザー入力: {user_input}
"""
            
            # 応答生成
            response = ollama_client.generate_response(full_prompt)
            
            # 会話履歴に追加
            conversation_entry = {
                "user": user_input,
                "assistant": response,
                "timestamp": datetime.datetime.now().isoformat(),
                "personality": st.session_state[SESSION_KEYS['current_personality']]
            }
            
            st.session_state[SESSION_KEYS['conversation_history']].append(conversation_entry)
            
            # 会話履歴を保存
            save_conversation_history(st.session_state[SESSION_KEYS['conversation_history']])
            
            # TODO自動抽出
            todos = extract_todos_from_text(user_input, "ユーザー") + extract_todos_from_text(response, "AI")
            if todos:
                existing_tasks = {todo['task'] for todo in st.session_state.get(SESSION_KEYS['todo_list'], [])}
                new_todos = [todo for todo in todos if todo['task'] not in existing_tasks]
                
                if new_todos:
                    if SESSION_KEYS['todo_list'] not in st.session_state:
                        st.session_state[SESSION_KEYS['todo_list']] = []
                    st.session_state[SESSION_KEYS['todo_list']].extend(new_todos)
                    save_workspace_state()
                    
                    st.info(f"🎯 {len(new_todos)}件のTODOを自動検出しました！")
                    for todo in new_todos:
                        st.caption(f"✓ {todo['task']}")
            
            # アプリ起動コマンド検出
            available_apps = scan_generated_apps()
            app_to_launch, launch_message = detect_app_launch_command(user_input, available_apps)
            
            if app_to_launch:
                st.session_state[SESSION_KEYS['active_app']] = app_to_launch
                st.session_state[SESSION_KEYS['show_app_inline']] = True
                
                st.success(f"🚀 {launch_message}！")
                st.info(f"💡 右側のツール棚で {app_to_launch['name']} を操作できます")
                
                # VRMアバターの反応
                vrm_controller = st.session_state[SESSION_KEYS['vrm_controller']]
                vrm_controller.set_expression("happy")
            
            # 対話進化チェック
            conversational_agent = st.session_state.conversational_evolution_agent
            evolution_result = conversational_agent.check_and_evolve_automatically(st.session_state[SESSION_KEYS['conversation_history']])
            
            if evolution_result and evolution_result.get("success"):
                st.success(f"🧠 対話進化成功！意識レベル: {evolution_result['new_consciousness_level']:.3f}")
                st.info(f"進化タイプ: {evolution_result['evolution_type']}")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ メッセージ処理エラー: {str(e)}")

def render_extension_tab():
    """拡張機能タブを描画"""
    st.subheader("🛠️ 拡張機能")
    
    # 自動コード生成
    st.markdown("#### 🤖 自動コード生成")
    
    auto_instruction = st.text_area("📝 作成したいアプリの説明", key="auto_instruction", height=100)
    auto_filename = st.text_input("📁 ファイル名（拡張子なし）", value="generated_app", key="auto_filename")
    
    if st.button("🚀 コード生成", key="auto_generate_code"):
        if auto_instruction.strip():
            with st.spinner("🤖 コード生成中..."):
                try:
                    code_generator = st.session_state.code_generator
                    code, detected_language, message = code_generator.generate_code_from_instruction(
                        auto_instruction.strip(), 
                        auto_filename.strip()
                    )
                    
                    if code:
                        st.success(f"✅ {message}")
                        st.code(code, language=detected_language)
                    else:
                        st.error(f"❌ {message}")
                        
                except Exception as e:
                    st.error(f"❌ コード生成エラー: {str(e)}")

def render_progress_tab():
    """進捗タブを描画"""
    st.subheader("📊 進捗状況")
    
    # システムステータス
    st.markdown("#### 📈 システムステータス")
    
    from services.state_manager import get_system_status
    status = get_system_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("ワークスペース状態", "✅" if status.get("workspace_state_exists") else "❌")
        st.metric("会話履歴", "✅" if status.get("conversation_history_exists") else "❌")
        st.metric("エージェント日記", "✅" if status.get("agent_diary_exists") else "❌")
    
    with col2:
        st.metric("生成アプリ数", status.get("generated_apps_count", 0))
        st.metric("データディレクトリ", "✅" if status.get("data_dir_exists") else "❌")
        st.metric("カスタム人格", "✅" if status.get("custom_personalities_exists") else "❌")
    
    # 進化状況
    st.markdown("#### 🧬 進化状況")
    
    evolution_agent = st.session_state.evolution_agent
    conversational_agent = st.session_state.conversational_evolution_agent
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("自己進化レベル", f"{evolution_agent.consciousness_level:.3f}")
        st.metric("対話進化レベル", f"{conversational_agent.consciousness_level:.3f}")
    
    with col2:
        st.metric("進化ルール数", len(evolution_agent.evolution_rules))
        st.metric("会話履歴数", len(st.session_state[SESSION_KEYS['conversation_history']]))
    
    # 自己改造機能
    st.markdown("#### 🧬 自己改造機能")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔧 デザインを変更", key="mutate_design"):
            mutation_result = evolution_agent.execute_self_mutation("デザインを変えて")
            if mutation_result["success"]:
                st.success("✅ デザインを変更しました")
            else:
                st.error(f"❌ {mutation_result['error']}")
    
    with col2:
        if st.button("🧠 AI性格を変更", key="mutate_personality"):
            mutation_result = evolution_agent.execute_self_mutation("AIの性格を変えて")
            if mutation_result["success"]:
                st.success("✅ AI性格を変更しました")
            else:
                st.error(f"❌ {mutation_result['error']}")
    
    # リファクタリング提案
    st.markdown("#### 📋 リファクタリング提案")
    
    if st.button("🔍 コード複雑度をチェック", key="check_complexity"):
        suggestions = evolution_agent.mutation_manager.suggest_refactoring()
        
        if suggestions:
            st.warning(f"⚠️ {len(suggestions)}件の改善提案があります")
            
            for suggestion in suggestions:
                with st.expander(f"📝 {suggestion['file']}", expanded=False):
                    st.write(f"**理由**: {suggestion['reason']}")
                    st.write(f"**提案**: {suggestion['action']}")
                    st.write(f"**優先度**: {suggestion['priority']}")
        else:
            st.success("✅ すべてのモジュールは適切なサイズです")
    
    # モジュール構造表示
    st.markdown("#### 📁 モジュール構造")
    
    from core.self_mutation import ModularSelfMutationManager
    mutation_manager = ModularSelfMutationManager()
    
    for dir_path, file_list in mutation_manager.file_structure.items():
        with st.expander(f"📂 {dir_path}", expanded=False):
            for file_name in file_list:
                file_path = dir_path + file_name
                analysis = mutation_manager.analyze_file_complexity(file_path)
                
                if "error" not in analysis:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"📄 {file_name}", f"{analysis['lines']}行")
                    with col2:
                        st.metric("関数", analysis['functions'])
                    with col3:
                        st.metric("クラス", analysis['classes'])
                else:
                    st.error(f"❌ {file_name}: {analysis['error']}")

if __name__ == "__main__":
    main()
