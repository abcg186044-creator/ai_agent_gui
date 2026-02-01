#!/usr/bin/env python3
"""
Voice-Fixed AI Agent - 音声合成修正版
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
import socket
import subprocess
from urllib.parse import urlparse

# 修正版動的インストーラーのインポート
sys.path.append('/app/scripts')
try:
    from dynamic_installer_fixed import install_package, auto_install_missing_packages, DynamicInstallerFixed
except ImportError:
    st.error("❌ 修正版動的インストーラーが見つかりません")
    sys.exit(1)

# 必要なライブラリの動的インストール
def install_required_packages_fixed():
    pytorch_packages = {
        'torch': '2.1.0',
        'torchaudio': '2.1.0',
        'torchvision': '0.16.0'
    }
    
    other_packages = [
        'sounddevice',
        'faster-whisper',
        'pyttsx3'
    ]
    
    installer = DynamicInstallerFixed()
    
    # PyTorchパッケージの特別処理 - まとめてインストール
    st.info("🔧 Checking PyTorch packages...")
    pytorch_success = True
    
    for package, version in pytorch_packages.items():
        try:
            import_name = package.replace('-', '_')
            importlib.import_module(import_name)
            st.success(f"✅ {package} is already installed")
        except ImportError:
            st.info(f"📦 Installing {package}=={version}...")
            success, message = installer.install_package(package, version, force_version=True)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                pytorch_success = False
    
    # PyTorchパッケージのインポート確認
    if pytorch_success:
        st.info("🔍 Verifying PyTorch packages...")
        importlib.invalidate_caches()  # キャッシュをクリア
        
        for package in pytorch_packages.keys():
            try:
                import_name = package.replace('-', '_')
                importlib.import_module(import_name)
                st.success(f"✅ {package} imported successfully")
            except ImportError as e:
                st.error(f"❌ Failed to import {package}: {e}")
                # PyTorch競合解決を試行
                st.info("🔧 Attempting to resolve PyTorch conflicts...")
                success, module = installer.handle_pytorch_conflict(package)
                if success:
                    st.success(f"✅ {package} conflict resolved")
                else:
                    st.error(f"❌ Failed to resolve {package} conflict")
                    return False
    
    # その他のパッケージをインストール
    for package in other_packages:
        try:
            importlib.import_module(package)
            st.success(f"✅ {package} is already installed")
        except ImportError:
            st.info(f"📦 Installing {package}...")
            success, message = installer.install_package(package)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                return False
    
    return True

if not install_required_packages_fixed():
    st.error("❌ 必要なライブラリのインストールに失敗しました")
    st.stop()

# ライブラリのインポート
def safe_import_with_retry(package_name, import_name=None, max_retries=3):
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    for attempt in range(max_retries):
        try:
            module = importlib.import_module(import_name)
            print(f"✅ {package_name} imported successfully")
            return module
        except ImportError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ {package_name} import failed, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(1)
                importlib.invalidate_caches()
            else:
                st.error(f"❌ {package_name}のインポートに失敗しました: {e}")
                return None

try:
    sounddevice = safe_import_with_retry('sounddevice', 'sd')
    if sounddevice is None:
        st.error("❌ sounddeviceのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ sounddeviceのインポートエラー: {e}")
    sys.exit(1)

try:
    faster_whisper = safe_import_with_retry('faster-whisper', 'faster_whisper')
    if faster_whisper is None:
        st.error("❌ faster-whisperのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ faster-whisperのインポートエラー: {e}")
    sys.exit(1)

try:
    torch = safe_import_with_retry('torch', 'torch')
    if torch is None:
        st.error("❌ torchのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ torchのインポートエラー: {e}")
    sys.exit(1)

try:
    torchaudio = safe_import_with_retry('torchaudio', 'torchaudio')
    if torchaudio is None:
        st.error("❌ torchaudioのインポートに失敗しました")
        sys.exit(1)
except Exception as e:
    st.error(f"❌ torchaudioのインポートエラー: {e}")
    sys.exit(1)

# 設定
class Config:
    MAIN_MODEL = "llama3.2"
    WHISPER_MODEL = "large-v3"
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_FORMAT = "int16"
    VAD_SILENCE_THRESHOLD = 0.5
    MIN_SPEECH_DURATION = 2.0
    MAX_PAUSE_DURATION = 2.0
    BUFFER_TIMEOUT = 5.0
    NODDING_INTERVAL = 1.0

class VoiceSynthesizer:
    """音声合成クラス - 複数エンジン対応"""
    
    def __init__(self):
        self.engines = {}
        self.current_engine = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """音声合成エンジンを初期化"""
        # pyttsx3エンジン
        try:
            import pyttsx3
            self.engines['pyttsx3'] = pyttsx3.init()
            self.engines['pyttsx3'].setProperty('rate', 150)
            self.engines['pyttsx3'].setProperty('volume', 0.9)
            print("✅ pyttsx3 engine initialized")
        except Exception as e:
            print(f"❌ pyttsx3 initialization failed: {e}")
        
        # VOICEVOXエンジン
        try:
            self.engines['voicevox'] = {
                'url': 'http://voicevox:50021',
                'available': False
            }
            # VOICEVOXの接続テスト
            response = requests.get(f"{self.engines['voicevox']['url']}/docs", timeout=5)
            if response.status_code == 200:
                self.engines['voicevox']['available'] = True
                print("✅ VOICEVOX engine initialized")
            else:
                print("❌ VOICEVOX not available")
        except Exception as e:
            print(f"❌ VOICEVOX initialization failed: {e}")
        
        # デフォルトエンジンを設定
        if self.engines.get('voicevox', {}).get('available'):
            self.current_engine = 'voicevox'
        elif 'pyttsx3' in self.engines:
            self.current_engine = 'pyttsx3'
        else:
            self.current_engine = None
    
    def get_available_engines(self):
        """利用可能なエンジンを取得"""
        available = {}
        for name, engine in self.engines.items():
            if name == 'voicevox':
                available[name] = engine.get('available', False)
            else:
                available[name] = engine is not None
        return available
    
    def set_engine(self, engine_name):
        """音声合成エンジンを設定"""
        if engine_name in self.engines:
            if engine_name == 'voicevox':
                if self.engines['voicevox']['available']:
                    self.current_engine = engine_name
                    return True
            else:
                if self.engines[engine_name] is not None:
                    self.current_engine = engine_name
                    return True
        return False
    
    def synthesize(self, text):
        """音声を合成"""
        if not self.current_engine:
            return False, "No available TTS engine"
        
        try:
            if self.current_engine == 'pyttsx3':
                return self._synthesize_pyttsx3(text)
            elif self.current_engine == 'voicevox':
                return self._synthesize_voicevox(text)
            else:
                return False, "Unknown TTS engine"
        except Exception as e:
            return False, f"TTS error: {str(e)}"
    
    def _synthesize_pyttsx3(self, text):
        """pyttsx3で音声合成"""
        try:
            engine = self.engines['pyttsx3']
            engine.say(text)
            engine.runAndWait()
            return True, "pyttsx3 synthesis completed"
        except Exception as e:
            return False, f"pyttsx3 error: {str(e)}"
    
    def _synthesize_voicevox(self, text):
        """VOICEVOXで音声合成"""
        try:
            # 音声合成クエリ
            query_response = requests.post(
                f"{self.engines['voicevox']['url']}/audio_query",
                params={
                    'text': text,
                    'speaker': 0
                },
                timeout=10
            )
            
            if query_response.status_code != 200:
                return False, f"VOICEVOX query failed: {query_response.status_code}"
            
            # 音声合成
            audio_response = requests.post(
                f"{self.engines['voicevox']['url']}/synthesis",
                json=query_response.json(),
                timeout=30
            )
            
            if audio_response.status_code != 200:
                return False, f"VOICEVOX synthesis failed: {audio_response.status_code}"
            
            # 音声を再生
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_response.content)
                tmp_file.flush()
                
                # 音声再生
                try:
                    subprocess.run(['aplay', tmp_file.name], check=True, timeout=30)
                    return True, "VOICEVOX synthesis completed"
                except subprocess.CalledProcessError as e:
                    return False, f"Audio playback failed: {str(e)}"
                finally:
                    os.unlink(tmp_file.name)
                    
        except Exception as e:
            return False, f"VOICEVOX error: {str(e)}"

class NetworkAwareAIAgent:
    """ネットワーク対応AIエージェント"""
    
    def __init__(self):
        self.base_urls = []
        self.current_url_index = 0
        self.timeout = 30
        self.max_retries = 3
        self._initialize_urls()
    
    def _initialize_urls(self):
        self.base_urls.append("http://ollama:11434")
        host_ip = os.getenv('HOST_IP', 'localhost')
        self.base_urls.append(f"http://{host_ip}:11434")
        self.base_urls.append("http://localhost:11434")
        
        try:
            host_ip = self._get_host_ip()
            if host_ip and host_ip not in [url.split('//')[1].split(':')[0] for url in self.base_urls]:
                self.base_urls.append(f"http://{host_ip}:11434")
        except:
            pass
    
    def _get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            host_ip = s.getsockname()[0]
            s.close()
            return host_ip
        except:
            return None
    
    def _test_connection(self, url):
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_working_url(self):
        if hasattr(self, '_last_working_url') and self._test_connection(self._last_working_url):
            return self._last_working_url
        
        for url in self.base_urls:
            if self._test_connection(url):
                self._last_working_url = url
                return url
        
        return None
    
    def generate_response(self, prompt, model="llama3.2"):
        working_url = self._get_working_url()
        
        if not working_url:
            return "❌ Ollamaサーバーに接続できません。"
        
        for attempt in range(self.max_retries):
            try:
                data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                
                response = requests.post(
                    f"{working_url}/api/generate",
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '')
                else:
                    if attempt < self.max_retries - 1:
                        working_url = self._get_working_url()
                        if not working_url:
                            break
                    else:
                        return f"❌ 応答生成エラー: HTTP {response.status_code}"
                        
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    working_url = self._get_working_url()
                    if not working_url:
                        break
                    time.sleep(1)
                else:
                    return "❌ Ollamaサーバーへの接続に失敗しました。"
            except Exception as e:
                return f"❌ 応答生成エラー: {str(e)}"
        
        return "❌ すべての接続試行が失敗しました。"

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
        self.current_segment_start = time.time()
        
    def end_segment(self):
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
        self.audio_buffer.extend(audio_data)
    
    def should_process_speech(self):
        if not self.speech_segments:
            return False
        
        if self.last_speech_end:
            time_since_last_speech = time.time() - self.last_speech_end
            return time_since_last_speech >= Config.MAX_PAUSE_DURATION
        
        return False
    
    def get_combined_audio(self):
        if not self.speech_segments:
            return None
        
        combined_audio = []
        for segment in self.speech_segments:
            combined_audio.extend(segment["audio_data"])
        
        return combined_audio
    
    def reset(self):
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
        
    def initialize(self):
        try:
            self.whisper_model = faster_whisper.WhisperModel(
                Config.WHISPER_MODEL,
                device="cuda" if self._check_cuda() else "cpu",
                compute_type="float32"
            )
            
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
        try:
            return torch.cuda.is_available()
        except:
            return False
    
    def start_recording(self):
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.voice_buffer.reset()
        
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
        try:
            with sounddevice.InputStream(
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
                            if self.vad_model is not None:
                                audio_tensor = torch.from_numpy(np.array(audio_data, dtype=np.float32))
                                speech_prob = self.vad_model(audio_tensor, Config.AUDIO_SAMPLE_RATE).item()
                            else:
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
        try:
            combined_audio = self.voice_buffer.get_combined_audio()
            
            if combined_audio and self.whisper_model:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    with wave.open(tmp_file.name, 'wb') as wf:
                        wf.setnchannels(Config.AUDIO_CHANNELS)
                        wf.setsampwidth(2)
                        wf.setframerate(Config.AUDIO_SAMPLE_RATE)
                        wf.writeframes(combined_audio)
                        wf.close()
                    
                    result = self.whisper_model.transcribe(
                        tmp_file.name,
                        language="ja",
                        word_timestamps=True,
                        temperature=0.0,
                        beam_size=5
                    )
                    
                    os.unlink(tmp_file.name)
                    
                    st.session_state.last_transcription = result
                    self.voice_buffer.reset()
                    
                    return result
            
        except Exception as e:
            st.error(f"❌ バッファ処理エラー: {str(e)}")
            return None
    
    def stop_recording(self):
        if not self.is_recording:
            return False
        
        self.is_recording = False
        
        if self.voice_buffer.current_segment_start:
            self.voice_buffer.end_segment()
        
        if self.voice_buffer.speech_segments:
            self._process_buffered_speech()
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
            self.processing_thread = None
        
        return True
    
    def get_status(self):
        return {
            "is_recording": self.is_recording,
            "buffer_segments": len(self.voice_buffer.speech_segments),
            "total_duration": self.voice_buffer.total_duration,
            "last_speech_end": self.voice_buffer.last_speech_end
        }

class VoiceFixedAIAgent:
    """音声修正版AIエージェント"""
    
    def __init__(self):
        self.ai_agent = NetworkAwareAIAgent()
        self.voice_input = SmartVoiceInputHandler()
        self.voice_synthesizer = VoiceSynthesizer()
        
    def initialize(self):
        try:
            if not self.voice_input.initialize():
                return False
            return True
        except Exception as e:
            return False
    
    def generate_response(self, transcription_text):
        try:
            if not transcription_text:
                return "音声が認識できませんでした。もう一度お試しください。"
            
            prompt = f"""あなたはスマート音声AIアシスタントです。ユーザーの音声入力に基づいて、自然で丁寧な応答を生成してください。

