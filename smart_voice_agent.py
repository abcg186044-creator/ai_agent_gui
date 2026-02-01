#!/usr/bin/env python3
"""
Smart Voice AI Agent - スマート・バッファリング機能付き音声入力システム
"""

import streamlit as st
import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import torch
import torchaudio
import requests
import json
import hashlib

# 基本インポート
try:
    import ollama
    import faster_whisper
    import pyttsx3
    import sounddevice as sd
    import soundfile as sf
    import torch
    import torchaudio
except ImportError as e:
    st.error(f"❌ 必須ライブラリのインポートエラー: {str(e)}")
    st.stop()

# 設定
class Config:
    MAIN_MODEL = "llama3.2"
    WHISPER_MODEL = "large-v3"
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_FORMAT = "int16"
    
    # スマートバッファリング設定
    VAD_SILENCE_THRESHOLD = 0.5
    MIN_SPEECH_DURATION = 2.0  # 最小発話時間（秒）
    MAX_PAUSE_DURATION = 2.0   # 最大休止時間（秒）
    BUFFER_TIMEOUT = 5.0       # バッファタイムアウト（秒）
    
    # UI設定
    NODDING_INTERVAL = 1.0  # 相槌間隔（秒）

class SmartVoiceBuffer:
    """スマート音声バッファリングシステム"""
    
    def __init__(self):
        self.is_active = False
        self.audio_buffer = []
        self.speech_segments = []
        self.last_speech_end = None
        self.current_segment_start = None
        self.total_duration = 0.0
        
    def start_segment(self):
        """音声セグメント開始"""
        self.current_segment_start = time.time()
        
    def end_segment(self):
        """音声セグメント終了"""
        if self.current_segment_start:
            duration = time.time() - self.current_segment_start
            if duration >= Config.MIN_SPEECH_DURATION:
                self.speech_segments.append({
                    "start": self.current_segment_start,
                    "end": time.time(),
                    "duration": duration,
                    "audio_data": self.audio_buffer.copy()
                })
                self.total_duration += duration
            
            self.last_speech_end = time.time()
            self.current_segment_start = None
            self.audio_buffer = []
    
    def add_audio_data(self, audio_data):
        """音声データを追加"""
        self.audio_buffer.extend(audio_data)
    
    def should_process_speech(self):
        """音声処理すべきか判定"""
        if not self.speech_segments:
            return False
        
        # 最後のセグメント終了から時間をチェック
        if self.last_speech_end:
            time_since_last_speech = time.time() - self.last_speech_end
            return time_since_last_speech >= Config.MAX_PAUSE_DURATION
        
        return False
    
    def get_combined_audio(self):
        """結合された音声データを取得"""
        if not self.speech_segments:
            return None
        
        # 全セグメントの音声データを結合
        combined_audio = []
        for segment in self.speech_segments:
            combined_audio.extend(segment["audio_data"])
        
        return combined_audio
    
    def get_speech_info(self):
        """音声情報を取得"""
        if not self.speech_segments:
            return None
        
        return {
            "segments_count": len(self.speech_segments),
            "total_duration": self.total_duration,
            "first_segment": self.speech_segments[0] if self.speech_segments else None,
            "last_segment": self.speech_segments[-1] if self.speech_segments else None
        }
    
    def reset(self):
        """バッファをリセット"""
        self.speech_segments = []
        self.audio_buffer = []
        self.last_speech_end = None
        self.current_segment_start = None
        self.total_duration = 0.0

