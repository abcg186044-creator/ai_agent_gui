#!/usr/bin/env python3
"""
スマート音声バッファリングシステム
会話の途切れを防ぐ、高い包容力を持つAI音声入力
"""

import streamlit as st
import numpy as np
import librosa
import pyaudio
import threading
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import webrtcvad
from faster_whisper import WhisperModel
from collections import deque
import queue

# リアルタイム相槌システム
from realtime_aizuchi import RealTimeAizuchiSystem

class SmartVoiceBuffer:
    """スマート音声バッファリングシステム"""
    
    def __init__(self):
        self.name = "smart_voice_buffer"
        self.description = "会話の途切れを防ぐスマート音声バッファリング"
        
        # 音声録音設定
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        
        # VAD設定
        self.vad = webrtcvad.Vad(2)  # 中程度の感度
        
        # Whisperモデル
        self.whisper_model = None
        self.model_loaded = False
        
        # スマートバッファリングパラメータ
        self.silence_threshold = 2.0  # 2秒の無音で会話終了と判定
        self.continuation_threshold = 2.0  # 2秒以内の再開始は継続とみなす
        self.nodding_threshold = 1.0  # 1秒の無音で相槌
        
        # バッファ管理
        self.audio_buffer = []
        self.is_speaking = False
        self.last_speech_time = None
        self.conversation_active = False
        self.waiting_for_continuation = False
        
        # スレッド管理
        self.listening_thread = None
        self.buffer_thread = None
        self.is_listening = False
        
        # 状態管理
        self.current_status = "待機中"
        self.status_messages = {
            "listening": "🎧 聞いています...",
            "waiting": "🤔 まだ聞いてるよ...",
            "processing": "🤖 処理中です...",
            "nodding": "😊 うん、うん...",
            "aizuchi": "👂 相槌中...",
            "ready": "✅ 準備完了"
        }
        
        # 結果保存
        self.last_recognition_result = None
        self.conversation_history = []
        
        # GUI更新用キュー
        self.gui_update_queue = queue.Queue()
        
        # リアルタイム相槌システム
        self.aizuchi_system = RealTimeAizuchiSystem()
        
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Whisperモデルを読み込み"""
        try:
            self.whisper_model = WhisperModel("large-v3", compute_type="int8")
            self.model_loaded = True
            print("✅ Faster-Whisper large-v3 モデル読み込み完了")
        except Exception as e:
            print(f"❌ Whisperモデル読み込みエラー: {str(e)}")
            # フォールバックとしてbaseモデル
            try:
                self.whisper_model = WhisperModel("base", compute_type="int8")
                self.model_loaded = True
                print("✅ Whisper base モデル読み込み完了（フォールバック）")
            except Exception as e2:
                print(f"❌ Whisper base モデルも読み込み失敗: {str(e2)}")
                self.model_loaded = False
    
    def start_smart_listening(self):
        """スマート聴取を開始"""
        if not self.is_listening:
            self.is_listening = True
            self.conversation_active = False
            self.waiting_for_continuation = False
            
            # 相槌システムも開始
            self.aizuchi_system.start_aizuchi_system()
            
            # 聴取スレッド
            self.listening_thread = threading.Thread(target=self._smart_listening_loop, daemon=True)
            self.listening_thread.start()
            
            # バッファ処理スレッド
            self.buffer_thread = threading.Thread(target=self._buffer_management_loop, daemon=True)
            self.buffer_thread.start()
            
            return True
        return False
    
    def stop_smart_listening(self):
        """スマート聴取を停止"""
        self.is_listening = False
        self.conversation_active = False
        self.waiting_for_continuation = False
        
        # 相槌システムも停止
        self.aizuchi_system.stop_aizuchi_system()
        
        return True
    
    def _smart_listening_loop(self):
        """スマート聴取メインループ"""
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("🎧 スマート聴取開始...")
            
            while self.is_listening:
                try:
                    # 音声データを読み込み
                    data = stream.read(self.chunk)
                    audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # VADで音声検出
                    is_speech = self._detect_voice_activity(audio_chunk)
                    
                    current_time = time.time()
                    
                    if is_speech:
                        # 音声検出時
                        if not self.is_speaking:
                            # 新しい発話の開始
                            self.is_speaking = True
                            self.last_speech_time = current_time
                            
                            # 継続判定
                            if (self.waiting_for_continuation and 
                                current_time - self.last_speech_time < self.continuation_threshold):
                                # 前の発話の継続
                                self.current_status = self.status_messages["listening"]
                                print("🔄 発話継続を検出")
                            else:
                                # 新しい会話の開始
                                self.conversation_active = True
                                self.waiting_for_continuation = False
                                self.current_status = self.status_messages["listening"]
                                print("🎤 新しい発話を検出")
                        
                        # 音声をバッファに追加
                        self.audio_buffer.append(audio_chunk)
                        
                        # リアルタイム相槌システムに音声チャンクを渡す
                        self.aizuchi_system.process_audio_chunk(audio_chunk)
                        
                    else:
                        # 無音時
                        if self.is_speaking:
                            # 発話が途切れた
                            self.is_speaking = False
                            self.last_speech_time = current_time
                            
                            if self.conversation_active:
                                # 会話中の途切れ → 待機状態へ
                                self.waiting_for_continuation = True
                                self.current_status = self.status_messages["waiting"]
                                print("⏸️ 発話途切れ、待機中...")
                
                except Exception as e:
                    print(f"聴取ループエラー: {str(e)}")
                    time.sleep(0.1)
            
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def _buffer_management_loop(self):
        """バッファ管理ループ"""
        while self.is_listening:
            try:
                current_time = time.time()
                
                # 相槌判定（1秒の無音）
                if (self.waiting_for_continuation and 
                    self.last_speech_time and 
                    current_time - self.last_speech_time > self.nodding_threshold):
                    
                    # VRMに相槌を指示
                    self._send_vrm_command("nodding")
                    self.current_status = self.status_messages["nodding"]
                
                # 会話終了判定（2秒の無音）
                if (self.waiting_for_continuation and 
                    self.last_speech_time and 
                    current_time - self.last_speech_time > self.silence_threshold):
                    
                    # 会話終了と判定
                    self._finalize_conversation()
                
                time.sleep(0.1)  # 100msごとにチェック
                
            except Exception as e:
                print(f"バッファ管理エラー: {str(e)}")
                time.sleep(0.5)
    
    def _finalize_conversation(self):
        """会話を確定して処理"""
        if len(self.audio_buffer) == 0:
            return
        
        try:
            self.current_status = self.status_messages["processing"]
            print("🤖 会話確定、処理開始...")
            
            # 音声データを結合
            audio_data = np.concatenate(self.audio_buffer)
            
            # Whisperで認識
            if self.model_loaded:
                segments, _ = self.whisper_model.transcribe(
                    audio_data, 
                    language="ja",
                    beam_size=5,
                    vad_filter=True
                )
                
                recognized_text = ""
                for segment in segments:
                    recognized_text += segment.text + " "
                
                recognized_text = recognized_text.strip()
                
                if recognized_text:
                    # 結果を保存
                    self.last_recognition_result = {
                        'text': recognized_text,
                        'timestamp': datetime.now().isoformat(),
                        'duration': len(audio_data) / self.rate,
                        'audio_length': len(self.audio_buffer)
                    }
                    
                    # 会話履歴に追加
                    self.conversation_history.append(self.last_recognition_result)
                    
                    print(f"✅ 認識完了: {recognized_text}")
                    
                    # GUIに通知
                    self.gui_update_queue.put({
                        'type': 'recognition_complete',
                        'text': recognized_text
                    })
                    
                    # VRMに通知
                    self._send_vrm_command("recognition_complete", {
                        'text': recognized_text
                    })
                else:
                    print("⚠️ 認識結果が空でした")
            
            # バッファをクリア
            self.audio_buffer = []
            self.conversation_active = False
            self.waiting_for_continuation = False
            self.current_status = self.status_messages["ready"]
            
        except Exception as e:
            print(f"会話確定エラー: {str(e)}")
            self.current_status = "エラー"
    
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
    
    def _send_vrm_command(self, command: str, data: Dict = None):
        """VRMアバターにコマンドを送信"""
        try:
            # VRM連携機能はメインアプリで実装
            if command == "aizuchi":
                # 相槌コマンド
                emotion = data.get('emotion', 'neutral') if data else 'neutral'
                js_code = f"""
                <script>
                    window.parent.postMessage({{
                        type: 'motion',
                        data: {{ motion: 'aizuchi', emotion: '{emotion}' }}
                    }}, '*');
                </script>
                """
                st.components.v1.html(js_code, height=0)
            
        except Exception as e:
            print(f"VRMコマンド送信エラー: {str(e)}")
    
    def get_current_status(self) -> Dict:
        """現在のステータスを取得"""
        return {
            'status': self.current_status,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'conversation_active': self.conversation_active,
            'waiting_for_continuation': self.waiting_for_continuation,
            'buffer_size': len(self.audio_buffer),
            'last_speech_time': self.last_speech_time,
            'last_result': self.last_recognition_result
        }
    
    def get_gui_updates(self) -> List[Dict]:
        """GUI更新情報を取得"""
        updates = []
        try:
            while not self.gui_update_queue.empty():
                updates.append(self.gui_update_queue.get_nowait())
        except queue.Empty:
            pass
        return updates
    
    def manual_record_with_buffer(self, max_duration: int = 30) -> Dict:
        """手動録音（スマートバッファリング付き）"""
        try:
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            speech_detected = False
            last_speech_time = time.time()
            start_time = time.time()
            
            print(f"🎤 スマート録音開始（最大{max_duration}秒）...")
            
            while time.time() - start_time < max_duration:
                data = stream.read(self.chunk)
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # VADで音声検出
                is_speech = self._detect_voice_activity(audio_chunk)
                
                if is_speech:
                    speech_detected = True
                    last_speech_time = time.time()
                    frames.append(audio_chunk)
                elif speech_detected:
                    # 音声が検出された後の無音
                    if time.time() - last_speech_time > self.silence_threshold:
                        # 2秒の無音で録音終了
                        break
            
            print("🎤 録音完了")
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if len(frames) == 0:
                return {'text': '', 'error': '音声が検出されませんでした'}
            
            # 音声データを結合
            audio_data = np.concatenate(frames)
            
            # Whisperで認識
            result = {'text': '', 'duration': len(audio_data) / self.rate}
            
            if self.model_loaded:
                segments, _ = self.whisper_model.transcribe(
                    audio_data, 
                    language="ja",
                    beam_size=5,
                    vad_filter=True
                )
                
                recognized_text = ""
                for segment in segments:
                    recognized_text += segment.text + " "
                
                result['text'] = recognized_text.strip()
                result['timestamp'] = datetime.now().isoformat()
                
                if result['text']:
                    print(f"✅ 認識結果: {result['text']}")
                else:
                    print("⚠️ 認識結果が空でした")
            
            return result
            
        except Exception as e:
            print(f"手動録音エラー: {str(e)}")
            return {'text': '', 'error': str(e)}
    
    def get_conversation_summary(self) -> Dict:
        """会話サマリーを取得"""
        return {
            'total_conversations': len(self.conversation_history),
            'total_duration': sum(conv.get('duration', 0) for conv in self.conversation_history),
            'average_duration': np.mean([conv.get('duration', 0) for conv in self.conversation_history]) if self.conversation_history else 0,
            'last_conversation': self.conversation_history[-1] if self.conversation_history else None,
            'buffer_efficiency': self._calculate_buffer_efficiency()
        }
    
    def _calculate_buffer_efficiency(self) -> float:
        """バッファ効率を計算"""
        if not self.conversation_history:
            return 0.0
        
        # 継続された会話の割合を計算
        continued_count = 0
        for i, conv in enumerate(self.conversation_history):
            if i > 0:
                # 前の会話との時間間隔をチェック
                prev_time = datetime.fromisoformat(self.conversation_history[i-1]['timestamp'])
                curr_time = datetime.fromisoformat(conv['timestamp'])
                time_diff = (curr_time - prev_time).total_seconds()
                
                if time_diff < self.continuation_threshold * 2:  # 継続の範囲内
                    continued_count += 1
        
        return continued_count / len(self.conversation_history) if self.conversation_history else 0.0
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "start_smart_listening":
            if self.start_smart_listening():
                return "スマート聴取を開始しました"
            else:
                return "すでに聴取中です"
        
        elif command == "stop_smart_listening":
            if self.stop_smart_listening():
                return "スマート聴取を停止しました"
            else:
                return "聴取していません"
        
        elif command.startswith("smart_record"):
            try:
                parts = command.split()
                duration = int(parts[1]) if len(parts) > 1 else 30
                result = self.manual_record_with_buffer(duration)
                if result.get('text'):
                    return f"認識結果: {result['text']} (継続時間: {result['duration']:.1f}秒)"
                else:
                    return f"録音エラー: {result.get('error', '不明なエラー')}"
            except:
                return "録音コマンド形式: smart_record [最大秒数]"
        
        elif command == "status":
            status = self.get_current_status()
            return f"スマート音声状態: {status['status']}, 聴取中={status['is_listening']}, 会話中={status['conversation_active']}, バッファ={status['buffer_size']}"
        
        elif command == "summary":
            summary = self.get_conversation_summary()
            return f"会話サマリー: 総数={summary['total_conversations']}, 総時間={summary['total_duration']:.1f}秒, 効率={summary['buffer_efficiency']:.2f}"
        
        elif command == "last_result":
            if self.last_recognition_result:
                return f"最後の認識: {self.last_recognition_result['text']} ({self.last_recognition_result['duration']:.1f}秒)"
            else:
                return "認識結果がありません"
        
        else:
            return "コマンド形式: start_smart_listening, stop_smart_listening, smart_record [秒数], status, summary, last_result"

# Streamlit GUIコンポーネント
def create_smart_voice_gui(smart_buffer: SmartVoiceBuffer):
    """スマート音声GUIを作成"""
    st.subheader("🎤 スマート音声バッファリング")
    
    # ステータス表示
    status = smart_buffer.get_current_status()
    
    # リアルタイムステータス
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "現在の状態",
            status['status'],
            help="現在の音声認識状態"
        )
    
    with col2:
        st.metric(
            "バッファサイズ",
            f"{status['buffer_size']} チャンク",
            help="現在の音声バッファ量"
        )
    
    with col3:
        is_active = "会話中" if status['conversation_active'] else "待機中"
        st.metric(
            "会話状態",
            is_active,
            help="会話の進行状況"
        )
    
    # 制御ボタン
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎧 スマート聴取開始", type="primary", disabled=status['is_listening']):
            if smart_buffer.start_smart_listening():
                st.success("🎧 スマート聴取を開始しました")
                st.info("🗣️ ゆっくり話してください。AIが最後までお待ちします")
            else:
                st.warning("すでに聴取中です")
    
    with col2:
        if st.button("⏹️ 聴取停止", type="secondary", disabled=not status['is_listening']):
            if smart_buffer.stop_smart_listening():
                st.info("⏹️ スマート聴取を停止しました")
    
    # 手動録音
    st.write("**手動録音（スマートバッファリング付き）**")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        max_duration = st.slider("最大録音時間（秒）", 5, 60, 30)
    
    with col2:
        if st.button("🎤 録音開始", type="primary"):
            with st.spinner("🎤 スマート録音中..."):
                result = smart_buffer.manual_record_with_buffer(max_duration)
                
                if result.get('text'):
                    st.success(f"✅ 認識結果: {result['text']}")
                    st.info(f"⏱️ 録音時間: {result['duration']:.1f}秒")
                    
                    # テキスト入力欄に自動入力
                    st.session_state.smart_voice_text = result['text']
                else:
                    st.warning(f"⚠️ {result.get('error', '音声が認識されませんでした')}")
    
    # GUI更新情報の表示
    gui_updates = smart_buffer.get_gui_updates()
    for update in gui_updates:
        if update['type'] == 'recognition_complete':
            st.success(f"🎤 自動認識: {update['text']}")
            st.session_state.smart_voice_text = update['text']
    
    # 最後の結果
    if st.button("📋 最後の認識結果"):
        if smart_buffer.last_recognition_result:
            st.info(f"最後の認識: {smart_buffer.last_recognition_result['text']}")
            st.info(f"時間: {smart_buffer.last_recognition_result['duration']:.1f}秒")
        else:
            st.info("認識結果がありません")
    
    # 会話サマリー
    if st.button("📊 会話サマリー"):
        summary = smart_buffer.get_conversation_summary()
        st.json(summary)
    
    # 詳細ステータス
    with st.expander("🔍 詳細ステータス"):
        st.json(status)