ユーザーの音声入力: {transcription_text}

ユーザーのペースを尊重し、適切なタイミングで応答してください。自然な対話を心がけてください。"""
            
            response = self.ai_agent.generate_response(prompt)
            return response
            
        except Exception as e:
            return f"❌ 応答生成エラー: {str(e)}"
    
    def speak_response(self, text):
        """応答を音声で出力"""
        success, message = self.voice_synthesizer.synthesize(text)
        return success, message

def render_voice_status(voice_synthesizer):
    """音声合成状態表示"""
    st.subheader("🔊 音声合成状態")
    
    available_engines = voice_synthesizer.get_available_engines()
    current_engine = voice_synthesizer.current_engine
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**利用可能なエンジン**:")
        for engine, available in available_engines.items():
            if available:
                st.success(f"✅ {engine}")
            else:
                st.error(f"❌ {engine}")
    
    with col2:
        st.write("**現在のエンジン**:")
        if current_engine:
            st.success(f"🎯 {current_engine}")
        else:
            st.error("❌ 利用可能なエンジンがありません")
    
    # エンジン切り替え
    engine_options = [name for name, available in available_engines.items() if available]
    if engine_options:
        selected_engine = st.selectbox(
            "音声合成エンジンを選択",
            engine_options,
            index=engine_options.index(current_engine) if current_engine in engine_options else 0
        )
        
        if selected_engine != current_engine:
            if voice_synthesizer.set_engine(selected_engine):
                st.success(f"✅ {selected_engine} に切り替えました")
                st.rerun()
            else:
                st.error(f"❌ {selected_engine} への切り替えに失敗しました")

def render_voice_interface(ai_agent):
    """音声インターフェース"""
    st.header("🎤️ 音声修正版AIエージェント")
    
    # 音声合成状態表示
    render_voice_status(ai_agent.voice_synthesizer)
    
    # 入力方法の選択
    input_method = st.radio(
        "🎯 入力方法を選択",
        ["🎤️ 音声入力", "⌨️ テキスト入力"],
        horizontal=True
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if input_method == "🎤️ 音声入力":
            st.subheader("🎤️ 音声録音")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎤️ 録音開始", key="start_voice_recording"):
                    if ai_agent.voice_input.start_recording():
                        st.success("✅ 録音開始")
                        st.session_state.recording_status = "recording"
                    else:
                        st.error("❌ 録音開始失敗")
            
            with col2:
                if st.button("⏹️ 録音停止", key="stop_voice_recording"):
                    if ai_agent.voice_input.stop_recording():
                        st.success("✅ 録音停止")
                        st.session_state.recording_status = "stopped"
                    else:
                        st.error("❌ 録音停止失敗")
            
            # 録音状態表示
            if st.session_state.get("recording_status") == "recording":
                st.info("🔴 録音中...")
                
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
            
            # 転記結果表示
            if st.session_state.get("last_transcription"):
                transcription = st.session_state.last_transcription
                
                st.subheader("📝 音声転記結果")
                st.write(f"**認識テキスト**: {transcription['text']}")
                st.write(f"**処理時間**: {transcription.get('time', 'N/A')}秒")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🤖 AI応答生成", key="generate_ai_response_voice"):
                        with st.spinner("🤖 AI応答生成中..."):
                            ai_response = ai_agent.generate_response(transcription['text'])
                            st.session_state.ai_response = ai_response
                            st.success("✅ AI応答生成完了")
                
                with col2:
                    if st.session_state.get("ai_response"):
                        if st.button("🔊 音声読み上げ", key="speak_response"):
                            with st.spinner("🔊 音声合成中..."):
                                success, message = ai_agent.speak_response(st.session_state.ai_response)
                                if success:
                                    st.success("✅ 音声読み上げ完了")
                                else:
                                    st.error(f"❌ 音声読み上げ失敗: {message}")
                
                # AI応答表示
                if st.session_state.get("ai_response"):
                    st.subheader("🤖 AI応答")
                    st.write(st.session_state.ai_response)
        
        elif input_method == "⌨️ テキスト入力":
            st.subheader("⌨️ テキスト入力")
            
            user_input = st.text_area(
                "💬 メッセージを入力してください",
                key="text_input",
                height=100,
                placeholder="ここにメッセージを入力..."
            )
            
            col1, col2 = st.columns(2)
            
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
            
            # テキストAI応答表示
            if st.session_state.get("text_ai_response"):
                st.subheader("🤖 AI応答")
                st.write(st.session_state.text_ai_response)
                
                if st.button("🔊 音声読み上げ", key="speak_text_response"):
                    with st.spinner("🔊 音声合成中..."):
                        success, message = ai_agent.speak_response(st.session_state.text_ai_response)
                        if success:
                            st.success("✅ 音声読み上げ完了")
                        else:
                            st.error(f"❌ 音声読み上げ失敗: {message}")
    
    with col2:
        st.subheader("📊 システム情報")
        
        # PyTorchバージョン情報
        st.write("**PyTorchバージョン情報**:")
        st.write(f"- torch: {torch.__version__}")
        st.write(f"- torchaudio: {torchaudio.__version__}")
        
        # CUDA情報
        if torch.cuda.is_available():
            st.write(f"- CUDA: 利用可能")
            st.write(f"- GPU数: {torch.cuda.device_count()}")
        else:
            st.write("- CUDA: 利用不可")
        
        # 音声デバイス情報
        try:
            devices = sounddevice.query_devices()
            st.write("**音声デバイス**:")
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    st.write(f"- 入力 {i}: {device['name']}")
                if device['max_output_channels'] > 0:
                    st.write(f"- 出力 {i}: {device['name']}")
        except Exception as e:
            st.write(f"- 音声デバイス情報取得エラー: {e}")

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🔊 Voice-Fixed AI Agent",
        page_icon="🔊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔊 Voice-Fixed AI Agent")
    st.markdown("### 音声合成修正版 - eSpeak/VOICEVOX対応")
    
    # セッション状態初期化
    if 'agent' not in st.session_state:
        st.session_state.agent = VoiceFixedAIAgent()
        
        # AIエージェント初期化
        with st.spinner("🤖 AIエージェントを初期化中..."):
            if st.session_state.agent.initialize():
                st.success("✅ AIエージェント初期化完了")
            else:
                st.error("❌ AIエージェント初期化失敗")
                st.stop()
    
    # メインインターフェース
    render_voice_interface(st.session_state.agent)

if __name__ == "__main__":
    main()
