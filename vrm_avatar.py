#!/usr/bin/env python3
"""
3D VRMアバター・インターフェース
AIの思考や感情に同期してアニメーション
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading

class VRMAvatar:
    def __init__(self):
        self.name = "vrm_avatar"
        self.description = "3D VRMアバターによるAI表現"
        
        # アバター状態
        self.current_emotion = "neutral"
        self.is_speaking = False
        self.is_thinking = False
        self.gaze_direction = [0, 0, 1]  # 前向き
        self.blend_shapes = {}
        
        # アニメーション履歴
        self.animation_history = []
        
        # VRMモデル情報（ダミー）
        self.model_info = {
            "name": "テックくん",
            "version": "1.0",
            "author": "AI System"
        }
        
        # 表情ブレンドシェイプ
        self.expressions = {
            "neutral": {"joy": 0, "angry": 0, "sorrow": 0, "fun": 0, "surprised": 0},
            "joy": {"joy": 1.0, "angry": 0, "sorrow": 0, "fun": 0.5, "surprised": 0.3},
            "sad": {"joy": 0, "angry": 0, "sorrow": 1.0, "fun": 0, "surprised": 0},
            "thinking": {"joy": 0, "angry": 0, "sorrow": 0, "fun": 0, "surprised": 0.5},
            "surprised": {"joy": 0.3, "angry": 0, "sorrow": 0, "fun": 0.8, "surprised": 1.0},
            "love": {"joy": 0.8, "angry": 0, "sorrow": 0, "fun": 0.6, "surprised": 0.2}
        }
        
        # ジェスチャー定義
        self.gestures = {
            "greeting": {"type": "wave", "duration": 2.0},
            "thinking": {"type": "hand_chin", "duration": 0},
            "explaining": {"type": "hand_gesture", "duration": 0},
            "happy": {"type": "jump", "duration": 1.0},
            "nodding": {"type": "nod", "duration": 1.0}
        }
        
        self.current_gesture = None
        self.gesture_start_time = None
    
    def update_emotion(self, emotion: str, intensity: float = 1.0):
        """感情を更新"""
        self.current_emotion = emotion
        
        # ブレンドシェイプを更新
        if emotion in self.expressions:
            base_expression = self.expressions[emotion]
            self.blend_shapes = {
                key: value * intensity for key, value in base_expression.items()
            }
        
        # 履歴に記録
        self.animation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "emotion",
            "emotion": emotion,
            "intensity": intensity
        })
    
    def start_speaking(self):
        """話し始め"""
        self.is_speaking = True
        # 話している時の微細なアニメーション
        self.update_emotion("neutral", 0.8)
    
    def stop_speaking(self):
        """話し終わり"""
        self.is_speaking = False
        # 少し頷く
        self.play_gesture("nodding")
    
    def start_thinking(self):
        """考え始め"""
        self.is_thinking = True
        self.update_emotion("thinking", 0.7)
        self.play_gesture("thinking")
    
    def stop_thinking(self):
        """考え終わり"""
        self.is_thinking = False
        self.update_emotion("neutral", 0.5)
    
    def update_gaze(self, direction: List[float]):
        """視線方向を更新"""
        self.gaze_direction = direction
    
    def play_gesture(self, gesture_name: str):
        """ジェスチャーを再生"""
        if gesture_name in self.gestures:
            self.current_gesture = self.gestures[gesture_name]
            self.gesture_start_time = time.time()
            
            self.animation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "gesture",
                "gesture": gesture_name
            })
    
    def get_current_state(self) -> Dict:
        """現在のアバター状態を取得"""
        return {
            "emotion": self.current_emotion,
            "is_speaking": self.is_speaking,
            "is_thinking": self.is_thinking,
            "gaze_direction": self.gaze_direction,
            "blend_shapes": self.blend_shapes,
            "current_gesture": self.current_gesture,
            "model_info": self.model_info
        }
    
    def create_3d_visualization(self) -> go.Figure:
        """3Dアバターの可視化を作成"""
        # 簡略化された3D頭部モデル
        fig = go.Figure()
        
        # 頭部（球体）
        fig.add_trace(go.Mesh3d(
            x=[0, 1, 1, 0, 0, 1, 1, 0],
            y=[0, 0, 1, 1, 0, 0, 1, 1],
            z=[0, 0, 0, 0, 1, 1, 1, 1],
            color='lightblue',
            opacity=0.8,
            name='頭部'
        ))
        
        # 目
        eye_color = 'blue' if self.is_thinking else 'black'
        fig.add_trace(go.Scatter3d(
            x=[0.3, 0.7],
            y=[0.3, 0.3],
            z=[0.6, 0.6],
            mode='markers',
            marker=dict(size=10, color=eye_color),
            name='目'
        ))
        
        # 口（感情によって変化）
        mouth_shape = self.get_mouth_shape()
        fig.add_trace(go.Scatter3d(
            x=mouth_shape['x'],
            y=mouth_shape['y'],
            z=mouth_shape['z'],
            mode='lines',
            line=dict(color='red', width=3),
            name='口'
        ))
        
        # 視線方向
        fig.add_trace(go.Scatter3d(
            x=[0.5, 0.5 + self.gaze_direction[0] * 0.5],
            y=[0.5, 0.5 + self.gaze_direction[1] * 0.5],
            z=[0.6, 0.6 + self.gaze_direction[2] * 0.5],
            mode='lines',
            line=dict(color='green', width=2),
            name='視線'
        ))
        
        fig.update_layout(
            title="VRMアバター - テックくん",
            scene=dict(
                xaxis=dict(range=[-0.5, 1.5]),
                yaxis=dict(range=[-0.5, 1.5]),
                zaxis=dict(range=[-0.5, 1.5]),
                aspectmode='cube'
            ),
            width=400,
            height=400
        )
        
        return fig
    
    def get_mouth_shape(self) -> Dict:
        """現在の感情に応じた口の形を取得"""
        if self.is_speaking:
            # 話している時の口の形
            return {
                'x': [0.3, 0.5, 0.7],
                'y': [0.1, 0.05, 0.1],
                'z': [0.3, 0.3, 0.3]
            }
        elif self.current_emotion == "joy":
            # 嬉しい時
            return {
                'x': [0.35, 0.5, 0.65],
                'y': [0.1, 0.15, 0.1],
                'z': [0.3, 0.3, 0.3]
            }
        elif self.current_emotion == "sad":
            # 悲しい時
            return {
                'x': [0.4, 0.5, 0.6],
                'y': [0.1, 0.05, 0.1],
                'z': [0.3, 0.3, 0.3]
            }
        else:
            # 普通
            return {
                'x': [0.4, 0.5, 0.6],
                'y': [0.1, 0.1, 0.1],
                'z': [0.3, 0.3, 0.3]
            }
    
    def create_emotion_dashboard(self) -> Dict:
        """感情ダッシュボードを作成"""
        state = self.get_current_state()
        
        # 感情ゲージ
        emotion_data = {
            "感情": ["喜び", "悲しみ", "楽しさ", "驚き", "怒り"],
            "強さ": [
                self.blend_shapes.get("joy", 0),
                self.blend_shapes.get("sorrow", 0),
                self.blend_shapes.get("fun", 0),
                self.blend_shapes.get("surprised", 0),
                self.blend_shapes.get("angry", 0)
            ]
        }
        
        return {
            "current_emotion": self.current_emotion,
            "is_speaking": self.is_speaking,
            "is_thinking": self.is_thinking,
            "emotion_data": emotion_data,
            "blend_shapes": self.blend_shapes
        }
    
    def sync_with_ai_state(self, ai_state: Dict):
        """AIの状態と同期"""
        # 感情同期
        if "emotion" in ai_state:
            self.update_emotion(ai_state["emotion"])
        
        # 話し状態同期
        if "is_speaking" in ai_state:
            if ai_state["is_speaking"]:
                self.start_speaking()
            else:
                self.stop_speaking()
        
        # 思考状態同期
        if "is_thinking" in ai_state:
            if ai_state["is_thinking"]:
                self.start_thinking()
            else:
                self.stop_thinking()
        
        # 視線同期
        if "gaze_direction" in ai_state:
            self.update_gaze(ai_state["gaze_direction"])
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "status":
            state = self.get_current_state()
            return f"アバター状態: 感情{state['emotion']} 話中{state['is_speaking']} 考え中{state['is_thinking']}"
        elif command.startswith("emotion"):
            try:
                parts = command.split()
                if len(parts) >= 2:
                    emotion = parts[1]
                    intensity = float(parts[2]) if len(parts) > 2 else 1.0
                    self.update_emotion(emotion, intensity)
                    return f"感情を{emotion}に設定しました"
            except:
                pass
            return "感情コマンド形式: emotion <name> [intensity]"
        elif command.startswith("gesture"):
            try:
                parts = command.split()
                if len(parts) >= 2:
                    gesture = parts[1]
                    self.play_gesture(gesture)
                    return f"ジェスチャー{gesture}を再生しました"
            except:
                pass
            return "ジェスチャーコマンド形式: gesture <name>"
        elif command == "history":
            if self.animation_history:
                recent = self.animation_history[-5:]
                return "\n".join([f"{h['timestamp']}: {h['type']} - {h.get('emotion', h.get('gesture', ''))}" for h in recent])
            else:
                return "アニメーション履歴はありません"
        else:
            return "コマンド形式: status, emotion <name> [intensity], gesture <name>, history"

# Streamlitコンポーネント
def render_vrm_avatar(avatar: VRMAvatar):
    """VRMアバターをStreamlitに描画"""
    st.subheader("🤖 3Dアバター - テックくん")
    
    # 3D可視化
    fig = avatar.create_3d_visualization()
    st.plotly_chart(fig, use_container_width=True)
    
    # 状態ダッシュボード
    dashboard = avatar.create_emotion_dashboard()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**現在の状態**")
        st.write(f"感情: {dashboard['current_emotion']}")
        st.write(f"話中: {'はい' if dashboard['is_speaking'] else 'いいえ'}")
        st.write(f"考え中: {'はい' if dashboard['is_thinking'] else 'いいえ'}")
    
    with col2:
        st.write("**感情の強さ**")
        emotion_df = px.data.tips()
        fig_emotion = px.bar(
            x=dashboard["emotion_data"]["感情"],
            y=dashboard["emotion_data"]["強さ"],
            title="感情ブレンドシェイプ"
        )
        st.plotly_chart(fig_emotion, use_container_width=True)
    
    # 操作パネル
    st.subheader("🎮 アバター操作")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😊 喜ぶ"):
            avatar.update_emotion("joy", 1.0)
    
    with col2:
        if st.button("🤔 考える"):
            avatar.start_thinking()
    
    with col3:
        if st.button("👋 挨拶"):
            avatar.play_gesture("greeting")
    
    # 感情スライダー
    st.write("**感情調整**")
    emotions = ["neutral", "joy", "sad", "thinking", "surprised", "love"]
    selected_emotion = st.selectbox("感情を選択", emotions)
    intensity = st.slider("強さ", 0.0, 1.0, 0.5)
    
    if st.button("感情を適用"):
        avatar.update_emotion(selected_emotion, intensity)
        st.success(f"感情を{selected_emotion}（強さ{intensity}）に設定しました")
