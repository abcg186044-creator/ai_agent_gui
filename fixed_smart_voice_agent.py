#!/usr/bin/env python3
"""
Fixed Smart Voice AI Agent - Ollama接続修正版
"""

import streamlit as st
import time
import threading
import numpy as np
import requests
import json
import queue
import tempfile
import wave
import os
import sys
import importlib

# 動的インストーラーのインポート
sys.path.append('/app/scripts')
try:
    from dynamic_installer import install_package, auto_install_missing_packages, DynamicInstaller
except ImportError:
    st.error("❌ 動的インストーラーが見つかりません")
    sys.exit(1)

# 必要なライブラリの動的インストール
def install_required_packages():
    """必要なライブラリを動的にインストール"""
    required_packages = [
        'sounddevice',
        'faster-whisper',
        'torch',
        'torchaudio',
        'pyttsx3'
    ]
    
    installer = DynamicInstaller()
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            success, message = install_package(package)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
                return False
    
    return True

# ライブラリのインストールを試行
if not install_required_packages():
    st.error("❌ 必要なライブラリのインストールに失敗しました")
    st.stop()

# ライブラリのインポート
try:
    import sounddevice as sd
    print("✅ sounddevice imported successfully")
except ImportError as e:
    st.error(f"❌ sounddeviceのインポートに失敗しました: {e}")
    st.stop()

try:
    from faster_whisper import WhisperModel
    print("✅ faster-whisper imported successfully")
except ImportError as e:
    st.error(f"❌ faster-whisperのインポートに失敗しました: {e}")
    st.stop()

try:
    import torch
    print("✅ torch imported successfully")
except ImportError as e:
    st.error(f"❌ torchのインポートに失敗しました: {e}")
    st.stop()

try:
    import torchaudio
    print("✅ torchaudio imported successfully")
except ImportError as e:
    st.error(f"❌ torchaudioのインポートに失敗しました: {e}")
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

class AIAgent:
    """AIエージェント - requests使用版"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.timeout = 30
    
    def generate_response(self, prompt, model="llama3.2"):
        """AI応答を生成（requests使用）"""
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return f"❌ 応答生成エラー: HTTP {response.status_code}"
                
        except Exception as e:
            return f"❌ 応答生成エラー: {str(e)}"

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
            self.whisper_model = WhisperModel(
                Config.WHISPER_MODEL,
                device="cuda" if self._check_cuda() else "cpu",
                compute_type="float32"
            )
            
            # VADモデル読み込み
            try:
                self.vad_model, utils = torch.hub.load(
                    'snakers4/silero-vad',
                    'silero_vad',
                    force_reload=True
                )
                self.vad_utils = utils
            except Exception as vad_error:
                st.warning(f"⚠️ VADモデル読み込みエラー: {vad_error}")
                self.vad_model = None
            
            return True
        except Exception as e:
            st.error(f"❌ 音声入力システム初期化エラー: {str(e)}")
            return False
    
    def _check_cuda(self):
        """CUDA利用可能かチェック"""
        try:
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
            with sd.InputStream(
                samplerate=Config.AUDIO_SAMPLE_RATE,
                channels=Config.AUDIO_CHANNELS,
                dtype=Config.AUDIO_FORMAT,
                blocksize=1024,
                callback=callback
            ) as stream:
                while self.is_recording:
                    try:
                        audio_data = self.audio_queue.get(timeout=1.0)
                        
                        if audio_data is not None and len(audio_data) > 0:
                            # VADで音声活動検出
                            if self.vad_model is not None:
                                audio_tensor = torch.from_numpy(np.array(audio_data, dtype=np.float32))
                                speech_prob = self.vad_model(audio_tensor, Config.AUDIO_SAMPLE_RATE).item()
                            else:
                                # 簡易的な音声検出
                                audio_array = np.array(audio_data)
                                energy = np.sqrt(np.mean(audio_array**2))
                                speech_prob = 1.0 if energy > 0.01 else 0.0
                            
                            if speech_prob > Config.VAD_SILENCE_THRESHOLD:
                                if not self.voice_buffer.current_segment_start:
                                    self.voice_buffer.start_segment()
                                
                                self.voice_buffer.add_audio_data(audio_data)
                            else:
                                if self.voice_buffer.current_segment_start:
                                    self.voice_buffer.end_segment()
                                
                                if self.voice_buffer.should_process_speech():
                                    self._process_buffered_speech()
                    
                    except queue.Empty:
                        continue
                    except Exception as e:
                        st.error(f"❌ 音声処理エラー: {str(e)}")
                        continue
                        
        except Exception as e:
            st.error(f"❌ 録音エラー: {str(e)}")
            self.is_recording = False
    
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

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🎤️ Fixed Smart Voice AI Agent",
        page_icon="🎤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤️ Fixed Smart Voice AI Agent")
    st.markdown("### Ollama接続修正版 - スマート音声入力システム")
    
    # セッション状態初期化
    if 'agent' not in st.session_state:
        st.session_state.agent = SmartVoiceAIAgent()
        
        # AIエージェント初期化
        with st.spinner("🤖 AIエージェントを初期化中..."):
            if st.session_state.agent.initialize():
                st.success("✅ AIエージェント初期化完了")
            else:
                st.error("❌ AIエージェント初期化失敗")
                st.stop()
    
    # メインインターフェース
    render_smart_voice_interface(st.session_state.agent)

if __name__ == "__main__":
    main()
