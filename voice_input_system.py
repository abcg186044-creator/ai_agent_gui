#!/usr/bin/env python3
"""
高度音声入力システム
リアルタイム音声認識・感情分析・イントネーション学習
"""

import streamlit as st
import numpy as np
import librosa
import soundfile as sf
import pyaudio
import wave
import threading
import time
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import webrtcvad
from faster_whisper import WhisperModel
import pyworld as pw
from scipy import signal
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class VoiceEmotionAnalyzer:
    """音声感情分析器"""
    
    def __init__(self):
        self.name = "voice_emotion_analyzer"
        self.description = "音声から感情・イントネーションを分析"
        
        # 感情分類モデル（簡易版）
        self.emotion_labels = ["neutral", "happy", "sad", "angry", "tired", "excited"]
        
        # 特徴量の正規化
        self.scaler = StandardScaler()
        
        # 分析履歴
        self.analysis_history = []
    
    def extract_voice_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """音声特徴量を抽出"""
        try:
            features = {}
            
            # 1. ピッチ（基本周波数）分析
            f0, time_axis = pw.harvest(audio_data, sample_rate)
            f0_clean = f0[f0 > 0]  # 有声音のみ
            
            if len(f0_clean) > 0:
                features['pitch_mean'] = np.mean(f0_clean)
                features['pitch_std'] = np.std(f0_clean)
                features['pitch_range'] = np.max(f0_clean) - np.min(f0_clean)
                features['pitch_slope'] = self._calculate_pitch_slope(f0_clean)
            else:
                # 無声の場合
                features['pitch_mean'] = 0
                features['pitch_std'] = 0
                features['pitch_range'] = 0
                features['pitch_slope'] = 0
            
            # 2. テンポ・リズム分析
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features['tempo'] = tempo
            features['beat_regularity'] = self._calculate_beat_regularity(beats)
            
            # 3. 音色・スペクトル特徴
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
            
            # スペクトルセントロイド
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            # 4. エネルギー・音量
            rms = librosa.feature.rms(y=audio_data)
            features['energy_mean'] = np.mean(rms)
            features['energy_std'] = np.std(rms)
            features['energy_range'] = np.max(rms) - np.min(rms)
            
            # 5. 話し速度
            duration = len(audio_data) / sample_rate
            features['duration'] = duration
            features['speech_rate'] = self._estimate_speech_rate(audio_data, sample_rate)
            
            # 6. 声質特徴
            features['voice_quality'] = self._analyze_voice_quality(audio_data, sample_rate)
            
            return features
            
        except Exception as e:
            print(f"音声特徴抽出エラー: {str(e)}")
            return self._get_default_features()
    
    def _calculate_pitch_slope(self, f0: np.ndarray) -> float:
        """ピッチの傾きを計算"""
        if len(f0) < 2:
            return 0.0
        
        x = np.arange(len(f0))
        slope, _ = np.polyfit(x, f0, 1)
        return slope
    
    def _calculate_beat_regularity(self, beats: np.ndarray) -> float:
        """ビートの規則性を計算"""
        if len(beats) < 2:
            return 0.0
        
        intervals = np.diff(beats)
        return 1.0 / (np.std(intervals) + 1e-8)
    
    def _estimate_speech_rate(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """話し速度を推定（音節/秒）"""
        # 簡易的な音節検出
        energy = librosa.feature.rms(y=audio_data)[0]
        threshold = np.mean(energy) + np.std(energy)
        
        # エネルギーが閾値を超える点を検出
        peaks = signal.find_peaks(energy, height=threshold)[0]
        
        if len(peaks) < 2:
            return 0.0
        
        duration = len(audio_data) / sample_rate
        return len(peaks) / duration
    
    def _analyze_voice_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """声質を分析"""
        try:
            # ハーモニクス・ノイズ比
            f0, time_axis = pw.harvest(audio_data, sample_rate)
            sp = pw.cheaptrick(audio_data, f0, time_axis, sample_rate)
            ap = pw.d4c(audio_data, f0, time_axis, sample_rate)
            
            # HNRの平均値
            hnr_values = []
            for i in range(len(f0)):
                if f0[i] > 0:
                    harmonic_energy = np.sum(sp[i]**2)
                    total_energy = np.sum(sp[i]**2 + ap[i]**2)
                    hnr = harmonic_energy / (total_energy + 1e-8)
                    hnr_values.append(hnr)
            
            if hnr_values:
                hnr_mean = np.mean(hnr_values)
                hnr_std = np.std(hnr_values)
            else:
                hnr_mean = 0.0
                hnr_std = 0.0
            
            return {
                'hnr_mean': hnr_mean,
                'hnr_std': hnr_std,
                'breathiness': self._calculate_breathiness(audio_data, sample_rate)
            }
            
        except Exception as e:
            print(f"声質分析エラー: {str(e)}")
            return {'hnr_mean': 0.0, 'hnr_std': 0.0, 'breathiness': 0.0}
    
    def _calculate_breathiness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """息の成分を計算"""
        # 高周波成分の割合
        high_freq = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate, fmax=8000)
        low_freq = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate, fmin=0, fmax=4000)
        
        high_energy = np.mean(high_freq)
        low_energy = np.mean(low_freq)
        
        return high_energy / (low_energy + 1e-8)
    
    def _get_default_features(self) -> Dict:
        """デフォルト特徴量"""
        return {
            'pitch_mean': 0.0, 'pitch_std': 0.0, 'pitch_range': 0.0, 'pitch_slope': 0.0,
            'tempo': 120.0, 'beat_regularity': 0.0,
            'mfcc_mean': [0.0]*13, 'mfcc_std': [0.0]*13,
            'spectral_centroid_mean': 0.0, 'spectral_centroid_std': 0.0,
            'energy_mean': 0.0, 'energy_std': 0.0, 'energy_range': 0.0,
            'duration': 0.0, 'speech_rate': 0.0,
            'voice_quality': {'hnr_mean': 0.0, 'hnr_std': 0.0, 'breathiness': 0.0}
        }
    
    def classify_emotion(self, features: Dict) -> Dict:
        """感情を分類（簡易ルールベース）"""
        try:
            emotion_scores = {}
            
            # ピッチに基づく感情判定
            pitch = features['pitch_mean']
            pitch_std = features['pitch_std']
            
            if pitch > 200 and pitch_std > 20:
                emotion_scores['excited'] = 0.8
                emotion_scores['happy'] = 0.6
            elif pitch > 150:
                emotion_scores['happy'] = 0.7
                emotion_scores['excited'] = 0.4
            elif pitch < 100 and pitch_std < 10:
                emotion_scores['tired'] = 0.8
                emotion_scores['sad'] = 0.5
            elif pitch < 120:
                emotion_scores['sad'] = 0.6
                emotion_scores['tired'] = 0.4
            else:
                emotion_scores['neutral'] = 0.7
            
            # テンポに基づく感情判定
            tempo = features['tempo']
            speech_rate = features['speech_rate']
            
            if tempo > 140 or speech_rate > 4:
                emotion_scores['excited'] = emotion_scores.get('excited', 0) + 0.3
                emotion_scores['angry'] = emotion_scores.get('angry', 0) + 0.2
            elif tempo < 80 or speech_rate < 2:
                emotion_scores['tired'] = emotion_scores.get('tired', 0) + 0.3
                emotion_scores['sad'] = emotion_scores.get('sad', 0) + 0.2
            
            # エネルギーに基づく感情判定
            energy = features['energy_mean']
            if energy > 0.1:
                emotion_scores['excited'] = emotion_scores.get('excited', 0) + 0.2
                emotion_scores['angry'] = emotion_scores.get('angry', 0) + 0.2
            elif energy < 0.02:
                emotion_scores['tired'] = emotion_scores.get('tired', 0) + 0.2
                emotion_scores['sad'] = emotion_scores.get('sad', 0) + 0.1
            
            # 声質に基づく感情判定
            breathiness = features['voice_quality']['breathiness']
            if breathiness > 0.3:
                emotion_scores['tired'] = emotion_scores.get('tired', 0) + 0.2
            
            # スコアを正規化
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                emotion_scores = {k: v/total_score for k, v in emotion_scores.items()}
            else:
                emotion_scores['neutral'] = 1.0
            
            # 最も高い感情を取得
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            
            return {
                'dominant_emotion': dominant_emotion,
                'emotion_scores': emotion_scores,
                'confidence': emotion_scores[dominant_emotion]
            }
            
        except Exception as e:
            print(f"感情分類エラー: {str(e)}")
            return {
                'dominant_emotion': 'neutral',
                'emotion_scores': {'neutral': 1.0},
                'confidence': 0.5
            }
    
    def analyze_voice(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """音声を完全に分析"""
        # 特徴量抽出
        features = self.extract_voice_features(audio_data, sample_rate)
        
        # 感情分類
        emotion_result = self.classify_emotion(features)
        
        # 結果を統合
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'emotion': emotion_result,
            'intonation_profile': self._create_intonation_profile(features)
        }
        
        # 履歴に保存
        self.analysis_history.append(analysis_result)
        
        return analysis_result
    
    def _create_intonation_profile(self, features: Dict) -> Dict:
        """イントネーションプロファイルを作成"""
        return {
            'pitch_characteristics': {
                'mean': features['pitch_mean'],
                'variability': features['pitch_std'],
                'range': features['pitch_range'],
                'trend': features['pitch_slope']
            },
            'rhythm_characteristics': {
                'tempo': features['tempo'],
                'speech_rate': features['speech_rate'],
                'regularity': features['beat_regularity']
            },
            'voice_characteristics': {
                'energy': features['energy_mean'],
                'brightness': features['spectral_centroid_mean'],
                'breathiness': features['voice_quality']['breathiness']
            }
        }

