#!/usr/bin/env python3
"""
Self-Healing Smart Voice AI Agent - 動的ライブラリインストール対応版
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
import traceback

# 動的インストーラーのインポート
sys.path.append('/app/scripts')
try:
    from dynamic_installer import install_package, auto_install_missing_packages, DynamicInstaller
except ImportError:
    st.error("❌ 動的インストーラーが見つかりません")
    sys.exit(1)

class SelfHealingAIAgent:
    """自己修復型AIエージェント"""
    
    def __init__(self):
        self.installer = DynamicInstaller()
        self.required_packages = {
            'sounddevice': 'sd',
            'faster-whisper': 'WhisperModel',
            'torch': 'torch',
            'torchaudio': 'torchaudio',
            'pyttsx3': 'pyttsx3'
        }
        self.installed_packages = {}
        self.install_notifications = []
        
    def install_package_with_retry(self, package_name, max_retries=3):
        """リトライ付きパッケージインストール"""
        for attempt in range(max_retries):
            try:
                success, message = install_package(package_name)
                
                if success:
                    # インストール成功通知
                    notification = {
                        "type": "install_success",
                        "package": package_name,
                        "message": f"✅ {package_name} をインストールしました！",
                        "timestamp": time.time()
                    }
                    self.install_notifications.append(notification)
                    return True, message
                else:
                    # インストール失敗通知
                    notification = {
                        "type": "install_failed",
                        "package": package_name,
                        "message": f"❌ {package_name} のインストールに失敗しました",
                        "error": message,
                        "timestamp": time.time()
                    }
                    self.install_notifications.append(notification)
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)  # リトライ前に待機
                    
            except Exception as e:
                error_msg = f"インストールエラー: {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return False, error_msg
        
        return False, f"最大リトライ回数に達しました: {package_name}"
    
    def safe_import_with_auto_install(self, package_name, import_name=None):
        """安全なインポートと自動インストール"""
        if import_name is None:
            import_name = package_name.replace('-', '_')
        
        try:
            module = importlib.import_module(import_name)
            self.installed_packages[package_name] = module
            return True, module
        except ImportError as e:
            st.warning(f"⚠️ {package_name} が見つかりません。自動インストールを開始します...")
            
            # 自動インストール
            success, message = self.install_package_with_retry(package_name)
            
            if success:
                # インストール後にインポートを再試行
                importlib.invalidate_caches()
                try:
                    module = importlib.import_module(import_name)
                    self.installed_packages[package_name] = module
                    st.success(f"✅ {package_name} のインストールとインポートに成功しました")
                    return True, module
                except ImportError as retry_error:
                    st.error(f"❌ {package_name} のインポートに再び失敗しました: {retry_error}")
                    return False, None
            else:
                st.error(f"❌ {package_name} のインストールに失敗しました: {message}")
                return False, None
    
    def initialize_all_packages(self):
        """すべての必要なパッケージを初期化"""
        st.info("🔧 必要なライブラリを確認・インストール中...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_packages = len(self.required_packages)
        success_count = 0
        
        for i, (package_name, import_name) in enumerate(self.required_packages.items()):
            status_text.text(f"📦 {package_name} を確認中... ({i+1}/{total_packages})")
            
            success, module = self.safe_import_with_auto_install(package_name, import_name)
            
            if success:
                success_count += 1
                progress_bar.progress((i + 1) / total_packages)
            else:
                st.error(f"❌ {package_name} の初期化に失敗しました")
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ 初期化完了: {success_count}/{total_packages} パッケージ")
        
        return success_count == total_packages
    
    def get_package_status(self):
        """パッケージの状態を取得"""
        status = {}
        for package_name, import_name in self.required_packages.items():
            if package_name in self.installed_packages:
                status[package_name] = "✅ インストール済み"
            else:
                status[package_name] = "❌ 未インストール"
        return status
    
    def display_notifications(self):
        """インストール通知を表示"""
        if self.install_notifications:
            with st.expander("🔧 ライブラリインストール通知", expanded=True):
                for notification in self.install_notifications[-5:]:  # 最新5件
                    if notification['type'] == 'install_success':
                        st.success(notification['message'])
                    else:
                        st.error(f"{notification['message']}\n詳細: {notification.get('error', 'Unknown error')}")
                    
                    st.caption(f"時刻: {time.strftime('%H:%M:%S', time.localtime(notification['timestamp']))}")

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
            if duration >= 2.0:  # 最小発話時間
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
        
        if self.last_speech_end:
            time_since_last_speech = time.time() - self.last_speech_end
            return time_since_last_speech >= 2.0  # 最大休止時間
        
        return False
    
    def get_combined_audio(self):
        """結合された音声データを取得"""
        if not self.speech_segments:
            return None
        
        combined_audio = []
        for segment in self.speech_segments:
            combined_audio.extend(segment["audio_data"])
        
        return combined_audio
    
    def reset(self):
        """バッファをリセット"""
        self.speech_segments = []
        self.audio_buffer = []
        self.last_speech_end = None
        self.current_segment_start = None
        self.total_duration = 0.0

class SmartVoiceInputHandler:
    """スマート音声入力ハンドラ"""
    
    def __init__(self, healing_agent):
        self.healing_agent = healing_agent
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.whisper_model = None
        self.vad_model = None
        self.voice_buffer = SmartVoiceBuffer()
        self.processing_thread = None
        
    def initialize(self):
        """音声入力システム初期化"""
        try:
            # Whisperモデル読み込み
            if 'faster-whisper' in self.healing_agent.installed_packages:
                from faster_whisper import WhisperModel
                
                # CUDAチェック
                torch = self.healing_agent.installed_packages.get('torch')
                use_cuda = torch and hasattr(torch, 'cuda') and torch.cuda.is_available()
                
                self.whisper_model = WhisperModel(
                    "large-v3",
                    device="cuda" if use_cuda else "cpu",
                    compute_type="float32"
                )
                st.success("✅ Whisperモデル読み込み完了")
            else:
                st.error("❌ faster-whisperが利用できません")
                return False
            
            # VADモデル読み込み
            if 'torch' in self.healing_agent.installed_packages:
                try:
                    torch = self.healing_agent.installed_packages['torch']
                    self.vad_model, utils = torch.hub.load(
                        'snakers4/silero-vad',
                        'silero_vad',
                        force_reload=True
                    )
                    self.vad_utils = utils
                    st.success("✅ VADモデル読み込み完了")
                except Exception as vad_error:
                    st.warning(f"⚠️ VADモデル読み込みエラー: {vad_error}")
                    self.vad_model = None
            else:
                st.warning("⚠️ torchが利用できないためVADを無効化します")
                self.vad_model = None
            
            return True
        except Exception as e:
            st.error(f"❌ 音声入力システム初期化エラー: {str(e)}")
            return False
    
    def start_recording(self):
        """録音開始"""
        if self.is_recording:
            return False
        
        if 'sounddevice' not in self.healing_agent.installed_packages:
            st.error("❌ sounddeviceが利用できません")
            return False
        
        self.is_recording = True
        self.voice_buffer.reset()
        
        # 録音スレッドを開始
        def audio_callback(indata, frame_count, time_info, status):
            if status:
                st.error(f"❌ 音声入力エラー: {status}")
            self.audio_queue.put(indata.copy())
        
        try:
            sd = self.healing_agent.installed_packages['sounddevice']
            
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
            sd = self.healing_agent.installed_packages['sounddevice']
            
            with sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype="int16",
                blocksize=1024,
                callback=callback
            ) as stream:
                while self.is_recording:
                    try:
                        audio_data = self.audio_queue.get(timeout=1.0)
                        
                        if audio_data is not None and len(audio_data) > 0:
                            # VADで音声活動検出
                            if self.vad_model is not None:
                                torch = self.healing_agent.installed_packages['torch']
                                np = self.healing_agent.installed_packages.get('numpy', __import__('numpy'))
                                
                                audio_tensor = torch.from_numpy(np.array(audio_data, dtype=np.float32))
                                speech_prob = self.vad_model(audio_tensor, 16000).item()
                            else:
                                # 簡易的な音声検出
                                np = self.healing_agent.installed_packages.get('numpy', __import__('numpy'))
                                audio_array = np.array(audio_data)
                                energy = np.sqrt(np.mean(audio_array**2))
                                speech_prob = 1.0 if energy > 0.01 else 0.0
                            
                            if speech_prob > 0.5:  # VAD閾値
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
            
            if combined_audio and self.whisper_model:
                # 音声データをWAVファイルに変換
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    with wave.open(tmp_file.name, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(16000)
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

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🤖 Self-Healing Smart Voice AI Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Self-Healing Smart Voice AI Agent")
    st.markdown("### 動的ライブラリインストール対応版 - 自己修復型AIエージェント")
    
    # 自己修復AIエージェントの初期化
    if 'healing_agent' not in st.session_state:
        st.session_state.healing_agent = SelfHealingAIAgent()
    
    healing_agent = st.session_state.healing_agent
    
    # サイドバーにパッケージ状態を表示
    with st.sidebar:
        st.header("🔧 ライブラリ状態")
        
        # パッケージ初期化ボタン
        if st.button("🔄 ライブラリ初期化", key="init_packages"):
            with st.spinner("🔧 ライブラリを初期化中..."):
                success = healing_agent.initialize_all_packages()
                if success:
                    st.success("✅ すべてのライブラリが正常に初期化されました")
                else:
                    st.warning("⚠️ 一部のライブラリで問題が発生しました")
        
        # パッケージ状態表示
        package_status = healing_agent.get_package_status()
        st.subheader("📦 パッケージ状態")
        for package, status in package_status.items():
            st.text(f"{package}: {status}")
        
        # インストール通知表示
        healing_agent.display_notifications()
    
    # ライブラリがインストールされているか確認
    if not healing_agent.installed_packages:
        st.warning("⚠️ 必要なライブラリがインストールされていません。サイドバーの「ライブラリ初期化」をクリックしてください。")
        st.stop()
    
    # AIエージェントの初期化
    if 'voice_agent' not in st.session_state:
        st.session_state.voice_agent = SmartVoiceInputHandler(healing_agent)
        
        with st.spinner("🤖 音声AIエージェントを初期化中..."):
            if st.session_state.voice_agent.initialize():
                st.success("✅ 音声AIエージェント初期化完了")
            else:
                st.error("❌ 音声AIエージェント初期化失敗")
                st.stop()
    
    # AI応答エージェント
    if 'ai_agent' not in st.session_state:
        st.session_state.ai_agent = AIAgent()
    
    voice_agent = st.session_state.voice_agent
    ai_agent = st.session_state.ai_agent
    
    # メインインターフェース
    st.header("🎤️ スマート音声入力システム")
    
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
            
            # 録音コントロール
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎤️ 録音開始", key="start_recording"):
                    if voice_agent.start_recording():
                        st.success("✅ 録音開始")
                        st.session_state.recording_status = "recording"
                    else:
                        st.error("❌ 録音開始失敗")
            
            with col2:
                if st.button("⏹️ 録音停止", key="stop_recording"):
                    if voice_agent.stop_recording():
                        st.success("✅ 録音停止")
                        st.session_state.recording_status = "stopped"
                    else:
                        st.error("❌ 録音停止失敗")
            
            # 録音状態表示
            if st.session_state.get("recording_status") == "recording":
                st.info("🔴 録音中...")
                
                # リアルタイムステータス
                status = {
                    "is_recording": voice_agent.is_recording,
                    "buffer_segments": len(voice_agent.voice_buffer.speech_segments),
                    "total_duration": voice_agent.voice_buffer.total_duration,
                    "last_speech_end": voice_agent.voice_buffer.last_speech_end
                }
                
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
                            if 'pyttsx3' in healing_agent.installed_packages:
                                pyttsx3 = healing_agent.installed_packages['pyttsx3']
                                engine = pyttsx3.init()
                                engine.say(st.session_state.ai_response)
                                engine.runAndWait()
                                st.success("✅ 音声読み上げ完了")
                            else:
                                st.error("❌ pyttsx3が利用できません")
                        except Exception as e:
                            st.error(f"音声読み上げエラー: {str(e)}")
        
        elif input_method == "⌨️ テキスト入力":
            st.subheader("⌨️ テキスト入力")
            
            # テキスト入力欄
            user_input = st.text_area(
                "💬 メッセージを入力してください",
                key="text_input",
                height=100,
                placeholder="ここにメッセージを入力..."
            )
            
            # 入力コントロール
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
    
    with col2:
        st.subheader("📊 システム情報")
        
        # パッケージ状態
        st.write("**インストール済みパッケージ**:")
        for package in healing_agent.installed_packages:
            st.write(f"✅ {package}")
        
        # システムコマンド
        st.write("**管理コマンド**:")
        st.code("docker logs ai-ollama --tail=20")
        st.code("docker exec -it ai-agent-app bash")
        st.code("curl -f http://localhost:11434/api/tags")

if __name__ == "__main__":
    main()
