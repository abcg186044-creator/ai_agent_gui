#!/usr/bin/env python3
"""
VRM Avatar Integrated AI Agent Application
構文エラー修正版
"""

import streamlit as st
import requests
import json
import subprocess
import os
import sys
import time
import datetime
from pathlib import Path
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import threading
import queue
import pyttsx3
from browser_audio_component_fixed import audio_recorder_component

# セッション状態の初期化
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "current_personality" not in st.session_state:
    st.session_state.current_personality = "friend"

if "ollama" not in st.session_state:
    st.session_state.ollama = None

if "vrm_controller" not in st.session_state:
    st.session_state.vrm_controller = None

# Ollamaクラス
class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.models = ["llama3.1:8b", "llama3.2", "llama3.2-vision"]
    
    def check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt, model="llama3.1:8b"):
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(f"{self.base_url}/api/generate", json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                return None
        except Exception as e:
            print(f"Ollama生成エラー: {str(e)}")
            return None

# VRMアバターコントローラー
class VRMAvatarController:
    def __init__(self):
        self.current_personality = "friend"
        self.expressions = {
            "friend": "happy",
            "copy": "joy", 
            "expert": "neutral"
        }
        self.vrm_path = self._find_vrm_file()
    
    def _find_vrm_file(self):
        search_paths = [
            Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free") / "avatar.vrm",
            Path(__file__).parent / "static" / "avatar.vrm",
            Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free") / "EzoMomonga_Free.vrm",
            Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free\EzoMomonga_Free") / "EzoMomonga_Free.vrm",
            Path(__file__).parent / "static" / "EzoMomonga_Free.vrm",
        ]
        
        for vrm_path in search_paths:
            if vrm_path.exists():
                print(f"✅ VRMファイルを見つけました: {vrm_path}")
                if "static" not in str(vrm_path):
                    static_file = Path(__file__).parent / "static" / vrm_path.name
                    try:
                        import shutil
                        shutil.copy2(vrm_path, static_file)
                        print(f"📁 VRMファイルをstaticにコピー: {static_file}")
                        return f"/static/{vrm_path.name}"
                    except Exception as e:
                        print(f"❌ VRMファイルのコピーに失敗: {str(e)}")
                        continue
                else:
                    return f"/static/{vrm_path.name}"
        
        print("❌ VRMファイルが見つかりませんでした")
        return None
    
    def update_personality(self, personality):
        self.current_personality = personality
        return self.expressions.get(personality, "neutral")
    
    def set_personality(self, personality):
        return self.update_personality(personality)
    
    def get_vrm_html(self):
        if not self.vrm_path:
            return """
            <div style="width: 100%; height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                <div style="text-align: center; color: #666;">
                    <h3>🤖 VRMアバター</h3>
                    <p>VRMファイルが見つかりません</p>
                </div>
            </div>
            """
        
        return f"""
        <div style="width: 100%; height: 400px; background: #f0f0f0; border-radius: 10px; position: relative;">
            <canvas id="vrm-canvas" style="width: 100%; height: 100%; border-radius: 10px;"></canvas>
            <script src="https://cdn.jsdelivr.net/npm/three@0.150.0/build/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@2.0.7/lib/three-vrm.min.js"></script>
            <script>
                let scene, camera, renderer, vrmModel;
                
                async function initVRM() {{
                    scene = new THREE.Scene();
                    camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
                    camera.position.set(0, 1.2, 2.5);
                    
                    renderer = new THREE.WebGLRenderer({{
                        canvas: document.getElementById('vrm-canvas'),
                        antialias: true,
                        alpha: true
                    }});
                    renderer.setSize(400, 400);
                    renderer.setPixelRatio(window.devicePixelRatio);
                    
                    const light = new THREE.DirectionalLight(0xffffff, 1.0);
                    light.position.set(1, 1, 1);
                    scene.add(light);
                    
                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                    scene.add(ambientLight);
                    
                    try {{
                        const loader = new THREE.GLTFLoader();
                        const gltf = await loader.loadAsync('{self.vrm_path}');
                        vrmModel = await THREE.VRM.from(gltf);
                        scene.add(vrmModel.scene);
                        
                        vrmModel.humanoid.getBoneNode('head').rotation.y = Math.PI;
                        
                        updateVRMExpression('{self.expressions.get(self.current_personality, "neutral")}');
                    }} catch (error) {{
                        console.error('VRM読み込みエラー:', error);
                    }}
                    
                    animate();
                }}
                
                function updateVRMExpression(expressionName) {{
                    if (vrmModel && vrmModel.blendShapeProxy) {{
                        vrmModel.blendShapeProxy.setValue(expressionName, 1.0);
                    }}
                }}
                
                function animate() {{
                    requestAnimationFrame(animate);
                    
                    if (vrmModel && vrmModel.update) {{
                        vrmModel.update(clock.getDelta());
                    }}
                    
                    renderer.render(scene, camera);
                }}
                
                const clock = new THREE.Clock();
                
                window.updateVRMExpression = updateVRMExpression;
                
                initVRM();
            </script>
        </div>
        """

# 音声合成クラス
class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        
        # 日本語音声を優先
        for voice in voices:
            if 'japanese' in voice.name.lower() or 'ja' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
    
    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"音声合成エラー: {str(e)}")

