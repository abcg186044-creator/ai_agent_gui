#!/usr/bin/env python3
"""
Voice Enhanced Autonomous AI Agent - 音声入力・感情分析・音声合成学習
"""

import streamlit as st
import sys
import os
import json
import tempfile
import time
import threading
import queue
import wave
import numpy as np
from datetime import datetime
import hashlib

# 基本インポート
try:
    import ollama
    import faster_whisper
    import pyttsx3
    import pyautogui
    import chromadb
    from sentence_transformers import SentenceTransformer
    import faiss
    import psutil
    import schedule
    import sounddevice as sd
    import soundfile as sf
    import speech_recognition as sr
except ImportError as e:
    st.error(f"❌ 必須ライブラリのインポートエラー: {str(e)}")
    st.stop()

# 設定
class Config:
    MAIN_MODEL = "llama3.2"
    VISION_MODEL = "llama3.2-vision"
    EMBEDD_MODEL = "all-MiniLM-L6-v2"
    
    # 音声設定
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_FORMAT = "int16"
    AUDIO_CHUNK_DURATION = 30  # 秒
    
    # Whisper設定
    WHISPER_MODEL = "large-v3"
    
    # 音声認識設定
    VAD_MODEL = "silero-vad"
    
    # 音声合成設定
    TTS_ENGINE = "sapi5"  # Windows標準
    TTS_RATE = 200
    TTS_VOLUME = 0.9
    
    # 音声特徴量
    VOICE_FEATURES = {
        "pitch": "ピッチ（音の高さ）",
        "energy": "エネルギー（声の大きさ）",
        "spectral_centroid": "音色（明るさ）",
        "zero_crossing_rate": "無音区間の交差",
        "speaking_rate": "話す速度"
    }
    
    # 感情分析設定
    EMOTION_KEYWORDS = {
        "positive": ["嬉しい", "楽しい", "ありがとう", "素晴らしい", "成功", "満足", "最高", "良い", "素敵"],
        "negative": ["悲しい", "つらい", "残念", "失敗", "困る", "大変", "最悪", "嫌い", "疲れた", "不安", "心配"],
        "neutral": ["普通", "通常", "まあ", "なるほど", "そう", "どう"]
    }

class VoiceInputHandler:
    """音声入力ハンドラ"""
    
    def __init__(self):
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        self.whisper_model = None
        self.vad_model = None
        
    def initialize(self):
        """音声入力システム初期化"""
        try:
            # Whisperモデル読み込み
            self.whisper_model = faster_whisper.WhisperModel(
                Config.WHISPER_MODEL,
                device="cuda" if torch.cuda.is_available() else "cpu",
                compute_type="float16"
            )
            
            # VADモデル読み込み
            try:
                import silero_vad
                self.vad_model = silero_vad.VAD(model_path=Config.VAD_MODEL)
            except ImportError:
                st.warning("⚠️ VADモデルが見つかりません。音声区別のみを使用します。")
                self.vad_model = None
            
            return True
        except Exception as e:
            st.error(f"❌ 音声入力システム初期化エラー: {str(e)}")
            return False
    
    def start_recording(self):
        """録音開始"""
        if self.is_recording:
            return False
        
        self.is_recording = True
        
        # 録音スレッドを開始
        def audio_callback(indata, frame_count, time_info):
            self.audio_queue.put(indata)
        
        try:
            self.recording_thread = threading.Thread(
                target=self._record_audio,
                args=(audio_callback,),
                daemon=True
            )
            self.recording_thread.start()
            return True
        except Exception as e:
            st.error(f"❌ 録音開始エラー: {str(e)}")
            return False
    
    def _record_audio(self, callback):
        """音声録音（バックグラウンド）"""
        try:
            with sd.InputStream(
                samplerate=Config.AUDIO_SAMPLE_RATE,
                channels=Config.AUDIO_CHANNELS,
                dtype=Config.AUDIO_FORMAT,
                blocksize=1024,
                callback=callback
            ) as stream:
                self.audio_queue.put(stream)
        except Exception as e:
            st.error(f"❌ 録音エラー: {str(e)}")
    
    def stop_recording(self):
        """録音停止"""
        if not self.is_recording:
            return False
        
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=5)
            self.recording_thread = None
    
    def get_audio_data(self):
        """録音データを取得"""
        audio_data = []
        try:
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())
        return audio_data
        except Exception as e:
            st.error(f"❌ 音声データ取得エラー: {str(e)}")
            return []
    
    def transcribe_audio(self, audio_data):
        """音声認識"""
        try:
            # 音声データをWAVファイルに変換
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wf:
                    wf.setnchannels(Config.AUDIO_CHANNELS)
                    wf.setsampwidth(Config.AUDIO_SAMPLE_RATE)
                    wf.setframerate(Config.AUDIO_SAMPLE_RATE)
                    wf.writeframes(audio_data)
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
                
                return result
        except Exception as e:
            return {"error": str(e)}
    
    def detect_voice_activity(self, audio_data):
        """音声活動検出"""
        if not self.vad_model:
            return {"activity": "unknown"}
        
        try:
            # 音声データをnumpy配列に変換
            audio_array = np.array(audio_data)
            
            # VADで音声活動検出
            speech_prob = self.vad_model(audio_array, sample_rate=Config.AUDIO_SAMPLE_RATE)
            
            if speech_prob > 0.5:
                return {"activity": "speaking"}
            else:
                return {"activity": "silent"}
        except Exception as e:
            return {"activity": "error", "message": str(e)}

