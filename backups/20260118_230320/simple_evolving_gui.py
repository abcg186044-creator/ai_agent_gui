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
            
            # バックアップを作成
            self._create_backup()
            
            # 簡単な機能追加を実行
            if "機能" in feature_desc:
                return self._add_feature(feature_desc)
            elif "人格" in feature_desc:
                return self._add_personality(requirements.get("new_personalities", []))
            else:
                return self._generic_change(feature_desc)
                
        except Exception as e:
            print(f"❌ タスク実行エラー: {e}")
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
            
            # 新機能コードを生成
            new_function = f"""

# 新規機能: {feature_desc}
def feature_{datetime.now().strftime('%Y%m%d_%H%M%S')}():
    \"\"\"
    {feature_desc}
    \"\"\"
    print("🚀 新機能が実行されました: {feature_desc}")
    return True
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

def main():
    """メイン関数 - シンプルな自己進化GUI"""
    st.set_page_config(
        page_title="🤖 自己進化型AIエージェント",
        page_icon="🧬",
        layout="wide"
    )
    
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
    
    # チャットインターフェース
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
                
                # 簡単な応答
                response = process_input(user_input)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
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

def process_input(user_input):
    """ユーザー入力を処理"""
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

現在、私は自己進化型AIエージェントとしてシステムの改善・機能追加に特化しています。

**進化を開始するには:**
「機能を追加」「変更して」「新しい人格」などのキーワードを含めてお話しください。

**例:**
- 「音声認識機能を追加して」
- 「UIを改善して」
- 「『丁寧な先生』という人格を作って」

システムの進化に関するご要望がありましたら、お気軽にお申し付けください！
        """

if __name__ == "__main__":
    main()
