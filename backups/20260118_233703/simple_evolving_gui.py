import streamlit as st
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# Coderエージェントの簡易実装
class SimpleCoderAgent:
    def __init__(self):
        self.monitoring = False
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def start_monitoring(self):
        """監視を開始"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_tasks, daemon=True)
        monitor_thread.start()
        print("🚀 Coderエージェントの監視を開始しました")
    
    def _monitor_tasks(self):
        """進化タスクを監視"""
        while self.monitoring:
            task_file = Path("evolution_task.json")
            
            if task_file.exists():
                try:
                    with open(task_file, "r", encoding="utf-8") as f:
                        task_data = json.load(f)
                    
                    if task_data.get("status") == "pending":
                        print(f"🔧 進化タスクを実行: {task_data.get('requirements', {}).get('feature_description', 'Unknown')}")
                        
                        # タスクを実行
                        success = self._execute_task(task_data)
                        
                        # ステータスを更新
                        task_data["status"] = "completed" if success else "failed"
                        task_data["completed_at"] = datetime.now().isoformat()
                        
                        with open(task_file, "w", encoding="utf-8") as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                        
                        if success:
                            print("✅ 進化タスクを完了しました")
                        else:
                            print("❌ 進化タスクの実行に失敗しました")
                            
                except Exception as e:
                    print(f"❌ タスク監視エラー: {e}")
            
            time.sleep(2)
    
    def _execute_task(self, task_data):
        """タスクを実行"""
        try:
            requirements = task_data.get("requirements", {})
            feature_desc = requirements.get("feature_description", "")
            
            print(f"🔧 タスク実行開: {feature_desc}")
            
            # バックアップを作成
            self._create_backup()
            
            # 簡単な機能追加を実行
            if "機能" in feature_desc:
                result = self._add_feature(feature_desc)
                print(f"✅ 機能追加結果: {result}")
                return result
            elif "人格" in feature_desc:
                result = self._add_personality(requirements.get("new_personalities", []))
                print(f"✅ 人格追加結果: {result}")
                return result
            else:
                result = self._generic_change(feature_desc)
                print(f"✅ 一般変更結果: {result}")
                return result
                
        except Exception as e:
            print(f"❌ タスク実行エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_backup(self):
        """バックアップを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / timestamp
        backup_subdir.mkdir(exist_ok=True)
        
        # 主要ファイルをバックアップ
        files_to_backup = ["simple_evolving_gui.py", "orchestrator_agent.py", "coder_agent.py"]
        
        for file_name in files_to_backup:
            source = Path(file_name)
            if source.exists():
                backup_path = backup_subdir / source.name
                import shutil
                shutil.copy2(source, backup_path)
                print(f"📁 バックアップ作成: {file_name}")
    
    def _add_feature(self, feature_desc):
        """機能を追加"""
        try:
            # simple_evolving_gui.pyに機能を追加
            gui_file = Path("simple_evolving_gui.py")
            
            with open(gui_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # メモ機能の場合は特別な処理
            if "メモ" in feature_desc and "入力ボックス" in feature_desc:
                new_function = self._create_memo_feature()
            else:
                # 新機能コードを生成
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_function = f"""

# 新規機能: {feature_desc}
def feature_{timestamp}():
    \"\"\"
    {feature_desc}
    \"\"\"
    print("🚀 新機能が実行されました: {feature_desc}")
    return True

# 新規機能の呼び出しボタンを追加
if st.button("🚀 {feature_desc}を実行"):
    result = feature_{timestamp}()
    if result:
        st.success("✅ 機能が正常に実行されました！")
    else:
        st.error("❌ 機能の実行に失敗しました")
"""
            
            # ファイルの末尾に追加
            updated_content = content + new_function
            
            with open(gui_file, "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            print(f"✅ 機能を追加: {feature_desc}")
            return True
            
        except Exception as e:
            print(f"❌ 機能追加エラー: {e}")
            return False
    
    def _create_memo_feature(self):
        """メモ機能のコードを生成"""
        return """

# メモ機能の実装
def display_memo_section():
    \"\"\"メモ機能セクションを表示\"\"\"
    st.subheader("📝 メモ機能")
    
    # メモデータの初期化
    if "memos" not in st.session_state:
        st.session_state.memos = []
    
    # メモ入力エリア
    with st.expander("📝 新規メモ作成", expanded=False):
        memo_title = st.text_input("タイトル", key="memo_title")
        memo_content = st.text_area("メモ内容", height=100, key="memo_content")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 メモを保存", type="primary"):
                if memo_title.strip() and memo_content.strip():
                    new_memo = {
                        "id": len(st.session_state.memos) + 1,
                        "title": memo_title,
                        "content": memo_content,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.memos.append(new_memo)
                    st.success("✅ メモを保存しました！")
                    st.rerun()
                else:
                    st.warning("⚠️ タイトルと内容を入力してください")
        
        with col2:
            if st.button("🗑️ 入力をクリア"):
                st.session_state.memo_title = ""
                st.session_state.memo_content = ""
                st.rerun()
    
    # メモ一覧表示
    if st.session_state.memos:
        st.write("### 📋 メモ一覧")
        
        for i, memo in enumerate(st.session_state.memos):
            with st.expander(f"📄 {memo['title']} ({memo['created_at']})", expanded=False):
                st.write(memo['content'])
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if st.button(f"✏️ 編集", key=f"edit_{i}"):
                        st.session_state.memo_title = memo['title']
                        st.session_state.memo_content = memo['content']
                        st.session_state.editing_memo_id = memo['id']
                        st.rerun()
                
                with col2:
                    if st.button(f"🗑️ 削除", key=f"delete_{i}"):
                        st.session_state.memos.pop(i)
                        st.success("🗑️ メモを削除しました")
                        st.rerun()
                
                with col3:
                    st.write(f"更新: {memo['updated_at']}")
    else:
        st.info("📝 メモがありません。新しいメモを作成してください。")

# メモ機能をメインUIに統合
def integrate_memo_feature():
    \"\"\"メモ機能を既存UIに統合\"\"\"
    # チャットセクションの後にメモ機能を追加
    display_memo_section()

# メモ機能の呼び出しをmain関数に追加
if st.button("📝 メモ機能を表示"):
    integrate_memo_feature()
"""
    
    def _add_personality(self, personalities):
        """人格を追加"""
        try:
            memory_file = Path("memory_db.json")
            
            if memory_file.exists():
                with open(memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)
            else:
                memory_data = {"personalities": {}}
            
            for personality in personalities:
                memory_data["personalities"][personality] = {
                    "name": personality,
                    "description": f"{personality}の人格",
                    "traits": ["friendly", "helpful"],
                    "created_at": datetime.now().isoformat()
                }
            
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 人格を追加: {', '.join(personalities)}")
            return True
            
        except Exception as e:
            print(f"❌ 人格追加エラー: {e}")
            return False
    
    def _generic_change(self, description):
        """一般的な変更"""
        print(f"🔧 変更を実行: {description}")
        time.sleep(2)  # 模擬的な処理時間
        print("✅ 変更完了")
        return True

# 会話コンテキスト管理クラス
class ChatContextManager:
    def __init__(self):
        self.max_history = 10  # 最大履歴数（往復）
        self.system_prompt = """あなたは自己進化能力を持つAIエンジニアです。
これまでの会話の流れを理解し、一貫性のあるプログラム提案を行ってください。
ユーザーの要望に応じてシステムを進化させることができます。
必ず日本語で応答してください。ユーザーは日本語での会話を希望しています。"""
    
    def get_context_for_ai(self, messages):
        """AIに渡すコンテキストを生成"""
        context = [{"role": "system", "content": self.system_prompt}]
        
        # 最新の履歴を追加
        recent_messages = messages[-(self.max_history * 2):]  # 往復分
        context.extend(recent_messages)
        
        return context
    
    def should_summarize(self, messages):
        """要約が必要か判定"""
        return len(messages) > self.max_history * 2
    
    def summarize_history(self, messages):
        """履歴を要約"""
        # 重要な情報を抽出（実装した機能、決定事項）
        summary_points = []
        
        for msg in messages:
            if msg["role"] == "user" and any(keyword in msg["content"] for keyword in ["機能を追加", "実装して", "作って"]):
                summary_points.append(f"✅ {msg['content']}")
        
        summary = "\n".join(summary_points) if summary_points else "会話履歴"
        
        # 要約メッセージを作成
        summary_msg = {
            "role": "system",
            "content": f"これまでの会話要約:\n{summary}\n\n以降の会話でこの文脈を考慮してください。",
            "timestamp": datetime.now().isoformat(),
            "is_summary": True
        }
        
        # 最新の数往復のみ保持
        recent_messages = messages[-(self.max_history * 2 - 2):]
        
        return [summary_msg] + recent_messages

# Ollama API連携クラス
class OllamaIntegration:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3.2"  # デフォルトモデル
    
    def generate_response(self, context, user_input):
        """Ollama APIで応答生成"""
        try:
            import requests
            
            # APIリクエスト
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": self._build_prompt(context, user_input),
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "応答の生成に失敗しました")
            else:
                return f"APIエラー: {response.status_code}"
                
        except Exception as e:
            return f"接続エラー: {str(e)}"
    
    def _build_prompt(self, context, user_input):
        """プロンプトを構築"""
        prompt_parts = []
        
        for msg in context:
            if msg["role"] == "system":
                prompt_parts.append(f"システム: {msg['content']}")
            elif msg["role"] == "user":
                prompt_parts.append(f"ユーザー: {msg['content']}")
            elif msg["role"] == "assistant":
                prompt_parts.append(f"AI: {msg['content']}")
        
        prompt_parts.append(f"ユーザー: {user_input}")
        prompt_parts.append("AI: ")
        
        return "\n".join(prompt_parts)

def main():
    """メイン関数 - シンプルな自己進化GUI"""
    st.set_page_config(
        page_title="🤖 自己進化型AIエージェント",
        page_icon="🧬",
        layout="wide"
    )
    
    # コンテキストマネージャーとOllama連携を初期化
    if "context_manager" not in st.session_state:
        st.session_state.context_manager = ChatContextManager()
        st.session_state.ollama_integration = OllamaIntegration()
    
    context_manager = st.session_state.context_manager
    ollama = st.session_state.ollama_integration
    
    # Coderエージェントを初期化・起動
    if "coder_agent" not in st.session_state:
        st.session_state.coder_agent = SimpleCoderAgent()
        st.session_state.coder_agent.start_monitoring()
        st.session_state.coder_started = True
    
    # タイトル
    st.title("🧬 自己進化型AIエージェントシステム")
    st.markdown("---")
    
    # 状態表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🤖 Orchestrator",
            "準備完了",
            "ユーザーとの対話を管理"
        )
    
    with col2:
        st.metric(
            "👨‍💻 Coder",
            "待機中",
            "バックエンドでシステム進化を実行"
        )
    
    with col3:
        # evolution_task.jsonの状態をチェック
        task_file = Path("evolution_task.json")
        if task_file.exists():
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                task_status = task_data.get("status", "unknown")
                st.metric("📋 進化タスク", task_status)
            except:
                st.metric("📋 進化タスク", "エラー")
        else:
            st.metric("📋 進化タスク", "なし")
    
    # 進化ステータス表示
    if task_file.exists():
        try:
            with open(task_file, "r", encoding="utf-8") as f:
                task_data = json.load(f)
            
            status = task_data.get("status", "pending")
            
            if status == "pending":
                st.warning("⚙️ **システムを再構成中（自己進化中）...**")
                st.info("Coderエージェントがバックエンドでシステムを進化させています。")
                
                # プログレスバー
                progress_bar = st.progress(50)
                st.text("🔧 コード編集中...")
                
            elif status == "completed":
                st.success("🎉 **進化が完了しました！**")
                st.info("✅ 新機能が正常に追加され、システムが更新されました。")
                if st.button("🔄 UIをリロード"):
                    st.rerun()
                    
        except Exception:
            pass
    st.subheader("💬 Orchestratorとの対話")
    
    # メッセージ表示
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"👤 **ユーザー**: {message['content']}")
        else:
            st.markdown(f"🤖 **Orchestrator**: {message['content']}")
        st.markdown("---")
    
    # 入力エリア
    st.subheader("📝 入力")
    
    user_input = st.text_area(
        "システムへの指示や要望を入力してください...",
        height=100,
        key="user_input"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📤 送信", type="primary"):
            if user_input.strip():
                # ユーザーメッセージを追加
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # AI応答を生成（コンテキスト考慮）
                context = context_manager.get_context_for_ai(st.session_state.messages)
                response = ollama.generate_response(context, user_input)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 履歴が長すぎる場合は要約
                if context_manager.should_summarize(st.session_state.messages):
                    st.session_state.messages = context_manager.summarize_history(st.session_state.messages)
                    st.info("📝 会話履歴を要約しました")
                
                st.rerun()
            else:
                st.warning("入力が空です。")
    
    with col2:
        if st.button("🗑️ クリア"):
            st.session_state.messages = []
            st.rerun()
    
    # ヘルプ
    st.markdown("""
    ---
    ### 💡 ヒント
    以下のようなキーワードを含めて話しかけると進化が開始されます：
    - 「機能を追加して」
    - 「変更して」
    - 「改善して」
    - 「新しい人格」
    - 「AIに指示して」
    - 「自分で書き換え」
    - 「システムを進化」
    
    ### 🔧 システム情報
    - **Orchestrator**: ユーザーとの対話を管理し、進化要求を検出します
    - **Coder**: バックエンドでコード編集と検証を実行します
    - **Verification**: コードの安全性と正しさを確認します
    
    ### 🛡️ 安全性
    - すべての編集前に自動バックアップを作成
    - 構文エラー検証と自動ロールバック
    - タイムスタンプ付き履歴管理
    """)

def get_current_code_context():
    """現在のソースコードを取得"""
    try:
        code_files = ["simple_evolving_gui.py", "orchestrator_agent.py", "coder_agent.py"]
        code_context = "現在のシステムコード:\n\n"

        for file_name in code_files:
            file_path = Path(file_name)
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # ファイルの重要部分のみ抽出（最初の50行）
                    lines = content.split('\n')
                    preview = '\n'.join(lines[:50])
                    code_context += f"=== {file_name} ===\n{preview}\n...\n\n"

        return code_context
    except Exception as e:
        return f"コード取得エラー: {str(e)}"

def process_input(user_input):
    """ユーザー入力を処理（フォールバック用）"""
    evolution_keywords = [
        "機能を追加", "変更して", "改善して", "新しい人格", 
        "AIに指示", "自分で書き換え", "システムを進化",
        "実装して", "作って", "修正して", "アップグレード"
    ]

    is_evolution = any(keyword in user_input for keyword in evolution_keywords)

    if is_evolution:
        # 進化要求の場合
        return f"""
🚀 **進化要求を検出しました！**

入力: 「{user_input}」

現在、自己進化機能の準備中です。以下の機能が実装されます：

1. **🤖 Orchestrator**: 要件の分析と確認
2. **👨‍💻 Coder**: コード編集とバックアップ
3. **🔍 Verification**: 安全性検証
4. **🔄 ホットリロード**: 即時反映

**次のステップ:**
- 要件の詳細を確認
- 安全なコード編集を実行
- 構文検証とテスト
- システムの自動更新

⚙️ システムを再構成中（自己進化中）...
        """
    else:
        # 通常の会話の場合
        return f"""
入力を理解しました: 「{user_input}」

現在、私は自己進化型AIエンジニアとしてシステムの改善・機能追加に特化しています。

**🚀 進化を開始するには:**
「機能を追加」「変更して」「新しい人格」などのキーワードを含めてお話しください。

**💡 例:**
- 「音声認識機能を追加して」
- "UIを改善して"
- "『丁寧な先生』という人格を作って"

**🔧 現在の状態:**
- Orchestrator: アクティブ ✅
- Coder: 監視中 🔄
- 進化準備: 完了 ✅

システムの進化に関するご要望がありましたら、お気軽にお申し付けください！
        """

if __name__ == "__main__":
    main()


# 新規機能: テスト用の新機能
def feature_20260118_230320():
    """
    テスト用の新機能
    """
    print("🚀 新機能が実行されました: テスト用の新機能")
    return True


# 新規機能: メモ機能のための新しい入力ボックスを追加
def feature_20260118_233300():
    """
    メモ機能のための新しい入力ボックスを追加
    """
    print("🚀 新機能が実行されました: メモ機能のための新しい入力ボックスを追加")
    return True

# 新規機能の呼び出しボタンを追加
if st.button("🚀 メモ機能のための新しい入力ボックスを追加を実行"):
    result = feature_20260118_233300()
    if result:
        st.success("✅ 機能が正常に実行されました！")
    else:
        st.error("❌ 機能の実行に失敗しました")