class VoiceFeatureExtractor:
    """音声特徴量抽出"""
    
    def __init__(self):
        self.sample_rate = Config.AUDIO_SAMPLE_RATE
        
    def extract_features(self, audio_data):
        """音声特徴量を抽出"""
        try:
            audio_array = np.array(audio_data)
            
            # 基本統計
            duration = len(audio_array) / self.sample_rate
            
            # ピッチ（音の高さ）
            pitches, magnitudes = librosa.pyin(audio_array, sr=self.sample_rate)
            avg_pitch = np.mean(pitches)
            
            # エネルギー（声の大きさ）
            energy = np.sqrt(np.mean(audio_array**2))
            
            # スペクトル（明るさ）
            spec = np.abs(np.fft(audio_array))
            spectral_centroid = np.mean(spec[:len(spec)//2])
            
            # ゼロスレート（話す速度）
            zero_crossings = np.sum(audio_array[:-1] != 0) & (audio_array[1:] != 0)
            
            return {
                "duration": duration,
                "avg_pitch": avg_pitch,
                "energy": energy,
                "spectral_centroid": spectral_centroid,
                "zero_crossing_rate": zero_crossings,
                "speaking_rate": len(audio_array) / self.sample_rate if audio_array else 0
            }
        except Exception as e:
            return {"error": str(e)}

class EmotionAnalyzer:
    """感情分析システム"""
    
    def __init__(self):
        self.emotion_keywords = Config.EMOTION_KEYWORDS
        
    def analyze_emotion(self, text, voice_features=None):
        """感情分析"""
        try:
            # テキスト感情分析
            text_lower = text.lower()
            text_sentiment = "neutral"
            text_score = 0.0
            
            positive_count = sum(1 for word in self.emotion_keywords["positive"] if word in text_lower)
            negative_count = sum(1 for word in self.emotion_keywords["negative"] if word in text_lower)
            
            if positive_count > negative_count:
                text_sentiment = "positive"
                text_score = min(1.0, positive_count / (positive_count + negative_count))
            elif negative_count > positive_count:
                text_sentiment = "negative"
                text_score = -min(1.0, negative_count / (positive_count + negative_count))
            
            # 音声特徴量からの感情分析
            voice_sentiment = "neutral"
            voice_score = 0.0
            
            if voice_features and "error" not in voice_features:
                # 音声の高さや速さから感情を推定
                if voice_features["avg_pitch"] > 200:  # 高い声
                    voice_sentiment = "excited"
                    voice_score = 0.8
                elif voice_features["energy"] > 0.7:  # 大きな声
                    voice_sentiment = "angry"
                    voice_score = -0.6
                elif voice_features["speaking_rate"] > 4: 0:  # 速い話
                    voice_sentiment = "nervous"
                    voice_score = 0.6
                elif voice_features["avg_pitch"] < 100: 0:  # 低い声
                    voice_sentiment = "sad"
                    voice_score = -0.6
            
            # 総合感情判定
            if text_score > 0.5:
                final_sentiment = "positive"
                final_score = text_score * 0.7 + voice_score * 0.3
            elif text_score < -0.5:
                final_sentiment = "negative"
                final_score = text_score * 0.7 + voice_score * 0.3
            else:
                final_sentiment = "neutral"
                final_score = text_score * 0.7 + voice_score * 0.3
            
            return {
                "text_sentiment": text_sentiment,
                "text_score": text_score,
                "voice_sentiment": voice_sentiment,
                "voice_score": voice_score,
                "final_sentiment": final_sentiment,
                "confidence": max(abs(text_score), abs(voice_score))
            }
            
        except Exception as:
            return {"error": str(e)}

class VoiceSynthesisLearner:
    """音声合成学習システム"""
    
    def __init__(self):
        self.tts_engine = None
        self.voice_profiles = {}
        self.learning_data = {}
        
    def initialize(self):
        """音声合成システム初期化"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', str(Config.TTS_RATE))
            self.tts_engine.setProperty('volume', str(Config.TTS_VOLUME))
            
            # 既存データ読み込み
            self._load_learning_data()
            
            return True
        except Exception as e:
            return False
    
    def _load_learning_data(self):
        """学習データ読み込み"""
        try:
            learning_file = "voice_learning.json"
            if os.path.exists(learning_file):
                with open(learning_file, 'r', encoding='utf-8') as f:
                    self.learning_data = json.load(f)
        except Exception:
            self.learning_data = {}
    
    def _save_learning_data(self):
        """学習データ保存"""
        try:
            learning_file = "voice_learning.json"
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"❌ 学習データ保存エラー: {str(e)}")
    
    def learn_voice_profile(self, text, voice_features):
        """ユーザーの音声プロファイルを学習"""
        try:
            profile_id = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()
            
            if profile_id not in self.voice_profiles:
                self.voice_profiles[profile_id] = {
                    "text": text,
                    "voice_features": voice_features,
                    "created_at": datetime.now().isoformat(),
                    "usage_count": 0
                }
                self.learning_data["profiles"][profile_id] = self.voice_profiles[profile_id]
                self._save_learning_data()
            
        except Exception as e:
            st.error(f"❌ 音声プロファイル学習エラー: {str(e)}")
    
    def synthesize_speech(self, text, profile_id=None):
        """学習した音声で合成"""
        try:
            if profile_id and profile_id in self.voice_profiles:
                profile = self.voice_profiles[profile_id]
                # 学習した特徴を反映
                if profile["voice_features"]:
                    if profile["voice_features"]["avg_pitch"] > 0:
                        self.tts_engine.setProperty('rate', str(int(profile["voice_features"]["avg_pitch"]))
                
                self.learning_data["profiles"][profile_id]["usage_count"] += 1
                self._save_learning_data()
                
                return True
        else:
            return False
        except Exception as e:
            st.error(f"❌ 音声合成エラー: {str(e)}")
            return False

class VoiceEnhancedAIAgent:
    """音声強化自律AIエージェント"""
    
    def __init__(self):
        self.ollama_client = None
        self.voice_input = VoiceInputHandler()
        self.knowledge_base = None
        self.emotion_analyzer = EmotionAnalyzer()
        self.voice_feature_extractor = VoiceFeatureExtractor()
        self.voice_synthesis_learner = VoiceSynthesisLearner()
        self.current_conversation = []
        
    def initialize(self):
        """AIエージェント初期化"""
        try:
            # Ollama初期化
            self.ollama_client = ollama.Client()
            
            # 各サブシステム初期化
            self.voice_input.initialize()
            self.emotion_analyzer.initialize()
            self.voice_feature_extractor.initialize()
            self.voice_synthesis_learner.initialize()
            
            return True
        except Exception as e:
            return False
    
    def process_voice_input(self, user_input):
        """音声入力処理"""
        try:
            # 録音開始
            if not self.voice_input.start_recording():
                st.error("❌ 録音開始に失敗しました")
                return "音声入力の開始に失敗しました。"
            
            st.info("🎤️ 録音中...話してください")
            
            # 録音停止
            time.sleep(3)  # 3秒間録音
            
            audio_data = self.voice_input.get_audio_data()
            self.voice_input.stop_recording()
            
            if not audio_data:
                return "音声が認識できませんでした。もう一度お試しください。"
            
            # 音声認識
            transcription = self.voice_input.transcribe_audio(audio_data)
            
            if "error" in transcription:
                return f"音声認識エラー: {transcription['error']}"
            
            # 音声特徴量抽出
            voice_features = self.voice_feature_extractor.extract_features(audio_data)
            
            # 感情分析
            emotion_result = self.emotion_analyzer.analyze_emotion(transcription["text"], voice_features)
            
            # ユーザー入力を保存
            self.current_conversation.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "transcription": transcription,
                "voice_features": voice_features,
                "emotion_analysis": emotion_result
            })
            
            # 音声プロファイル学習
            self.voice_synthesis_learner.learn_voice_profile(transcription["text"], voice_features)
            
            return {
                "transcription": transcription,
                "voice_features": voice_features,
                "emotion_analysis": emotion_result
            }
            
        except Exception as e:
            return f"❌ 音声入力処理エラー: {str(e)}"

def render_voice_interface(ai_agent):
    """音声インターフェース"""
    st.header("🎤️ 音声入力・音声分析")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎤️ 音声入力")
        
        # 録音コントロール
        if st.button("🎤️ 録音開始", key="start_recording"):
            result = ai_agent.process_voice_input("音声入力テスト")
            
            if "error" in result:
                st.error(result)
            elif "transcription" in result:
                st.success(f"✅ 音声認識完了: {result['transcription']['text'][:100]}...")
            else:
                st.success(result)
        
        # 音声入力中の表示
        if ai_agent.voice_input.is_recording:
            st.info("🔴 録音中... 話り込んでください")
            
        # 音声特徴量表示
        if st.session_state.get("last_voice_features"):
            features = st.session_state["last_voice_features"]
            st.subheader("📊 音声特徴量")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("平均ピッチ", f"{features['avg_pitch']:.1f} Hz")
                st.metric("エネルギー", f"{features['energy']:.2f}")
                st.metric("スペクトル重心", f"{features['spectral_centroid']:.1f}")
                st.metric("ゼロ交差", f"{features['zero_crossing_rate']}")
            
            with col2:
                st.metric("話す速度", f"{features['speaking_rate']:.1f} 字/秒")
                st.metric("録音時間", f"{features['duration']:.1f} 秒")
        
        # 感情分析結果
        if st.session_state.get("last_emotion_analysis"):
            emotion = st.session_state["last_emotion_analysis"]
            st.subheader("😊 感情分析")
            
            col1, col2 = st2, col3 = st.columns(3)
            
            with col1:
                st.metric("テキスト感情", emotion["text_sentiment"])
                st.metric("テキストスコア", f"{emotion['text_score']:.2f}")
            
            with col2:
                st.metric("音声感情", emotion["voice_sentiment"])
                st.metric("音声スコア", f"{emotion['voice_score']:.2f}")
            
            with col3:
                st.metric("最終感情", emotion["final_sentiment"])
                st.metric("信頼度", f"{emotion['confidence']:.2f}")
    
    with col2:
        st.subheader("🎙️ 音声合成学習")
        
        # 学習済みプロファイル
        profiles = ai_agent.voice_synthesis_learner.voice_profiles
        if profiles:
            st.write("**学習済みプロファイル**:")
            for profile_id, profile_data in list(profiles.values())[:5]:
                st.write(f"- {profile_id}: 使用回数: {profile_data['usage_count']}")
        
        # プロファイル選択
        selected_profile = st.selectbox(
            "音声プロファイル選択",
            options=["なし"] + list(profiles.keys()),
            key="voice_profile_select"
        )
        
        # テスト入力
        test_text = st.text_area("テストテキスト", key="test_text")
        
        if st.button("🔊 音声合成テスト", key="test_synthesis"):
            if selected_profile != "なし":
                success = ai_agent.voice_synthesis_learner.synthesize_speech(test_text, selected_profile)
                if success:
                    st.success("✅ 音声合成完了")
                else:
                    st.error("❌ 音声合成失敗")
            else:
                st.warning("⚠️ 音声プロファイルを選択してください")
    
    with col2:
        st.subheader("📊 対話履歴")
        
        if ai_agent.current_conversation:
            st.write("**最近の対話**:")
            for conv in ai_agent.current_conversation[-5:]:
                timestamp = datetime.fromisoformat(conv["timestamp"])
                time_str = timestamp.strftime('%H:%M:%S')
                
                st.write(f"**{time_str}**: {conv['transcription']['text'][:50]}...")
                
                # 感情分析
                if "emotion_analysis" in conv:
                    emotion = conv["emotion_analysis"]
                    st.write(f"感情: {emotion['final_sentiment']} (信頼度: {emotion['confidence']:.2f})")
    
    # 音声入力中のステータス表示
    if ai_agent.voice_input.is_recording:
        st.warning("🔴 録音中...")

def render_main_interface(ai_agent):
    """メインインターフェース"""
    st.header("💬 音声強化AIアシスタント")
    
    # 会話履歴
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    # 入力エリア
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_input(
            "💬 メッセージを入力",
            placeholder="音声またはテキストで入力...",
            key="user_input"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            send_button = st.button("💬 送信", type="primary")
        
        with col2:
            voice_mode = st.checkbox("🎤️ 音声入力モード", value=False)
            auto_speech = st.checkbox("🔊 音声読み上げ", value=True)
        
        with col3:
            show_analysis = st.checkbox("🔍 分析表示", value=False)
        
        # 送信処理
        if send_button and user_input:
            if voice_mode:
                # 音声入力モード
                result = ai_agent.process_voice_input(user_input)
                st.session_state.messages.append({"role": "user", "content": f"🎤️ 音声入力: {result['transcription']['text']}"})
            else:
                # テキスト入力モード
                # llama3.2で応答生成
                with st.spinner("🤖 AI応答生成中..."):
                    response = ai_agent.ollama_client.generate(
                        model=Config.MAIN_MODEL,
                        prompt=f"ユーザーの入力: {user_input}",
                        options={"temperature": 0.7, "max_tokens": 4096}
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response['response']})
            
            # 自動音声読み上げ
            if auto_speech:
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(response['response'])
                    engine.runAndWait()
                except Exception as e:
                    st.error(f"音声読み上げエラー: {str(e)}")
            
            st.rerun()
    
    with col2:
        # VRM表示（オプション）
        st.subheader("👤 アバター状態")
        
        # 現在の感情状態を表示
        if st.session_state.get("last_emotion_analysis"):
            emotion = st.session_state["last_emotion_analysis"]
            st.write(f"**現在の感情**: {emotion['final_sentiment']}")
            
            # 感情に応じた調整
            if emotion["final_sentiment"] == "positive":
                st.success("😊 ポジティブな応答です！")
            elif emotion["final_sentiment"] == "negative":
                st.warning("😔 共感的に対応します")
            elif emotion["final_sentiment"] == "neutral":
                st.info("😐 通常の応答です")
        
        # アバター表示
        avatar_display = f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 10px 0;">
            <div style="color: white; font-weight: bold;">
                <div style="font-size: 64px; margin-bottom: 10px;">😐</div>
                <div>AIアバター</div>
                <div>状態: 準備中</div>
                <div>時刻: {datetime.now().strftime('%H:%M:%S')}</div>
            </div>
        </div>
        """
        st.markdown(avatar_display, unsafe_allow_html=True)

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🎤️ Voice Enhanced AI Agent",
        page_icon="🎤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤️ AI Agent System - 音声強化版")
    st.markdown("### 🎯 音声入力・感情分析・音声合成学習")
    
    # システム初期化
    if 'ai_agent' not in st.session_state:
        with st.spinner("🎤️ 音声強化AIシステム初期化中..."):
            ai_agent = VoiceEnhancedAIAgent()
            if ai_agent.initialize():
                st.session_state.ai_agent = ai_agent
                st.success("✅ 音声強化AIシステム初期化完了")
            else:
                st.error("❌ AIシステム初期化失敗")
                st.stop()
    
    ai_agent = st.session_state.ai_agent
    
    # サイドバー
    with st.sidebar:
        st.subheader("⚙️ 音声設定")
        
        # 音声認識設定
        st.write("**Whisperモデル**: large-v3")
        st.write("**サンプルレート**: 16000Hz")
        st.write("**チャンネル**: 1")
        
        # 音声合成設定
        st.write("**エンジン**: SAPI5")
        st.write(f"レート: {Config.TTS_RATE}")
        st.write(f"音量: {Config.TTS_VOLUME}")
        
        # 学習状況
        profiles = ai_agent.voice_synthesis_learner.voice_profiles
        st.write(f"**学習済みプロファイル**: {len(profiles)}")
        
        # 最新の学習データ
        if ai_agent.voice_synthesis_learner.learning_data:
            st.write("**学習データ**:")
            st.json(ai_agent.voice_synthesis_learner.learning_data, indent=2)
    
    # メインタブ
    tab1, tab2 = st.tabs(["💬 音声強化AI対話", "🎤️ 音声入力・分析"])
    
    with tab1:
        render_main_interface(ai_agent)
    
    with tab2:
        render_voice_interface(ai_agent)
    
    # フッター情報
    st.markdown("---")
    st.markdown(f"**🎤️ 音声強化AI**: {Config.MAIN_MODEL}")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🎯 目標**: 音声で自然な対話・感情理解・音声合成学習")

if __name__ == "__main__":
    main()
