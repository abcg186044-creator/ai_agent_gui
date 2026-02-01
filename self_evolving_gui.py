import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
from orchestrator_agent import OrchestratorAgent
from coder_agent import CoderAgent
from verification_system import VerificationProtocols

class SelfEvolvingInterface:
    """
    自己進化型マルチエージェントシステムのUIインターフェース
    Orchestratorとの対話のみを表示し、バックエンド処理を管理する
    """
    
    def __init__(self):
        # セッション状態の初期化
        self._init_session_state()
        
        # エージェントの初期化（セッション状態が確立してから）
        if "agents_initialized" not in st.session_state:
            self.orchestrator = OrchestratorAgent()
            self.coder = CoderAgent()
            self.verifier = VerificationProtocols()
            
            # Coderエージェントの監視を開始
            self.coder.start_monitoring()
            st.session_state.agents_initialized = True
        else:
            # 既存のエージェントを再利用
            self.orchestrator = st.session_state.get("orchestrator", OrchestratorAgent())
            self.coder = st.session_state.get("coder", CoderAgent())
            self.verifier = st.session_state.get("verifier", VerificationProtocols())
    
    def _init_session_state(self):
        """セッション状態を初期化"""
        if "evolution_messages" not in st.session_state:
            st.session_state.evolution_messages = []
        
        if "evolution_status" not in st.session_state:
            st.session_state.evolution_status = "idle"
        
        if "current_task" not in st.session_state:
            st.session_state.current_task = None
        
        if "clarification_mode" not in st.session_state:
            st.session_state.clarification_mode = False
        
        if "clarification_data" not in st.session_state:
            st.session_state.clarification_data = None
    
    def render_interface(self):
        """メインインターフェースを描画"""
        st.set_page_config(
            page_title="🤖 自己進化型AIエージェント",
            page_icon="🧬",
            layout="wide"
        )
        
        # ヘッダー
        self._render_header()
        
        # 進化ステータス表示
        self._render_evolution_status()
        
        # メインチャットエリア
        self._render_chat_interface()
        
        # 入力エリア
        self._render_input_area()
        
        # サイドバー情報
        self._render_sidebar()
    
    def _render_header(self):
        """ヘッダーを描画"""
        st.title("🧬 自己進化型AIエージェントシステム")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🤖 Orchestrator",
                "稼働中",
                "ユーザーとの対話を管理"
            )
        
        with col2:
            status = "🔄 進化中" if st.session_state.evolution_status == "evolving" else "⏸️ 待機中"
            st.metric(
                "👨‍💻 Coder",
                status,
                "バックエンドでシステム進化を実行"
            )
        
        with col3:
            # evolution_task.jsonの状態をチェック
            task_file = Path("evolution_task.json")
            if task_file.exists():
                with open(task_file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                task_status = task_data.get("status", "unknown")
                st.metric("📋 進化タスク", task_status)
            else:
                st.metric("📋 進化タスク", "なし")
    
    def _render_evolution_status(self):
        """進化ステータスを描画"""
        if st.session_state.evolution_status == "evolving":
            st.warning("⚙️ **システムを再構成中（自己進化中）...**")
            st.info("Coderエージェントがバックエンドでシステムを進化させています。完了までお待ちください...")
            
            # プログレスバー
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 進化状況を監視
            self._monitor_evolution_progress(progress_bar, status_text)
    
    def _monitor_evolution_progress(self, progress_bar, status_text):
        """進化進捗を監視"""
        task_file = Path("evolution_task.json")
        
        if task_file.exists():
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                
                status = task_data.get("status", "pending")
                
                if status == "pending":
                    progress_bar.progress(25)
                    status_text.text("📝 タスク解析中...")
                elif status == "in_progress":
                    progress_bar.progress(50)
                    status_text.text("🔧 コード編集中...")
                elif status == "verifying":
                    progress_bar.progress(75)
                    status_text.text("🔍 検証実行中...")
                elif status == "completed":
                    progress_bar.progress(100)
                    status_text.text("✅ 進化完了！")
                    st.session_state.evolution_status = "completed"
                    st.success("🎉 システムの進化が完了しました！")
                    time.sleep(2)
                    st.rerun()
                elif status == "failed":
                    st.session_state.evolution_status = "failed"
                    st.error("❌ 進化に失敗しました")
                    time.sleep(2)
                    st.rerun()
                
            except Exception:
                pass
    
    def _render_chat_interface(self):
        """チャットインターフェースを描画"""
        st.subheader("💬 Orchestratorとの対話")
        
        # メッセージ表示エリア
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.evolution_messages:
                self._render_message(message)
    
    def _render_message(self, message):
        """単一メッセージを描画"""
        if message["role"] == "user":
            st.markdown(f"👤 **ユーザー**: {message['content']}")
        elif message["role"] == "orchestrator":
            st.markdown(f"🤖 **Orchestrator**: {message['content']}")
        elif message["role"] == "system":
            if message["type"] == "clarification":
                st.info(f"❓ **確認**: {message['content']}")
            elif message["type"] == "confirmation":
                st.warning(f"🤔 **確認**: {message['content']}")
            elif message["type"] == "evolution":
                st.success(f"🧬 **進化**: {message['content']}")
        
        st.markdown("---")
    
    def _render_input_area(self):
        """入力エリアを描画"""
        st.subheader("📝 入力")
        
        # 確認モードの場合
        if st.session_state.clarification_mode:
            self._render_clarification_input()
        else:
            self._render_normal_input()
    
    def _render_clarification_input(self):
        """確認入力エリアを描画"""
        st.info("🔍 要件を明確にするため、いくつか質問にお答えください。")
        
        clarification_data = st.session_state.clarification_data
        responses = {}
        
        for i, question in enumerate(clarification_data.get("questions", []), 1):
            response = st.text_input(f"質問 {i}: {question}", key=f"clarification_{i}")
            responses[f"question_{i}"] = response
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ 回答を送信"):
                if all(responses.values()):
                    self._process_clarification_responses(responses)
                else:
                    st.warning("すべての質問に回答してください。")
        
        with col2:
            if st.button("❌ キャンセル"):
                st.session_state.clarification_mode = False
                st.session_state.clarification_data = None
                st.rerun()
    
    def _render_normal_input(self):
        """通常入力エリアを描画"""
        user_input = st.text_area(
            "システムへの指示や要望を入力してください...",
            height=100,
            key="user_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📤 送信", type="primary"):
                if user_input.strip():
                    self._process_user_input(user_input)
                else:
                    st.warning("入力が空です。")
        
        with col2:
            if st.button("🗑️ クリア"):
                st.session_state.evolution_messages = []
                st.rerun()
        
        with col3:
            # ヘルプテキスト
            st.markdown("""
            <small>
            💡 ヒント: 「機能を追加」「変更して」「新しい人格」などのキーワードで進化を開始できます
            </small>
            """, unsafe_allow_html=True)
    
    def _process_user_input(self, user_input):
        """ユーザー入力を処理"""
        # ユーザーメッセージを追加
        st.session_state.evolution_messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Orchestratorで入力を分析
        is_evolution, evolution_data = self.orchestrator.analyze_user_input(user_input)
        
        if is_evolution:
            # 進化要求の場合
            self._handle_evolution_request(evolution_data)
        else:
            # 通常の会話の場合
            self._handle_normal_conversation(user_input)
        
        st.rerun()
    
    def _handle_evolution_request(self, evolution_data):
        """進化要求を処理"""
        # 確認が必要かチェック
        if evolution_data.get("clarification_needed", False):
            # 確認モードに移行
            st.session_state.clarification_mode = True
            st.session_state.clarification_data = evolution_data
            
            # 確認メッセージを表示
            clarification_response = self.orchestrator.generate_clarification_response(
                evolution_data["clarification_questions"]
            )
            
            st.session_state.evolution_messages.append({
                "role": "system",
                "type": "clarification",
                "content": clarification_response,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # 確認メッセージを表示
            confirmation = self.orchestrator.generate_evolution_confirmation(evolution_data)
            
            st.session_state.evolution_messages.append({
                "role": "system",
                "type": "confirmation",
                "content": confirmation,
                "timestamp": datetime.now().isoformat()
            })
            
            # 自動で進化を開始（簡略化のため）
            self._start_evolution(evolution_data)
    
    def _handle_normal_conversation(self, user_input):
        """通常の会話を処理"""
        response = f"入力を理解しました: 「{user_input}」\n\n"
        response += "現在、私は自己進化型AIエージェントとしてシステムの改善・機能追加に特化しています。"
        response += "システムの進化に関するご要望がありましたら、「機能を追加」「変更して」"
        response += "「新しい人格」などのキーワードを含めてお話しください。"
        
        st.session_state.evolution_messages.append({
            "role": "orchestrator",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
    
    def _process_clarification_responses(self, responses):
        """確認回答を処理"""
        # 確認回答を元に進化データを更新
        st.session_state.clarification_mode = False
        st.session_state.clarification_data = None
        
        # 進化を開始
        if st.session_state.current_task:
            self._start_evolution(st.session_state.current_task)
        
        st.rerun()
    
    def _start_evolution(self, evolution_data):
        """進化を開始"""
        # 進化タスクを作成
        task_file = self.orchestrator.create_evolution_task(evolution_data)
        
        # ステータスを更新
        st.session_state.evolution_status = "evolving"
        st.session_state.current_task = evolution_data
        
        # 進化開始メッセージ
        st.session_state.evolution_messages.append({
            "role": "system",
            "type": "evolution",
            "content": f"🚀 進化を開始します: {evolution_data['requirements']['feature_description']}",
            "timestamp": datetime.now().isoformat()
        })
    
    def _render_sidebar(self):
        """サイドバーを描画"""
        with st.sidebar:
            st.header("🔧 システム情報")
            
            # エージェント状態
            st.subheader("🤖 エージェント状態")
            st.write("**Orchestrator**: アクティブ")
            st.write("**Coder**: 監視中")
            
            # 最近の進化履歴
            st.subheader("📜 最近の進化")
            
            backups_dir = Path("backups")
            if backups_dir.exists():
                backup_dirs = sorted([d for d in backups_dir.iterdir() if d.is_dir()], 
                                   key=lambda x: x.name, reverse=True)
                
                for backup_dir in backup_dirs[:5]:  # 最新5件
                    st.write(f"📁 {backup_dir.name}")
            else:
                st.write("進化履歴がありません")
            
            # システム設定
            st.subheader("⚙️ 設定")
            
            auto_evolution = st.checkbox(
                "自動進化モード",
                value=True,
                help="確認なしで自動的に進化を実行"
            )
            
            if st.button("🔄 システムを再起動"):
                st.info("システムを再起動します...")
                time.sleep(2)
                st.rerun()
            
            # 検証レポート
            st.subheader("🔍 検証レポート")
            
            if st.button("📊 検証を実行"):
                with st.spinner("検証中..."):
                    verification_result = self.verifier.verify_project()
                    report = self.verifier.generate_report(verification_result)
                    st.text_area("検証レポート", report, height=300)

def main():
    """メイン関数"""
    app = SelfEvolvingInterface()
    app.render_interface()

if __name__ == "__main__":
    main()