class SmartVoiceInputHandler:
    """スマート音声入力ハンドラ"""
    
    def __init__(self):
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.whisper_model = None
        self.vad_model = None
        self.voice_buffer = SmartVoiceBuffer()
        self.processing_thread = None
        self.last_nodding_time = 0
        
    def initialize(self):
        """音声入力システム初期化"""
        try:
            # Whisperモデル読み込み
            self.whisper_model = faster_whisper.WhisperModel(
                Config.WHISPER_MODEL,
                device="cuda" if self._check_cuda() else "cpu",
                compute_type="float32"  # float16をfloat32に変更
            )
            
            # VADモデル読み込み - torch Hubから直接ダウンロード
            try:
                self.vad_model, utils = torch.hub.load(
                    'snakers4/silero-vad',
                    'silero_vad',
                    force_reload=True
                )
                self.vad_utils = utils
            except Exception as vad_error:
                st.warning(f"⚠️ VADモデル読み込みエラー: {vad_error}")
                st.warning("⚠️ VAD機能を無効化します。音声検出は簡易的な方法で行います。")
                self.vad_model = None
            
            return True
        except Exception as e:
            st.error(f"❌ 音声入力システム初期化エラー: {str(e)}")
            return False
    
    def _check_cuda(self):
        """CUDA利用可能かチェック"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def start_recording(self):
        """録音開始"""
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.voice_buffer.reset()
        
        # 録音スレッドを開始
        def audio_callback(indata, frame_count, time_info, status):
            if status:
                st.error(f"❌ 音声入力エラー: {status}")
            self.audio_queue.put(indata.copy())
        
        try:
            # 音声デバイス情報を表示
            device_info = sd.query_devices()
            st.info(f"🎤️ 音声デバイス: {device_info[0]['name']}")
            
            self.processing_thread = threading.Thread(
                target=self._smart_record_audio,
                args=(audio_callback,),
                daemon=True
            )
            self.processing_thread.start()
            return True
        except Exception as e:
            st.error(f"❌ 録音開始エラー: {str(e)}")
            self.is_recording = False
            return False
    
    def _smart_record_audio(self, callback):
        """スマート録音処理"""
        try:
            st.info("🎤️ 録音を開始しました...")
            
            with sd.InputStream(
                samplerate=Config.AUDIO_SAMPLE_RATE,
                channels=Config.AUDIO_CHANNELS,
                dtype=Config.AUDIO_FORMAT,
                blocksize=1024,
                callback=callback
            ) as stream:
                st.success("✅ 音声ストリームが開始されました")
                
                while self.is_recording:
                    try:
                        # 音声データを取得（タイムアウト付き）
                        audio_data = self.audio_queue.get(timeout=1.0)
                        
                        # 音声データを処理
                        if audio_data is not None and len(audio_data) > 0:
                            # VADで音声活動検出
                            if self.vad_model is not None:
                                # torch HubのVADモデルを使用
                                audio_tensor = torch.from_numpy(np.array(audio_data, dtype=np.float32))
                                speech_prob = self.vad_model(audio_tensor, Config.AUDIO_SAMPLE_RATE).item()
                            else:
                                # 簡易的な音声検出（エネルギーベース）
                                audio_array = np.array(audio_data)
                                energy = np.sqrt(np.mean(audio_array**2))
                                speech_prob = 1.0 if energy > 0.01 else 0.0
                            
                            if speech_prob > Config.VAD_SILENCE_THRESHOLD:
                                # 音声が検出された場合
                                if not self.voice_buffer.current_segment_start:
                                    self.voice_buffer.start_segment()
                                    st.info("🎤️ 音声を検出しました...")
                                
                                self.voice_buffer.add_audio_data(audio_data)
                                
                                # 相槌チェック
                                self._check_nodding()
                                
                            else:
                                # 音声が検出されない場合
                                if self.voice_buffer.current_segment_start:
                                    self.voice_buffer.end_segment()
                                    st.info("⏸️ 音声セグメントを終了しました")
                                
                                # 処理すべきかチェック
                                if self.voice_buffer.should_process_speech():
                                    self._process_buffered_speech()
                    
                    except queue.Empty:
                        # タイムアウト - 録音継続
                        continue
                    except Exception as e:
                        st.error(f"❌ 音声処理エラー: {str(e)}")
                        continue
                        
        except Exception as e:
            st.error(f"❌ 録音エラー: {str(e)}")
            self.is_recording = False
    
    def _check_nodding(self):
        """相槌チェック"""
        current_time = time.time()
        if current_time - self.last_nodding_time >= Config.NODDING_INTERVAL:
            self.last_nodding_time = current_time
            # VRMアバターに相槌指示を送信
            self._send_vrm_command("nod")
    
    def _send_vrm_command(self, command):
        """VRMアバターにコマンドを送信"""
        # 実際の実装ではWebSocketやAPI経由でVRMに指示を送信
        if command == "nod":
            # 軽く頷くモーション
            pass
        elif command == "thinking":
            # 考え中モーション
            pass
    
    def stop_recording(self):
        """録音停止"""
        if not self.is_recording:
            return False
        
        self.is_recording = False
        
        # 最後のセグメントを処理
        if self.voice_buffer.current_segment_start:
            self.voice_buffer.end_segment()
        
        # 残りのバッファを処理
        if self.voice_buffer.speech_segments:
            self._process_buffered_speech()
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
            self.processing_thread = None
        
        return True
    
    def _process_buffered_speech(self):
        """バッファされた音声を処理"""
        try:
            combined_audio = self.voice_buffer.get_combined_audio()
            speech_info = self.voice_buffer.get_speech_info()
            
            if combined_audio and speech_info:
                # 音声データをWAVファイルに変換
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    with wave.open(tmp_file.name, 'wb') as wf:
                        wf.setnchannels(Config.AUDIO_CHANNELS)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(Config.AUDIO_SAMPLE_RATE)
                        wf.writeframes(combined_audio)
                        wf.close()
                    
                    # Whisperで転記
                    result = self.whisper_model.transcribe(
                        tmp_file.name,
                        language="ja",
                        word_timestamps=True,
                        temperature=0.0,
                        beam_size=5
                    )
                    
                    # 一時ファイルを削除
                    os.unlink(tmp_file.name)
                    
                    # 結果をセッションに保存
                    st.session_state.last_transcription = result
                    st.session_state.speech_info = speech_info
                    
                    # バッファをリセット
                    self.voice_buffer.reset()
                    
                    return result
            
        except Exception as e:
            st.error(f"❌ バッファ処理エラー: {str(e)}")
            return None
    
    def get_status(self):
        """現在のステータスを取得"""
        return {
            "is_recording": self.is_recording,
            "buffer_segments": len(self.voice_buffer.speech_segments),
            "total_duration": self.voice_buffer.total_duration,
            "last_speech_end": self.voice_buffer.last_speech_end
        }

class SmartVoiceAIAgent:
    """スマート音声AIエージェント"""
    
    def __init__(self):
        self.ai_agent = AIAgent()
        self.voice_input = SmartVoiceInputHandler()
        self.current_conversation = []
        
    def initialize(self):
        """AIエージェント初期化"""
        try:
            # 音声入力システム初期化
            if not self.voice_input.initialize():
                return False
            
            return True
        except Exception as e:
            return False
    
    def process_voice_input(self):
        """音声入力処理"""
        try:
            if self.voice_input.is_recording:
                status = self.voice_input.get_status()
                
                # 待機状態の表示
                if status["last_speech_end"]:
                    time_since_last_speech = time.time() - status["last_speech_end"]
                    if time_since_last_speech < Config.MAX_PAUSE_DURATION:
                        return "まだ聞いてるよ...続きを待機中です。"
                    else:
                        return "まだ聞いてるよ...新しい発話を待っています。"
                else:
                    return "まだ聞いてるよ...話してください。"
            
            return None
            
        except Exception as e:
            return f"❌ 音声入力処理エラー: {str(e)}"
    
    def generate_response(self, transcription_text):
        """AI応答生成"""
        try:
            if not transcription_text:
                return "音声が認識できませんでした。もう一度お試しください。"
            
            # llama3.2で応答生成
            prompt = f"""あなたはスマート音声AIアシスタントです。ユーザーの音声入力に基づいて、自然で丁寧な応答を生成してください。

