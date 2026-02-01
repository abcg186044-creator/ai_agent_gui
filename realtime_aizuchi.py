#!/usr/bin/env python3
"""
リアルタイム相槌（あいづち）システム
ユーザーの発話中に自然な相槌を打つ高度なリスニング機能
"""

import streamlit as st
import numpy as np
import librosa
import pyaudio
import threading
import time
import json
import random
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import webrtcvad
from collections import deque
import queue
import tempfile

class RealTimeAizuchiSystem:
    """リアルタイム相槌システム"""
    
    def __init__(self):
        self.name = "realtime_aizuchi"
        self.description = "発話中のリアルタイム相槌システム"
        
        # 音声録音設定
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 256  # 小さなチャンクで高頻度処理
        
        # VAD設定
        self.vad = webrtcvad.Vad(2)  # 中程度の感度
        
        # 相槌タイミング設定
        self.aizuchi_min_duration = 1.5  # 1.5秒の発話で相槌可能
        self.aizuchi_max_duration = 8.0  # 8秒以上の長話は相槌を控える
        self.aizuchi_cooldown = 2.0  # 相槌後のクールダウン
        self.pause_threshold = 0.3  # 0.3秒の無音を文の区切りと判定
        
        # VOICEVOX設定
        self.voicevox_url = "http://localhost:50021"
        self.aizuchi_speaker_id = 3  # 相槌用話者ID（四国めたんなど）
        
        # 相槌パターン
        self.aizuchi_patterns = {
            'neutral': ['うん', 'なるほど', 'そうだね', '了解'],
            'positive': ['なるほど！', 'そうなんだ！', 'へぇー！', 'おもしろい！'],
            'thinking': ['うーん', 'そうか...', 'なるほどね', 'ふむふむ'],
            'sympathy': ['そうなんだ...', '大変だね', 'わかるよ', 'そうなんだね'],
            'surprise': ['へぇー！', 'まじで！', 'うそ！', 'ほんとに？']
        }
        
        # 状態管理
        self.is_active = False
        self.speech_start_time = None
        self.last_speech_time = None
        self.last_aizuchi_time = None
        self.continuous_speech_duration = 0.0
        self.pause_count = 0
        self.current_emotion = 'neutral'
        
        # 音声バッファ
        self.speech_buffer = deque(maxlen=1000)  # 最近の音声チャンク
        self.energy_history = deque(maxlen=50)   # エネルギー履歴
        self.pitch_history = deque(maxlen=50)     # ピッチ履歴
        
        # スレッド管理
        self.aizuchi_thread = None
        self.is_running = False
        
        # 相槌再生キュー
        self.aizuchi_queue = queue.Queue()
        self.playback_thread = None
        
        # 統計情報
        self.aizuchi_count = 0
        self.aizuchi_history = []
        
        # 初期化
        self._init_voicevox()
    
    def _init_voicevox(self):
        """VOICEVOX初期化"""
        try:
            response = requests.get(f"{self.voicevox_url}/speakers")
            if response.status_code == 200:
                speakers = response.json()
                # 相槌に適した話者を探す
                for speaker in speakers:
                    if speaker["name"] in ["四国めたん", "ずんだもん", "春日部つぐみ"]:
                        for style in speaker["styles"]:
                            self.aizuchi_speaker_id = style["id"]
                            break
                        break
                print(f"✅ 相槌用話者ID: {self.aizuchi_speaker_id}")
            else:
                print("⚠️ VOICEVOXに接続できません")
        except Exception as e:
            print(f"❌ VOICEVOX初期化エラー: {str(e)}")
    
    def start_aizuchi_system(self):
        """相槌システムを開始"""
        if not self.is_active:
            self.is_active = True
            self.is_running = True
            
            # 相槌再生スレッド
            self.playback_thread = threading.Thread(target=self._aizuchi_playback_loop, daemon=True)
            self.playback_thread.start()
            
            print("🎯 リアルタイム相槌システムを開始しました")
            return True
        return False
    
    def stop_aizuchi_system(self):
        """相槌システムを停止"""
        self.is_active = False
        self.is_running = False
        return True
    
    def process_audio_chunk(self, audio_chunk: np.ndarray):
        """音声チャンクを処理"""
        if not self.is_active:
            return
        
        current_time = time.time()
        
        # VADで音声検出
        is_speech = self._detect_voice_activity(audio_chunk)
        
        # エネルギー計算
        energy = np.mean(audio_chunk ** 2)
        self.energy_history.append(energy)
        
        # ピッチ推定（簡易）
        pitch = self._estimate_pitch(audio_chunk)
        self.pitch_history.append(pitch)
        
        # 音声バッファに追加
        self.speech_buffer.append({
            'audio': audio_chunk,
            'timestamp': current_time,
            'is_speech': is_speech,
            'energy': energy,
            'pitch': pitch
        })
        
        # 発話状態の更新
        self._update_speech_state(is_speech, current_time)
        
        # 相槌タイミングの判定
        if is_speech:
            self._check_aizuchi_timing(current_time)
    
    def _detect_voice_activity(self, audio_chunk: np.ndarray) -> bool:
        """音声活動検出"""
        try:
            # 音声データを16bitに変換
            audio_int16 = (audio_chunk * 32767).astype(np.int16)
            
            # VADで判定
            is_speech = self.vad.is_speech(audio_int16.tobytes(), self.rate)
            return is_speech
            
        except Exception as e:
            print(f"VADエラー: {str(e)}")
            return False
    
    def _estimate_pitch(self, audio_chunk: np.ndarray) -> float:
        """ピッチ推定（簡易版）"""
        try:
            # 自己相関関数で基本周波数を推定
            autocorr = np.correlate(audio_chunk, audio_chunk, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # ピーク検出
            peak = np.argmax(autocorr[1:]) + 1
            if peak > 0:
                pitch = self.rate / peak
                # 人間の声の範囲に制限
                if 50 <= pitch <= 500:
                    return pitch
        except:
            pass
        
        return 0.0
    
    def _update_speech_state(self, is_speech: bool, current_time: float):
        """発話状態を更新"""
        if is_speech:
            if self.speech_start_time is None:
                # 新しい発話の開始
                self.speech_start_time = current_time
                self.continuous_speech_duration = 0.0
                self.pause_count = 0
                print("🎤 発話開始検出")
            
            self.last_speech_time = current_time
            self.continuous_speech_duration = current_time - self.speech_start_time
            
        else:
            # 無音時
            if self.last_speech_time and (current_time - self.last_speech_time) > self.pause_threshold:
                # 文の区切りと判定
                self.pause_count += 1
                print(f"⏸️ 文の区切り検出 (合計: {self.pause_count})")
    
    def _check_aizuchi_timing(self, current_time: float):
        """相槌タイミングをチェック"""
        # 条件チェック
        if not self._should_aizuchi(current_time):
            return
        
        # 感情分析
        emotion = self._analyze_speech_emotion()
        
        # 相槌の種類を選択
        aizuchi_text = self._select_aizuchi(emotion)
        
        # 相槌をキューに追加
        aizuchi_data = {
            'text': aizuchi_text,
            'emotion': emotion,
            'timestamp': current_time,
            'speech_duration': self.continuous_speech_duration
        }
        
        self.aizuchi_queue.put(aizuchi_data)
        self.last_aizuchi_time = current_time
        
        print(f"👂 相槌キュー追加: {aizuchi_text} (感情: {emotion})")
    
    def _should_aizuchi(self, current_time: float) -> bool:
        """相槌を打つべきか判定"""
        # 基本条件チェック
        if not self.is_active or not self.speech_start_time:
            return False
        
        # 発話継続時間チェック
        if self.continuous_speech_duration < self.aizuchi_min_duration:
            return False
        
        if self.continuous_speech_duration > self.aizuchi_max_duration:
            return False
        
        # クールダウンチェック
        if self.last_aizuchi_time and (current_time - self.last_aizuchi_time) < self.aizuchi_cooldown:
            return False
        
        # 文の区切りチェック（1回以上のポーズがある）
        if self.pause_count < 1:
            return False
        
        # エネルギー変動チェック（話し方の変化）
        if len(self.energy_history) < 10:
            return False
        
        energy_variance = np.var(list(self.energy_history)[-10:])
        if energy_variance < 1e-6:  # 単調な発話は控える
            return False
        
        return True
    
    def _analyze_speech_emotion(self) -> str:
        """発話の感情を分析"""
        if len(self.pitch_history) < 5 or len(self.energy_history) < 5:
            return 'neutral'
        
        # ピッチの統計
        recent_pitches = list(self.pitch_history)[-5:]
        pitch_mean = np.mean(recent_pitches)
        pitch_std = np.std(recent_pitches)
        
        # エネルギーの統計
        recent_energies = list(self.energy_history)[-5:]
        energy_mean = np.mean(recent_energies)
        energy_std = np.std(recent_energies)
        
        # 感情判定（簡易ルール）
        if pitch_mean > 200 and pitch_std > 30:
            return 'surprise'
        elif pitch_mean > 180 and energy_std > 0.001:
            return 'positive'
        elif pitch_mean < 100 and energy_std < 0.0005:
            return 'sympathy'
        elif self.pause_count > 2:
            return 'thinking'
        else:
            return 'neutral'
    
    def _select_aizuchi(self, emotion: str) -> str:
        """相槌の種類を選択"""
        patterns = self.aizuchi_patterns.get(emotion, self.aizuchi_patterns['neutral'])
        return random.choice(patterns)
    
    def _aizuchi_playback_loop(self):
        """相槌再生ループ"""
        while self.is_running:
            try:
                # キューから相槌データを取得
                aizuchi_data = self.aizuchi_queue.get(timeout=0.1)
                
                # 音声合成と再生
                self._synthesize_and_play_aizuchi(aizuchi_data)
                
                # VRMに相槌モーションを送信
                self._send_vrm_aizuchi_motion(aizuchi_data)
                
                # 統計更新
                self.aizuchi_count += 1
                self.aizuchi_history.append(aizuchi_data)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"相槌再生エラー: {str(e)}")
    
    def _synthesize_and_play_aizuchi(self, aizuchi_data: Dict):
        """相槌の音声合成と再生"""
        try:
            # VOICEVOXで音声合成
            query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={
                    'speaker': self.aizuchi_speaker_id,
                    'text': aizuchi_data['text']
                }
            )
            
            if query_response.status_code == 200:
                query = query_response.json()
                
                # 相槌用のパラメータ調整
                query['speedScale'] = 1.2  # 少し速め
                query['pitchScale'] = 1.0
                query['volumeScale'] = 0.7  # 少し静かに
                
                # 音声合成
                synth_response = requests.post(
                    f"{self.voicevox_url}/synthesis",
                    params={'speaker': self.aizuchi_speaker_id},
                    json=query
                )
                
                if synth_response.status_code == 200:
                    # 一時ファイルに保存
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                        f.write(synth_response.content)
                        temp_file = f.name
                    
                    # 音声再生（非同期）
                    self._play_audio_file(temp_file)
                    
                    # ファイル削除
                    Path(temp_file).unlink(missing_ok=True)
                    
                    print(f"🔊 相槌再生: {aizuchi_data['text']}")
                
        except Exception as e:
            print(f"相槌音声合成エラー: {str(e)}")
    
    def _play_audio_file(self, file_path: str):
        """音声ファイルを再生"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # 再生終了を待機（非同期にする場合はコメントアウト）
            while pygame.mixer.music.get_busy():
                time.sleep(0.01)
                
        except Exception as e:
            print(f"音声再生エラー: {str(e)}")
    
    def _send_vrm_aizuchi_motion(self, aizuchi_data: Dict):
        """VRMに相槌モーションを送信"""
        try:
            # VRM連携機能はメインアプリで実装
            motion_type = "aizuchi"
            emotion = aizuchi_data['emotion']
            
            # JavaScriptにメッセージを送信
            js_code = f"""
            <script>
                window.parent.postMessage({{
                    type: 'motion',
                    data: {{ motion: '{motion_type}', emotion: '{emotion}' }}
                }}, '*');
            </script>
            """
            
            # Streamlitで実行
            st.components.v1.html(js_code, height=0)
            
        except Exception as e:
            print(f"VRMモーション送信エラー: {str(e)}")
    
    def get_aizuchi_statistics(self) -> Dict:
        """相槌統計情報を取得"""
        if not self.aizuchi_history:
            return {
                'total_aizuchi': 0,
                'average_interval': 0,
                'emotion_distribution': {},
                'most_used_aizuchi': None
            }
        
        # 感情分布
        emotion_counts = {}
        for aizuchi in self.aizuchi_history:
            emotion = aizuchi['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # 最も使用した相槌
        aizuchi_texts = [a['text'] for a in self.aizuchi_history]
        most_common = max(set(aizuchi_texts), key=aizuchi_texts.count) if aizuchi_texts else None
        
        # 平均間隔
        if len(self.aizuchi_history) > 1:
            intervals = []
            for i in range(1, len(self.aizuchi_history)):
                interval = self.aizuchi_history[i]['timestamp'] - self.aizuchi_history[i-1]['timestamp']
                intervals.append(interval)
            avg_interval = np.mean(intervals)
        else:
            avg_interval = 0
        
        return {
            'total_aizuchi': self.aizuchi_count,
            'average_interval': avg_interval,
            'emotion_distribution': emotion_counts,
            'most_used_aizuchi': most_common,
            'current_speech_duration': self.continuous_speech_duration,
            'pause_count': self.pause_count
        }
    
    def reset_state(self):
        """状態をリセット"""
        self.speech_start_time = None
        self.last_speech_time = None
        self.last_aizuchi_time = None
        self.continuous_speech_duration = 0.0
        self.pause_count = 0
        self.speech_buffer.clear()
        self.energy_history.clear()
        self.pitch_history.clear()
        
        # キューをクリア
        while not self.aizuchi_queue.empty():
            try:
                self.aizuchi_queue.get_nowait()
            except queue.Empty:
                break
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "start_aizuchi":
            if self.start_aizuchi_system():
                return "リアルタイム相槌システムを開始しました"
            else:
                return "すでに稼働中です"
        
        elif command == "stop_aizuchi":
            if self.stop_aizuchi_system():
                return "リアルタイム相槌システムを停止しました"
            else:
                return "稼働していません"
        
        elif command == "status":
            stats = self.get_aizuchi_statistics()
            return f"相槌システム状態: 稼働中={self.is_active}, 相槌数={stats['total_aizuchi']}, 発話継続={stats['current_speech_duration']:.1f}秒"
        
        elif command == "statistics":
            stats = self.get_aizuchi_statistics()
            return json.dumps(stats, ensure_ascii=False, indent=2)
        
        elif command == "reset":
            self.reset_state()
            return "相槌システムの状態をリセットしました"
        
        else:
            return "コマンド形式: start_aizuchi, stop_aizuchi, status, statistics, reset"

# Streamlit GUIコンポーネント
def create_aizuchi_gui(aizuchi_system: RealTimeAizuchiSystem):
    """相槌システムGUIを作成"""
    st.subheader("👂 リアルタイム相槌システム")
    
    # 統計情報
    stats = aizuchi_system.get_aizuchi_statistics()
    
    # リアルタイムメトリクス
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "システム状態",
            "🟢 稼働中" if aizuchi_system.is_active else "🔴 停止中",
            help="相槌システムの稼働状態"
        )
    
    with col2:
        st.metric(
            "相槌回数",
            stats['total_aizuchi'],
            help="累計相槌回数"
        )
    
    with col3:
        st.metric(
            "発話継続",
            f"{stats['current_speech_duration']:.1f}秒",
            help="現在の発話継続時間"
        )
    
    with col4:
        st.metric(
            "文の区切り",
            stats['pause_count'],
            help="検出された文の区切り数"
        )
    
    # 制御ボタン
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 相槌開始", type="primary", disabled=aizuchi_system.is_active):
            if aizuchi_system.start_aizuchi_system():
                st.success("🎯 リアルタイム相槌を開始しました")
                st.info("🗣️ 発話中に自然な相槌が入ります")
            else:
                st.warning("すでに稼働中です")
    
    with col2:
        if st.button("⏹️ 相槌停止", type="secondary", disabled=not aizuchi_system.is_active):
            if aizuchi_system.stop_aizuchi_system():
                st.info("⏹️ リアルタイム相槌を停止しました")
    
    # 相槌パターン設定
    st.write("**相槌パターン設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**基本相槌**")
        st.code(", ".join(aizuchi_system.aizuchi_patterns['neutral']))
    
    with col2:
        st.write("**感情別相槌**")
        for emotion, patterns in aizuchi_system.aizuchi_patterns.items():
            if emotion != 'neutral':
                st.write(f"{emotion}: {', '.join(patterns[:2])}")
    
    # 統計詳細
    if st.button("📊 相槌統計"):
        st.json(stats)
    
    # 手動テスト
    st.write("**手動テスト**")
    if st.button("🧪 テスト相槌"):
        # テスト用相槌データ
        test_aizuchi = {
            'text': 'なるほど',
            'emotion': 'neutral',
            'timestamp': time.time(),
            'speech_duration': 2.0
        }
        
        aizuchi_system.aizuchi_queue.put(test_aizuchi)
        st.success("🧪 テスト相槌をキューに追加しました")
    
    # 状態リセット
    if st.button("🔄 状態リセット"):
        aizuchi_system.reset_state()
        st.info("🔄 相槌システムの状態をリセットしました")
