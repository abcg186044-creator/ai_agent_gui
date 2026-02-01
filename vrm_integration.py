#!/usr/bin/env python3
"""
VRMアバター統合コンポーネント
StreamlitとThree.js VRMの連携
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import threading

class VRMIntegration:
    def __init__(self):
        self.name = "vrm_integration"
        self.description = "VRMアバターとAIエージェントの連携システム"
        
        # VRMコンポーネントの状態
        self.current_motion = "idle"
        self.is_speaking = False
        self.current_emotion = "neutral"
        
        # VRMファイルパス
        self.vrm_file_path = "avatar.vrm"
        
        # コンポーネントの高さ
        self.component_height = 400
        
        # JavaScriptとの通信
        self.js_queue = []
        
        # モーション履歴
        self.motion_history = []
    
    def render_vrm_component(self, vrm_file: str = "avatar.vrm", height: int = 400) -> str:
        """VRMコンポーネントをStreamlitに描画"""
        self.vrm_file_path = vrm_file
        self.component_height = height
        
        # HTMLファイルのパス
        html_path = Path(__file__).parent / "vrm_component.html"
        
        if not html_path.exists():
            st.error("VRMコンポーネントHTMLファイルが見つかりません")
            return ""
        
        # HTMLファイルを読み込み
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # VRMファイルパスを動的に設定
        html_content = html_content.replace(
            "const vrmPath = window.location.search.includes('vrm=')",
            f"const vrmPath = '{vrm_file}'"
        )
        
        # コンポーネントを埋め込み
        component = components.html(
            html_content,
            height=height,
            scrolling=False
        )
        
        return component
    
    def send_message_to_vrm(self, message_type: str, data: Any) -> bool:
        """VRMコンポーネントにメッセージを送信"""
        try:
            message = {
                "type": message_type,
                "data": data,
                "timestamp": time.time()
            }
            
            # JavaScriptにメッセージを送信
            js_code = f"""
            <script>
                window.parent.postMessage({json.dumps(message)}, '*');
            </script>
            """
            
            components.html(js_code, height=0)
            
            # 履歴に記録
            self.motion_history.append({
                "timestamp": time.time(),
                "type": message_type,
                "data": data
            })
            
            return True
            
        except Exception as e:
            st.error(f"VRMメッセージ送信エラー: {str(e)}")
            return False
    
    def set_motion(self, motion: str) -> bool:
        """モーションを設定"""
        valid_motions = ["idle", "thinking", "speaking", "working", "greeting", "listening", "nodding", "aizuchi"]
        
        if motion not in valid_motions:
            st.warning(f"無効なモーション: {motion}")
            return False
        
        self.current_motion = motion
        return self.send_message_to_vrm("motion", {"motion": motion})
    
    def set_aizuchi_motion(self, emotion: str = "neutral") -> bool:
        """相槌モーションを感情付きで設定"""
        self.current_motion = "aizuchi"
        return self.send_message_to_vrm("motion", {"motion": "aizuchi", "emotion": emotion})
    
    def set_speaking(self, speaking: bool) -> bool:
        """話す状態を設定"""
        self.is_speaking = speaking
        return self.send_message_to_vrm("speech", {"speaking": speaking})
    
    def set_emotion(self, emotion: str) -> bool:
        """感情を設定"""
        valid_emotions = ["neutral", "happy", "sad", "angry", "surprised", "joy"]
        
        if emotion not in valid_emotions:
            st.warning(f"無効な感情: {emotion}")
            return False
        
        self.current_emotion = emotion
        return self.send_message_to_vrm("emotion", {"emotion": emotion})
    
    def load_vrm_file(self, vrm_path: str) -> bool:
        """VRMファイルをロード"""
        if not Path(vrm_path).exists():
            st.error(f"VRMファイルが見つかりません: {vrm_path}")
            return False
        
        self.vrm_file_path = vrm_path
        return self.send_message_to_vrm("load_vrm", {"vrm_path": vrm_path})
    
    def sync_with_ai_state(self, ai_state: Dict[str, Any]) -> bool:
        """AIの状態と同期"""
        try:
            # 思考状態
            if ai_state.get("is_thinking"):
                self.set_motion("thinking")
            elif ai_state.get("is_speaking"):
                self.set_motion("speaking")
            elif ai_state.get("is_working"):
                self.set_motion("working")
            else:
                self.set_motion("idle")
            
            # 話す状態
            if ai_state.get("is_speaking"):
                self.set_speaking(True)
            else:
                self.set_speaking(False)
            
            # 感情状態
            emotion = ai_state.get("emotion", "neutral")
            self.set_emotion(emotion)
            
            return True
            
        except Exception as e:
            st.error(f"AI状態同期エラー: {str(e)}")
            return False
    
    def get_current_state(self) -> Dict[str, Any]:
        """現在のVRM状態を取得"""
        return {
            "motion": self.current_motion,
            "speaking": self.is_speaking,
            "emotion": self.current_emotion,
            "vrm_file": self.vrm_file_path,
            "motion_history_count": len(self.motion_history)
        }
    
    def create_control_panel(self) -> None:
        """VRM制御パネルを作成"""
        st.subheader("🎮 VRMアバター制御")
        
        # モーション制御
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🤔 思考中"):
                self.set_motion("thinking")
                st.success("思考モーションを設定")
        
        with col2:
            if st.button("💬 話中"):
                self.set_motion("speaking")
                self.set_speaking(True)
                st.success("話すモーションを設定")
        
        with col3:
            if st.button("⚡ 作業中"):
                self.set_motion("working")
                st.success("作業モーションを設定")
        
        # 感情制御
        st.write("**感情設定**")
        emotions = ["neutral", "happy", "sad", "angry", "surprised", "joy"]
        emotion_cols = st.columns(3)
        
        for i, emotion in enumerate(emotions):
            with emotion_cols[i % 3]:
                if st.button(f"{'😊' if emotion == 'happy' else '😢' if emotion == 'sad' else '😠' if emotion == 'angry' else '😲' if emotion == 'surprised' else '😄' if emotion == 'joy' else '😐'} {emotion.title()}"):
                    self.set_emotion(emotion)
                    st.success(f"{emotion}感情を設定")
        
        # VRMファイル選択
        st.write("**VRMファイル**")
        vrm_files = list(Path(".").glob("*.vrm"))
        if vrm_files:
            selected_vrm = st.selectbox(
                "VRMファイルを選択",
                options=[f.name for f in vrm_files],
                index=0
            )
            
            if st.button("🔄 VRMを再読み込み"):
                self.load_vrm_file(selected_vrm)
                st.success(f"{selected_vrm} を読み込みました")
        else:
            st.warning("VRMファイルが見つかりません。avatar.vrmを配置してください")
        
        # 状態表示
        state = self.get_current_state()
        st.write("**現在の状態**")
        st.json(state)
    
    def create_auto_sync_controls(self) -> None:
        """自動同期制御を作成"""
        st.subheader("🔄 自動同期設定")
        
        # 自動同期の有効/無効
        auto_sync = st.checkbox(
            "AI状態と自動同期",
            value=True,
            help="AIエージェントの状態変化をVRMに自動反映"
        )
        
        if auto_sync:
            st.info("✅ 自動同期が有効です")
            
            # 同期間隔
            sync_interval = st.slider(
                "同期間隔（秒）",
                min_value=0.1,
                max_value=2.0,
                value=0.5,
                step=0.1
            )
            
            # 手動同期ボタン
            if st.button("🔄 今すぐ同期"):
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'digital_human'):
                    ai_state = st.session_state.agent.digital_human.get_consciousness_state()
                    self.sync_with_ai_state({
                        "is_thinking": ai_state.get("consciousness_level", 0) < 0.5,
                        "is_speaking": ai_state.get("avatar_state", {}).get("is_speaking", False),
                        "is_working": len(ai_state.get("growth_metrics", {}).get("current_tasks", [])) > 0,
                        "emotion": ai_state.get("emotional_state", {}).get("dominant_emotion", "neutral")
                    })
                    st.success("状態を同期しました")
        else:
            st.warning("⚠️ 自動同期が無効です")
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "status":
            state = self.get_current_state()
            return f"VRM状態: モーション{state['motion']}, 感情{state['emotion']}, 話中{state['speaking']}"
        
        elif command.startswith("motion"):
            parts = command.split()
            if len(parts) >= 2:
                motion = parts[1]
                if self.set_motion(motion):
                    return f"モーションを{motion}に設定しました"
                else:
                    return "モーション設定に失敗しました"
            else:
                return "モーションコマンド形式: motion <type>"
        
        elif command.startswith("emotion"):
            parts = command.split()
            if len(parts) >= 2:
                emotion = parts[1]
                if self.set_emotion(emotion):
                    return f"感情を{emotion}に設定しました"
                else:
                    return "感情設定に失敗しました"
            else:
                return "感情コマンド形式: emotion <type>"
        
        elif command.startswith("speak"):
            parts = command.split()
            if len(parts) >= 2:
                speaking = parts[1].lower() == "true"
                if self.set_speaking(speaking):
                    return f"話す状態を{speaking}に設定しました"
                else:
                    return "話す状態設定に失敗しました"
            else:
                return "話すコマンド形式: speak <true/false>"
        
        elif command.startswith("load"):
            parts = command.split()
            if len(parts) >= 2:
                vrm_path = parts[1]
                if self.load_vrm_file(vrm_path):
                    return f"VRMファイル{vrm_path}を読み込みました"
                else:
                    return "VRMファイル読み込みに失敗しました"
            else:
                return "読み込みコマンド形式: load <vrm_path>"
        
        else:
            return "コマンド形式: status, motion <type>, emotion <type>, speak <true/false>, load <vrm_path>"

# Streamlitコンポーネント描画関数
def render_vrm_avatar(vrm_file: str = "avatar.vrm", height: int = 400, show_controls: bool = True):
    """VRMアバターをStreamlitに描画"""
    vrm_integration = VRMIntegration()
    
    # VRMコンポーネントを描画
    vrm_integration.render_vrm_component(vrm_file, height)
    
    if show_controls:
        # 制御パネルを描画
        vrm_integration.create_control_panel()
        vrm_integration.create_auto_sync_controls()
    
    return vrm_integration