ユーザーの音声入力: {transcription_text}

音声の特徴:
- セグメント数: {len(self.voice_input.voice_buffer.speech_segments)}
- 総時間: {self.voice_input.voice_buffer.total_duration:.1f}秒

ユーザーのペースを尊重し、適切なタイミングで応答してください。自然な対話を心がけてください。"""
            
            response = self.ai_agent.generate_response(prompt)
            
            return response
            
        except Exception as e:
            return f"❌ 応答生成エラー: {str(e)}"

def render_smart_voice_interface(ai_agent):
    """スマート音声インターフェース"""
    st.header("🎤️ スマート音声入力システム")
    
    # 入力方法の選択
    input_method = st.radio(
        "🎯 入力方法を選択",
        ["🎤️ 音声入力", "⌨️ テキスト入力", "🔄 両方使用"],
        horizontal=True
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if input_method in ["🎤️ 音声入力", "🔄 両方使用"]:
            st.subheader("🎤️ 音声録音")
            
            # 録音コントロール
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎤️ 録音開始", key="start_smart_recording"):
                    if ai_agent.voice_input.start_recording():
                        st.success("✅ 録音開始")
                        st.session_state.recording_status = "recording"
                    else:
                        st.error("❌ 録音開始失敗")
            
            with col2:
                if st.button("⏹️ 録音停止", key="stop_smart_recording"):
                    if ai_agent.voice_input.stop_recording():
                        st.success("✅ 録音停止")
                        st.session_state.recording_status = "stopped"
                    else:
                        st.error("❌ 録音停止失敗")
            
            with col3:
                auto_process = st.checkbox("🔄 自動処理", value=True, help="音声の途切れを自動で検出")
            
            # 録音状態表示
            if st.session_state.get("recording_status") == "recording":
                st.info("🔴 録音中...")
                
                # リアルタイムステータス
                status = ai_agent.voice_input.get_status()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("セグメント数", status["buffer_segments"])
                
                with col2:
                    st.metric("総時間", f"{status['total_duration']:.1f}秒")
                
                with col3:
                    if status["last_speech_end"]:
                        time_since = time.time() - status["last_speech_end"]
                        st.metric("前回発話から", f"{time_since:.1f}秒前")
                    else:
                        st.metric("状態", "発話中")
                
                # 待機状態の表示
                if auto_process:
                    waiting_message = ai_agent.process_voice_input()
                    if waiting_message:
                        st.info(f"💭 {waiting_message}")
            
            # 転記結果表示
            if st.session_state.get("last_transcription"):
                transcription = st.session_state.last_transcription
                speech_info = st.session_state.get("speech_info", {})
                
                st.subheader("📝 音声転記結果")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**認識テキスト**: {transcription['text']}")
                    st.write(f"**処理時間**: {transcription.get('time', 'N/A')}秒")
                    
                    if speech_info:
                        st.write(f"**セグメント数**: {speech_info['segments_count']}")
                        st.write(f"**総時間**: {speech_info['total_duration']:.1f}秒")
                
                with col2:
                    # AI応答生成
                    if st.button("🤖 AI応答生成", key="generate_ai_response_voice"):
                        with st.spinner("🤖 AI応答生成中..."):
                            ai_response = ai_agent.generate_response(transcription['text'])
                            st.session_state.ai_response = ai_response
                            st.success("✅ AI応答生成完了")
                    
                    # AI応答表示
                    if st.session_state.get("ai_response"):
                        st.subheader("🤖 AI応答")
                        st.write(st.session_state.ai_response)
                        
                        # 音声読み上げ
                        if st.button("🔊 音声読み上げ", key="speak_response"):
                            try:
                                import pyttsx3
                                engine = pyttsx3.init()
                                engine.say(st.session_state.ai_response)
                                engine.runAndWait()
                                st.success("✅ 音声読み上げ完了")
                            except Exception as e:
                                st.error(f"音声読み上げエラー: {str(e)}")
        
        if input_method in ["⌨️ テキスト入力", "🔄 両方使用"]:
            st.subheader("⌨️ テキスト入力")
            
            # テキスト入力欄
            user_input = st.text_area(
                "💬 メッセージを入力してください",
                key="text_input",
                height=100,
                placeholder="ここにメッセージを入力..."
            )
            
            # 入力コントロール
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 送信", key="send_text", type="primary"):
                    if user_input.strip():
                        with st.spinner("🤖 AI応答生成中..."):
                            ai_response = ai_agent.generate_response(user_input)
                            st.session_state.text_ai_response = ai_response
                            st.session_state.last_text_input = user_input
                            st.success("✅ AI応答生成完了")
                    else:
                        st.warning("⚠️ メッセージを入力してください")
            
            with col2:
                if st.button("🗑️ クリア", key="clear_text"):
                    st.session_state.text_input = ""
                    st.session_state.text_ai_response = ""
                    st.success("✅ 入力をクリアしました")
            
            with col3:
                if st.button("📋 履歴", key="show_history"):
                    if "conversation_history" not in st.session_state:
                        st.session_state.conversation_history = []
                    
                    if st.session_state.conversation_history:
                        st.write("📜 対話履歴:")
                        for i, (user_msg, ai_msg) in enumerate(st.session_state.conversation_history[-5:], 1):
                            st.write(f"{i}. **ユーザー**: {user_msg}")
                            st.write(f"   **AI**: {ai_msg}")
                    else:
                        st.info("📝 履歴がありません")
            
            # テキストAI応答表示
            if st.session_state.get("text_ai_response"):
                st.subheader("🤖 AI応答")
                st.write(st.session_state.text_ai_response)
                
                # 音声読み上げ
                if st.button("🔊 音声読み上げ", key="speak_text_response"):
                    try:
                        import pyttsx3
                        engine = pyttsx3.init()
                        engine.say(st.session_state.text_ai_response)
                        engine.runAndWait()
                        st.success("✅ 音声読み上げ完了")
                    except Exception as e:
                        st.error(f"音声読み上げエラー: {str(e)}")
                
                # 履歴に保存
                if st.session_state.get("last_text_input"):
                    if "conversation_history" not in st.session_state:
                        st.session_state.conversation_history = []
                    
                    st.session_state.conversation_history.append(
                        (st.session_state.last_text_input, st.session_state.text_ai_response)
                    )
                    
                    # 履歴を最新の10件に制限
                    if len(st.session_state.conversation_history) > 10:
                        st.session_state.conversation_history = st.session_state.conversation_history[-10:]
    
    with col2:
        st.subheader("📊 バッファリング設定")
        
        # 設定表示
        st.write("**現在の設定**:")
        st.write(f"- 最小発話時間: {Config.MIN_SPEECH_DURATION}秒")
        st.write(f"- 最大休止時間: {Config.MAX_PAUSE_DURATION}秒")
        st.write(f"- バッファタイムアウト: {Config.BUFFER_TIMEOUT}秒")
        st.write(f"- VAD閾値: {Config.VAD_SILENCE_THRESHOLD}")
        st.write(f"- 相槌間隔: {Config.NODDING_INTERVAL}秒")
        
        # 設定調整（オプション）
        with st.expander("詳細設定"):
            min_speech = st.slider("最小発話時間", 0.5, 5.0, Config.MIN_SPEECH_DURATION)
            max_pause = st.slider("最大休止時間", 0.5, 5.0, Config.MAX_PAUSE_DURATION)
            nodding_interval = st.slider("相槌間隔", 0.5, 3.0, Config.NODDING_INTERVAL)
            
            if st.button("設定を保存", key="save_settings"):
                # 設定を保存（実際の実装では設定ファイルに保存）
                st.success("✅ 設定を保存しました")
        
        # ステータス履歴
        if st.session_state.get("recording_history"):
            st.subheader("📈 録音履歴")
            for i, record in enumerate(st.session_state.recording_history[-5:]):
                st.write(f"{i+1}. {record}")
        
        # 対話統計
        if "conversation_history" in st.session_state and st.session_state.conversation_history:
            st.subheader("📈 対話統計")
            total_conversations = len(st.session_state.conversation_history)
            st.metric("総対話数", total_conversations)
            
            # 最新の対話
            if st.session_state.conversation_history:
                latest_user, latest_ai = st.session_state.conversation_history[-1]
                st.write("**最新の対話**:")
                st.write(f"👤 ユーザー: {latest_user[:50]}...")
                st.write(f"🤖 AI: {latest_ai[:50]}...")

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🎤️ Smart Voice AI Agent",
        page_icon="🎤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤️ AI Agent System - スマート音声入力版")
    st.markdown("### 🎯 スマート・バッファリングによる自然な対話")
    
    # システム初期化
    if 'ai_agent' not in st.session_state:
        with st.spinner("🎤️ スマート音声AIシステム初期化中..."):
            ai_agent = SmartVoiceAIAgent()
            if ai_agent.initialize():
                st.session_state.ai_agent = ai_agent
                st.success("✅ スマート音声AIシステム初期化完了")
            else:
                st.error("❌ AIシステム初期化失敗")
                st.stop()
    
    ai_agent = st.session_state.ai_agent
    
    # サイドバー
    with st.sidebar:
        st.subheader("⚙️ スマート音声設定")
        
        # モデル情報
        st.write("**使用モデル**:")
        st.write(f"- Whisper: {Config.WHISPER_MODEL}")
        st.write(f"- AI: {Config.MAIN_MODEL}")
        
        # バッファリング設定
        st.write("**バッファリング設定**:")
        st.write(f"- 最小発話時間: {Config.MIN_SPEECH_DURATION}秒")
        st.write(f"- 最大休止時間: {Config.MAX_PAUSE_DURATION}秒")
        st.write(f"- VAD閾値: {Config.VAD_SILENCE_THRESHOLD}")
        
        # ステータス
        if ai_agent.voice_input.is_recording:
            status = ai_agent.voice_input.get_status()
            st.write("**現在のステータス**:")
            st.write(f"- 録音中: {status['is_recording']}")
            st.write(f"- バッファセグメント: {status['buffer_segments']}")
            st.write(f"- 総時間: {status['total_duration']:.1f}秒")
    
    # メインインターフェース
    render_smart_voice_interface(ai_agent)
    
    # フッター情報
    st.markdown("---")
    st.markdown(f"**🎤️ スマート音声AI**: {Config.MAIN_MODEL}")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🎯 目標**: スマート・バッファリングによる自然な対話と高い包容力")

if __name__ == "__main__":
    main()