class IntonationMirroringSystem:
    """イントネーションミラーリング学習システム"""
    
    def __init__(self):
        self.name = "intonation_mirroring"
        self.description = "ユーザーのイントネーションを学習・模倣"
        
        # 学習データファイル
        self.adaptation_log_file = "voice_adaptation_log.json"
        
        # ユーザープロファイル
        self.user_voice_profile = {
            'pitch_mean': 150.0,
            'pitch_std': 20.0,
            'speech_rate': 3.0,
            'tempo': 120.0,
            'energy_mean': 0.05,
            'intonation_patterns': [],
            'emotion_responses': {}
        }
        
        # AI音声パラメータ
        self.ai_voice_params = {
            'pitch_scale': 1.0,
            'speed_scale': 1.0,
            'volume_scale': 1.0,
            'intonation_emphasis': 1.0
        }
        
        # 学習履歴
        self.learning_history = []
        
        self.load_adaptation_data()
    
    def load_adaptation_data(self):
        """適応データを読み込み"""
        try:
            if Path(self.adaptation_log_file).exists():
                with open(self.adaptation_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_voice_profile = data.get('user_profile', self.user_voice_profile)
                    self.ai_voice_params = data.get('ai_params', self.ai_voice_params)
                    self.learning_history = data.get('history', [])
        except Exception as e:
            print(f"適応データ読み込みエラー: {str(e)}")
    
    def save_adaptation_data(self):
        """適応データを保存"""
        try:
            data = {
                'user_profile': self.user_voice_profile,
                'ai_params': self.ai_voice_params,
                'history': self.learning_history[-100:],  # 最新100件
                'last_updated': datetime.now().isoformat()
            }
            with open(self.adaptation_log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"適応データ保存エラー: {str(e)}")
    
    def learn_from_user_voice(self, voice_analysis: Dict):
        """ユーザーの声から学習"""
        try:
            features = voice_analysis['features']
            emotion = voice_analysis['emotion']['dominant_emotion']
            
            # ユーザープロファイルを更新
            self._update_user_profile(features)
            
            # 感情とイントネーションの関連を学習
            self._learn_emotion_intonation_mapping(emotion, features)
            
            # AI音声パラメータを調整
            self._adapt_ai_voice_parameters(features)
            
            # 学習履歴に記録
            learning_record = {
                'timestamp': datetime.now().isoformat(),
                'user_features': features,
                'user_emotion': emotion,
                'ai_params_before': self.ai_voice_params.copy(),
                'adaptation_type': 'user_voice_learning'
            }
            
            self.learning_history.append(learning_record)
            self.save_adaptation_data()
            
            return True
            
        except Exception as e:
            print(f"音声学習エラー: {str(e)}")
            return False
    
    def _update_user_profile(self, features: Dict):
        """ユーザープロファイルを更新"""
        # 指数移動平均で滑らかに更新
        alpha = 0.1  # 学習率
        
        self.user_voice_profile['pitch_mean'] = (
            alpha * features['pitch_mean'] + 
            (1 - alpha) * self.user_voice_profile['pitch_mean']
        )
        
        self.user_voice_profile['pitch_std'] = (
            alpha * features['pitch_std'] + 
            (1 - alpha) * self.user_voice_profile['pitch_std']
        )
        
        self.user_voice_profile['speech_rate'] = (
            alpha * features['speech_rate'] + 
            (1 - alpha) * self.user_voice_profile['speech_rate']
        )
        
        self.user_voice_profile['tempo'] = (
            alpha * features['tempo'] + 
            (1 - alpha) * self.user_voice_profile['tempo']
        )
        
        self.user_voice_profile['energy_mean'] = (
            alpha * features['energy_mean'] + 
            (1 - alpha) * self.user_voice_profile['energy_mean']
        )
    
    def _learn_emotion_intonation_mapping(self, emotion: str, features: Dict):
        """感情とイントネーションの関連を学習"""
        if emotion not in self.user_voice_profile['emotion_responses']:
            self.user_voice_profile['emotion_responses'][emotion] = {
                'pitch_mean': features['pitch_mean'],
                'pitch_std': features['pitch_std'],
                'speech_rate': features['speech_rate'],
                'energy_mean': features['energy_mean'],
                'sample_count': 1
            }
        else:
            # 既存のデータを更新
            existing = self.user_voice_profile['emotion_responses'][emotion]
            alpha = 0.2
            
            existing['pitch_mean'] = (
                alpha * features['pitch_mean'] + 
                (1 - alpha) * existing['pitch_mean']
            )
            
            existing['pitch_std'] = (
                alpha * features['pitch_std'] + 
                (1 - alpha) * existing['pitch_std']
            )
            
            existing['speech_rate'] = (
                alpha * features['speech_rate'] + 
                (1 - alpha) * existing['speech_rate']
            )
            
            existing['energy_mean'] = (
                alpha * features['energy_mean'] + 
                (1 - alpha) * existing['energy_mean']
            )
            
            existing['sample_count'] += 1
    
    def _adapt_ai_voice_parameters(self, features: Dict):
        """AI音声パラメータを適応"""
        # ピッチの適応
        user_pitch = features['pitch_mean']
        baseline_pitch = 150.0  # 基準ピッチ
        
        pitch_ratio = user_pitch / baseline_pitch
        self.ai_voice_params['pitch_scale'] = np.clip(pitch_ratio, 0.5, 2.0)
        
        # 話し速度の適応
        user_speed = features['speech_rate']
        baseline_speed = 3.0  # 基準速度
        
        speed_ratio = user_speed / baseline_speed
        self.ai_voice_params['speed_scale'] = np.clip(speed_ratio, 0.5, 2.0)
        
        # エネルギー（音量）の適応
        user_energy = features['energy_mean']
        baseline_energy = 0.05  # 基準エネルギー
        
        energy_ratio = user_energy / baseline_energy
        self.ai_voice_params['volume_scale'] = np.clip(energy_ratio, 0.5, 2.0)
        
        # イントネーションの強調
        pitch_variability = features['pitch_std']
        baseline_variability = 20.0
        
        variability_ratio = pitch_variability / baseline_variability
        self.ai_voice_params['intonation_emphasis'] = np.clip(variability_ratio, 0.5, 2.0)
    
    def get_adapted_voice_params(self, target_emotion: str = None) -> Dict:
        """適応された音声パラメータを取得"""
        params = self.ai_voice_params.copy()
        
        if target_emotion and target_emotion in self.user_voice_profile['emotion_responses']:
            emotion_profile = self.user_voice_profile['emotion_responses'][target_emotion]
            
            # 感情特有の調整を適用
            emotion_pitch_ratio = emotion_profile['pitch_mean'] / 150.0
            params['pitch_scale'] *= emotion_pitch_ratio
            
            emotion_speed_ratio = emotion_profile['speech_rate'] / 3.0
            params['speed_scale'] *= emotion_speed_ratio
            
            emotion_energy_ratio = emotion_profile['energy_mean'] / 0.05
            params['volume_scale'] *= emotion_energy_ratio
        
        return params
    
    def get_learning_summary(self) -> Dict:
        """学習サマリーを取得"""
        return {
            'total_interactions': len(self.learning_history),
            'user_voice_profile': self.user_voice_profile,
            'current_ai_params': self.ai_voice_params,
            'learned_emotions': list(self.user_voice_profile['emotion_responses'].keys()),
            'adaptation_level': self._calculate_adaptation_level()
        }
    
    def _calculate_adaptation_level(self) -> float:
        """適応レベルを計算"""
        if len(self.learning_history) == 0:
            return 0.0
        
        # 学習回数に基づく適応レベル
        interaction_count = len(self.learning_history)
        
        # 対数スケールで飽和させる
        adaptation_level = min(1.0, np.log10(interaction_count + 1) / np.log10(100))
        
        return adaptation_level

class RealTimeVoiceInput:
    """リアルタイム音声入力システム"""
    
    def __init__(self):
        self.name = "realtime_voice_input"
        self.description = "リアルタイム音声認識と感情分析"
        
        # Whisperモデル
        self.whisper_model = None
        self.model_loaded = False
        
        # 音声感情分析器
        self.emotion_analyzer = VoiceEmotionAnalyzer()
        
        # イントネーションミラーリング
        self.mirroring_system = IntonationMirroringSystem()
        
        # 録音設定
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.record_seconds = 10
        
        # VAD（Voice Activity Detection）
        self.vad = webrtcvad.Vad(2)  # 中程度の感度
        
        # ウェイクワード
        self.wake_word = "ねえ相棒"
        self.wake_word_detected = False
        
        # 録音状態
        self.is_recording = False
        self.is_listening = False
        self.audio_buffer = []
        
        # 認識結果
        self.last_recognition_result = None
        self.last_emotion_analysis = None
        
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Whisperモデルを読み込み"""
        try:
            # 軽量モデルを使用
            self.whisper_model = WhisperModel("base", compute_type="int8")
            self.model_loaded = True
            print("✅ Whisperモデル読み込み完了")
        except Exception as e:
            print(f"❌ Whisperモデル読み込みエラー: {str(e)}")
            self.model_loaded = False
    
    def start_listening(self):
        """常時聴取を開始"""
        if not self.is_listening:
            self.is_listening = True
            listening_thread = threading.Thread(target=self._listening_loop, daemon=True)
            listening_thread.start()
            return True
        return False
    
    def stop_listening(self):
        """常時聴取を停止"""
        self.is_listening = False
        return True
    
    def _listening_loop(self):
        """常時聴取ループ"""
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("🎤 常時聴取開始...")
            
            while self.is_listening:
                try:
                    # 音声データを読み込み
                    data = stream.read(self.chunk)
                    audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # VADで音声検出
                    is_speech = self._detect_voice_activity(audio_chunk)
                    
                    if is_speech:
                        self.audio_buffer.append(audio_chunk)
                        
                        # ウェイクワード検出
                        if not self.wake_word_detected:
                            self._check_wake_word()
                    else:
                        # 無音区間でバッファを処理
                        if len(self.audio_buffer) > 0:
                            self._process_audio_buffer()
                            self.audio_buffer = []
                
                except Exception as e:
                    print(f"聴取ループエラー: {str(e)}")
                    time.sleep(0.1)
            
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
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
    
    def _check_wake_word(self):
        """ウェイクワードを検出"""
        try:
            if len(self.audio_buffer) < self.rate * 2:  # 2秒以上の音声が必要
                return
            
            # 音声データを結合
            audio_data = np.concatenate(self.audio_buffer)
            
            # Whisperで認識
            if self.model_loaded:
                segments, _ = self.whisper_model.transcribe(audio_data, language="ja")
                
                for segment in segments:
                    text = segment.text.strip()
                    if self.wake_word in text:
                        self.wake_word_detected = True
                        print(f"🎯 ウェイクワード検出: {text}")
                        
                        # VRMアバターに通知
                        self._notify_vrm("wake_word_detected")
                        
                        break
            
        except Exception as e:
            print(f"ウェイクワード検出エラー: {str(e)}")
    
    def _process_audio_buffer(self):
        """音声バッファを処理"""
        try:
            if len(self.audio_buffer) < self.rate * 0.5:  # 0.5秒未満は無視
                return
            
            # 音声データを結合
            audio_data = np.concatenate(self.audio_buffer)
            
            # Whisperで認識
            if self.model_loaded:
                segments, _ = self.whisper_model.transcribe(audio_data, language="ja")
                
                for segment in segments:
                    text = segment.text.strip()
                    if text and len(text) > 1:
                        # 感情分析
                        emotion_analysis = self.emotion_analyzer.analyze_voice(audio_data, self.rate)
                        
                        # ミラーリング学習
                        self.mirroring_system.learn_from_user_voice(emotion_analysis)
                        
                        # 結果を保存
                        self.last_recognition_result = {
                            'text': text,
                            'timestamp': datetime.now().isoformat(),
                            'confidence': segment.avg_logprob
                        }
                        
                        self.last_emotion_analysis = emotion_analysis
                        
                        print(f"🎤 認識結果: {text}")
                        print(f"😊 感情: {emotion_analysis['emotion']['dominant_emotion']}")
                        
                        # VRMアバターに通知
                        self._notify_vrm("voice_input", {
                            'text': text,
                            'emotion': emotion_analysis['emotion']['dominant_emotion']
                        })
                        
                        break
            
        except Exception as e:
            print(f"音声処理エラー: {str(e)}")
    
    def _notify_vrm(self, event_type: str, data: Dict = None):
        """VRMアバターに通知"""
        # VRM連携機能はメインアプリで実装
        pass
    
    def record_manual_input(self, duration: int = 5) -> Dict:
        """手動録音"""
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
            print(f"🎤 {duration}秒間録音開始...")
            
            for _ in range(int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            print("🎤 録音完了")
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # 音声データを結合
            audio_data = b''.join(frames)
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Whisperで認識
            result = {'text': '', 'emotion': None}
            
            if self.model_loaded:
                segments, _ = self.whisper_model.transcribe(audio_array, language="ja")
                
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        # 感情分析
                        emotion_analysis = self.emotion_analyzer.analyze_voice(audio_array, self.rate)
                        
                        # ミラーリング学習
                        self.mirroring_system.learn_from_user_voice(emotion_analysis)
                        
                        result = {
                            'text': text,
                            'emotion': emotion_analysis,
                            'confidence': segment.avg_logprob,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        self.last_recognition_result = result
                        self.last_emotion_analysis = emotion_analysis
                        
                        break
            
            return result
            
        except Exception as e:
            print(f"手動録音エラー: {str(e)}")
            return {'text': '', 'emotion': None, 'error': str(e)}
    
    def get_last_result(self) -> Dict:
        """最後の認識結果を取得"""
        return {
            'recognition': self.last_recognition_result,
            'emotion': self.last_emotion_analysis,
            'adaptation_summary': self.mirroring_system.get_learning_summary()
        }
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "start_listening":
            if self.start_listening():
                return "常時聴取を開始しました"
            else:
                return "すでに聴取中です"
        
        elif command == "stop_listening":
            if self.stop_listening():
                return "常時聴取を停止しました"
            else:
                return "聴取していません"
        
        elif command.startswith("record"):
            try:
                parts = command.split()
                duration = int(parts[1]) if len(parts) > 1 else 5
                result = self.record_manual_input(duration)
                if result.get('text'):
                    return f"認識結果: {result['text']} (感情: {result['emotion']['emotion']['dominant_emotion']})"
                else:
                    return "音声が認識されませんでした"
            except:
                return "録音コマンド形式: record [秒数]"
        
        elif command == "status":
            summary = self.mirroring_system.get_learning_summary()
            return f"音声入力状態: 聴取中={self.is_listening}, 学習回数={summary['total_interactions']}, 適応レベル={summary['adaptation_level']:.2f}"
        
        elif command == "last_result":
            result = self.get_last_result()
            if result['recognition']:
                return f"最後の認識: {result['recognition']['text']} (感情: {result['emotion']['emotion']['dominant_emotion']})"
            else:
                return "認識結果がありません"
        
        else:
            return "コマンド形式: start_listening, stop_listening, record [秒数], status, last_result"