# 会話履歴保存
def save_conversation(conversation, personality):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{personality}_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
        return filename
    except Exception as e:
        print(f"会話履歴保存エラー: {str(e)}")
        return None

# メインアプリケーション
def main():
    st.set_page_config(
        page_title="VRM AI Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 VRM AI Agent")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 人格選択
        st.subheader("🎭 人格設定")
        personalities = {
            "friend": {
                "name": "親友エンジニア",
                "prompt": "あなたは親しみやすいエンジニアです。カジュアルな口調で、技術的なことを分かりやすく説明してください。",
                "icon": "👨‍💻",
                "color": "#4CAF50"
            },
            "copy": {
                "name": "分身",
                "prompt": "あなたは私の分身です。私の考え方や話し方を真似して、共感的に対応してください。",
                "icon": "🪞",
                "color": "#2196F3"
            },
            "expert": {
                "name": "専門家",
                "prompt": "あなたはAIの専門家です。正確で詳細な情報を、専門用語を適切に使いながら提供してください。",
                "icon": "🎓",
                "color": "#FF9800"
            }
        }
        
        for key, info in personalities.items():
            if st.button(f"{info['icon']} {info['name']}", key=f"personality_{key}"):
                st.session_state.current_personality = key
                if st.session_state.vrm_controller:
                    st.session_state.vrm_controller.set_personality(key)
                
                # VRM表情更新
                if st.session_state.get('updateVRMExpression'):
                    js_code = f"window.updateVRMExpression('{st.session_state.vrm_controller.expressions.get(key, 'neutral')}');"
                    st.components.v1.html(f"<script>{js_code}</script>", height=0)
        
        # 現在の人格表示
        current_personality = personalities[st.session_state.current_personality]
        st.success(f"現在の人格: {current_personality['icon']} {current_personality['name']}")
        
        # Ollama接続確認
        if st.button("🔍 Ollama接続確認"):
            if not st.session_state.ollama:
                st.session_state.ollama = OllamaClient()
            
            if st.session_state.ollama.check_connection():
                st.success("✅ Ollamaに接続されています")
            else:
                st.error("❌ Ollamaに接続できません")
        
        # モデル管理
        st.subheader("📦 モデル管理")
        if st.session_state.ollama and st.session_state.ollama.check_connection():
            models_status = True
        else:
            models_status = False
        
        if models_status:
            st.success("✅ モデル利用可能")
            
            # 個別ダウンロード
            if st.button("📥 llama3.1:8b", help="llama3.1:8bモデルをダウンロード"):
                with st.spinner("llama3.1:8bをダウンロード中..."):
                    result = subprocess.run(["ollama", "pull", "llama3.1:8b"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ llama3.1:8bのダウンロードが完了しました")
                    else:
                        st.error(f"❌ ダウンロード失敗: {result.stderr}")
            
            if st.button("📥 llama3.2", help="llama3.2モデルをダウンロード"):
                with st.spinner("llama3.2をダウンロード中..."):
                    result = subprocess.run(["ollama", "pull", "llama3.2"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ llama3.2のダウンロードが完了しました")
                    else:
                        st.error(f"❌ ダウンロード失敗: {result.stderr}")
            
            if st.button("📥 llama3.2-vision", help="llama3.2-visionモデルをダウンロード"):
                with st.spinner("llama3.2-visionをダウンロード中..."):
                    result = subprocess.run(["ollama", "pull", "llama3.2-vision"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ llama3.2-visionのダウンロードが完了しました")
                    else:
                        st.error(f"❌ ダウンロード失敗: {result.stderr}")
            
            # 一括ダウンロード
            if st.button("📦 全モデル一括ダウンロード", help="すべてのモデルを一度にダウンロード"):
                with st.spinner("全モデルをダウンロード中..."):
                    models = ["llama3.1:8b", "llama3.2", "llama3.2-vision"]
                    success_count = 0
                    
                    for model in models:
                        result = subprocess.run(["ollama", "pull", model], capture_output=True, text=True)
                        if result.returncode == 0:
                            success_count += 1
                            st.success(f"✅ {model}のダウンロードが完了しました")
                        else:
                            st.error(f"❌ {model}のダウンロード失敗: {result.stderr}")
                    
                    if success_count == len(models):
                        st.success("✅ 全モデルのダウンロードが完了しました")
                    else:
                        st.warning(f"⚠️ {success_count}/{len(models)}モデルのダウンロードが完了しました")
        else:
            st.error("❌ モデル利用不可")
        
        # 会話履歴管理
        st.subheader("💬 会話履歴")
        if st.button("🗑️ 履歴をクリア"):
            st.session_state.conversation_history = []
            st.rerun()
        
        if st.button("💾 履歴を保存"):
            if st.session_state.conversation_history:
                filename = save_conversation(
                    st.session_state.conversation_history,
                    st.session_state.current_personality
                )
                st.success(f"会話履歴を保存しました: {filename}")
            else:
                st.warning("保存する会話履歴がありません")
        
        # 統計情報
        st.subheader("📊 統計")
        st.write(f"会話数: {len(st.session_state.conversation_history)}")
        if st.session_state.conversation_history:
            user_messages = [msg for msg in st.session_state.conversation_history if msg["role"] == "user"]
            ai_messages = [msg for msg in st.session_state.conversation_history if msg["role"] == "assistant"]
            st.write(f"ユーザー発言: {len(user_messages)}")
            st.write(f"AI応答: {len(ai_messages)}")
    
    # メインコンテンツ
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎙️ 音声入力")
        
        # 入力方法選択
        input_method = st.radio(
            "入力方法を選択:",
            ["🎙️ 音声入力", "💬 テキスト入力", "🤖 自動応答"],
            horizontal=True,
            help="音声、テキスト、または自動応答でAIと対話できます"
        )
        
        if input_method == "🎙️ 音声入力":
            # 音声録音コンポーネント
            audio_data, sample_rate = audio_recorder_component(key="ollama_audio")
            
            # 音声認識ボタン
            if st.button("🎤 音声認識", help="録音した音声をテキストに変換"):
                if audio_data is not None:
                    with st.spinner("音声認識中..."):
                        try:
                            # 音声ファイルを一時保存
                            temp_audio_path = "temp_audio.wav"
                            wav.write(temp_audio_path, sample_rate, audio_data)
                            
                            # 音声認識（ここではダミー実装）
                            recognized_text = "音声認識されたテキスト（ダミー）"
                            
                            st.session_state.recognized_text = recognized_text
                            st.success(f"認識結果: {recognized_text}")
                            
                            # 一時ファイルを削除
                            if os.path.exists(temp_audio_path):
                                os.remove(temp_audio_path)
                                
                        except Exception as e:
                            st.error(f"音声認識エラー: {str(e)}")
                else:
                    st.warning("音声データがありません。録音してください。")
        
        elif input_method == "💬 テキスト入力":
            # テキスト入力エリア
            user_text = st.text_area(
                "💬 メッセージを入力:",
                value=st.session_state.get("user_input_text", ""),
                height=100,
                placeholder="ここにメッセージを入力してください...",
                help="AIとの対話メッセージを入力します"
            )
            
            # 入力テキストを保存
            st.session_state.user_input_text = user_text
            
            # テキスト送信ボタン
            if st.button("📤 メッセージ送信", help="入力したメッセージをAIに送信"):
                if user_text.strip():
                    st.session_state.recognized_text = user_text.strip()
                    st.success(f"送信メッセージ: {user_text.strip()}")
                else:
                    st.warning("メッセージを入力してください。")
        
        else:  # 自動応答
            st.subheader("🤖 自動応答モード")
            st.write("AIが自動的に会話を開始し、継続的に応答します。")
            
            # 自動応答設定
            col_auto1, col_auto2 = st.columns([2, 1])
            with col_auto1:
                auto_topic = st.selectbox(
                    "会話トピックを選択:",
                    ["天気について", "最新の技術ニュース", "自己紹介", "雑談", "専門的な相談"],
                    help="AIが自動的に話題を提供します"
                )
            
            with col_auto2:
                auto_count = st.number_input(
                    "応答回数:",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="自動応答の回数を設定"
                )
            
            # 自動応答開始ボタン
            if st.button("🚀 自動応答開始", help="AIが自動的に会話を開始します"):
                with st.spinner("AIが自動応答を生成中..."):
                    try:
                        # 初期プロンプトを生成
                        topic_prompts = {
                            "天気について": "今日の天気について自然な会話を始めてください。天気の話題から関連する話題に広げてください。",
                            "最新の技術ニュース": "最新の技術ニュースについて興味深い話題を提供し、解説してください。",
                            "自己紹介": "自己紹介をしてください。あなたの能力や特徴について詳しく説明してください。",
                            "雑談": "楽しい雑談をしてください。ユーザーを楽しませるような話題を選んでください。",
                            "専門的な相談": "専門家として、ユーザーが相談したいであろう専門的な質問と回答を提供してください。"
                        }
                        
                        # 人格に応じたプロンプトを作成
                        personality = st.session_state.current_personality
                        current_personality = personalities[personality]
                        base_prompt = topic_prompts[auto_topic]
                        
                        # 自動応答生成
                        auto_responses = []
                        for i in range(auto_count):
                            # 会話履歴を整形
                            conversation_history = st.session_state.conversation_history[-5:]
                            history_text = ""
                            for conv in conversation_history:
                                history_text += f"User: {conv['user']}\nAssistant: {conv['assistant']}\n"
                            
                            # プロンプト構築
                            if i == 0:
                                prompt = f"""{current_personality['prompt']}

{base_prompt}

{history_text}
Assistant:"""
                            else:
                                # 前の応答から次の話題を生成
                                prev_response = auto_responses[-1] if auto_responses else ""
                                prompt = f"""{current_personality['prompt']}

前の応答から自然に会話を続けてください。新しい視点や関連する話題を提供してください。

前の応答: {prev_response}

{history_text}
Assistant:"""
                            
                            # Ollamaで応答生成
                            if not st.session_state.ollama:
                                st.session_state.ollama = OllamaClient()
                            
                            response = st.session_state.ollama.generate_response(prompt)
                            
                            if response:
                                auto_responses.append(response)
                                
                                # 会話履歴に追加
                                st.session_state.conversation_history.append({
                                    "user": f"自動応答 {i+1} ({auto_topic})",
                                    "assistant": response,
                                    "personality": personality,
                                    "timestamp": datetime.datetime.now().isoformat()
                                })
                        
                        # 自動応答結果を表示
                        st.success(f"✅ 自動応答を {len(auto_responses)} 件生成しました！")
                        
                        for i, response in enumerate(auto_responses):
                            with st.expander(f"🤖 自動応答 {i+1}"):
                                st.write(response)
                        
                        # VRMアバター表情更新
                        if st.session_state.vrm_controller:
                            st.session_state.vrm_controller.set_personality(personality)
                        
                    except Exception as e:
                        st.error(f"自動応答生成エラー: {str(e)}")
        
        # 認識結果・入力結果表示
        if "recognized_text" in st.session_state and st.session_state.recognized_text:
            st.subheader("💭 入力内容")
            st.write(st.session_state.recognized_text)
            
            # AI応答生成
            if st.button("🤖 AI応答生成", help="入力内容に対するAI応答を生成"):
                with st.spinner("AI応答を生成中..."):
                    try:
                        # 人格に応じたプロンプトを作成
                        personality = st.session_state.current_personality
                        current_personality = personalities[personality]
                        
                        # 会話履歴を整形
                        conversation_history = st.session_state.conversation_history[-5:]
                        history_text = ""
                        for conv in conversation_history:
                            history_text += f"User: {conv['user']}\nAssistant: {conv['assistant']}\n"
                        
                        # プロンプト構築
                        prompt = f"""{current_personality['prompt']}

以下のユーザーの入力に対して、人格に応じて自然に応答してください。

ユーザー入力: {st.session_state.recognized_text}

{history_text}
Assistant:"""
                        
                        # Ollamaで応答生成
                        if not st.session_state.ollama:
                            st.session_state.ollama = OllamaClient()
                        
                        response = st.session_state.ollama.generate_response(prompt)
                        
                        if response:
                            # 会話履歴に追加
                            st.session_state.conversation_history.append({
                                "user": st.session_state.recognized_text,
                                "assistant": response,
                                "personality": personality,
                                "timestamp": datetime.datetime.now().isoformat()
                            })
                            
                            # 応答表示
                            st.subheader("🤖 AI応答")
                            st.write(response)
                            
                            # VRMアバター表情更新
                            if st.session_state.vrm_controller:
                                st.session_state.vrm_controller.set_personality(personality)
                            
                            # 音声合成
                            if st.button("🔊 応答を音声で再生", key="tts_button"):
                                with st.spinner("音声合成中..."):
                                    try:
                                        tts_engine = TTSEngine()
                                        tts_engine.speak(response)
                                        st.success("✅ 音声再生が完了しました")
                                    except Exception as e:
                                        st.error(f"音声合成エラー: {str(e)}")
                        else:
                            st.error("❌ AI応答の生成に失敗しました")
                            
                    except Exception as e:
                        st.error(f"AI応答生成エラー: {str(e)}")
    
    with col2:
        st.header("🎭 VRMアバター")
        
        # VRMアバター表示
        if not st.session_state.vrm_controller:
            st.session_state.vrm_controller = VRMAvatarController()
        
        if st.session_state.vrm_controller.vrm_path:
            vrm_html = st.session_state.vrm_controller.get_vrm_html()
            st.components.v1.html(vrm_html, height=450)
        else:
            st.error("❌ VRMファイルが見つかりません")
        
        # 現在の人格情報表示
        current_personality = personalities[st.session_state.current_personality]
        st.info(f"""
        **現在の人格**: {current_personality['icon']} {current_personality['name']}
        
        **表情**: {st.session_state.vrm_controller.expressions.get(st.session_state.current_personality, 'neutral')}
        """)
    
    # 会話履歴表示
    if st.session_state.conversation_history:
        st.header("💬 会話履歴")
        
        for i, msg in enumerate(reversed(st.session_state.conversation_history[-10:])):
            with st.expander(f"💭 {msg['user'][:30]}... ({msg.get('timestamp', 'N/A')})"):
                st.write(f"**ユーザー**: {msg['user']}")
                st.write(f"**AI**: {msg['assistant']}")
                st.write(f"**人格**: {msg.get('personality', 'N/A')}")
    else:
        st.info("会話履歴がありません。AIとの対話を始めてください。")

if __name__ == "__main__":
    main()
