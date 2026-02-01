import streamlit as st
import numpy as np
import tempfile
import json
import requests
import time
import asyncio
import subprocess
import os
from datetime import datetime
from browser_audio_component_fixed import audio_recorder_component

# Ollama連携（Docker内完結型）
OLLAMA_HOST = "localhost"
OLLAMA_PORT = "11434"
OLLAMA_MODEL = "llama3.1:8b"

class OllamaIntegration:
    def __init__(self):
        self.base_url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
        self.model = OLLAMA_MODEL
    
    def check_connection(self):
        """Ollama接続確認"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt, personality="friend"):
        """人格に応じたAI応答生成"""
        # 人格別システムプロンプト
        personality_prompts = {
            "friend": "あなたは親切でフレンドリーなエンジニアです。ユーザーの親友として、分かりやすく楽しく会話してください。",
            "copy": "あなたはユーザーの分身です。ユーザーと同じ視点で、共感しながら応答してください。",
            "expert": "あなたは専門家です。正確で詳細な情報を提供し、的確なアドバイスをしてください。"
        }
        
        system_prompt = personality_prompts.get(personality, personality_prompts["friend"])
        full_prompt = f"{system_prompt}\n\nユーザー: {prompt}\n応答: "
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "応答を生成できませんでした。")
            else:
                return f"APIエラー: {response.status_code}"
                
        except Exception as e:
            return f"Ollamaエラー: {str(e)}"
    
    def pull_model(self):
        """モデルダウンロード（Dockerビルド時に実行済みのため不要）"""
        return True
    
    def check_models_loaded(self):
        """モデルがVRAMにロードされているか確認"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                return {
                    "llama3.1:8b": "llama3.1:8b" in model_names,
                    "llama3.2:latest": "llama3.2:latest" in model_names,
                    "llama3.2-vision:latest": "llama3.2-vision:latest" in model_names,
                    "total_models": len(models)
                }
            return {}
        except:
            return {}

class VRMAvatarController:
    def __init__(self):
        self.current_personality = "friend"
        self.expressions = {
            "friend": "happy",
            "copy": "joy", 
            "expert": "neutral"
        }
        # VRMファイルパスを確認
        self.vrm_path = self._find_vrm_file()
    
    def _find_vrm_file(self):
        """VRMファイルを検索"""
        import os
        from pathlib import Path
        
        # 検索パスの優先順位
        search_paths = [
            Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free") / "avatar.vrm",  # 1. 指定デスクトップ（優先）
            Path(__file__).parent / "static" / "avatar.vrm",           # 2. アプリ用デフォルト
            Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free") / "EzoMomonga_Free.vrm",  # 3. 元ファイル名
            Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free") / "VRM_Sample_Basic.glb",  # 4. glbファイル
            Path(__file__).parent / "static" / "EzoMomonga_Free.vrm",  # 5. アプリ用コピー
            Path(__file__).parent / "static" / "VRM_Sample_Basic.glb",  # 6. アプリ用glb
        ]
        
        for vrm_path in search_paths:
            if vrm_path.exists():
                print(f"✅ VRMファイルを見つけました: {vrm_path}")
                # staticディレクトリ内のファイルは /static/ パスを返す
                if "static" in str(vrm_path):
                    return f"/static/{vrm_path.name}"
                else:
                    # デスクトップのファイルはstaticにコピーして参照
                    static_file = Path(__file__).parent / "static" / vrm_path.name
                    try:
                        import shutil
                        shutil.copy2(vrm_path, static_file)
                        print(f"📁 VRMファイルをstaticにコピー: {static_file}")
                        return f"/static/{vrm_path.name}"
                    except Exception as e:
                        print(f"❌ VRMファイルのコピーに失敗: {str(e)}")
                        continue
        
        print("⚠️ VRMファイルが見つかりません。プレースホルダーを使用します。")
        return "/static/avatar.vrm"
    
    def update_personality(self, personality):
        """人格切り替え"""
        self.current_personality = personality
        return self.expressions.get(personality, "neutral")
    
    def set_personality(self, personality):
        """人格を設定（update_personalityのエイリアス）"""
        return self.update_personality(personality)
    
    def get_vrm_html(self):
        """VRM表示用HTML"""
        return f"""
        <div id="vrm-container" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
            <canvas id="vrm-canvas"></canvas>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@1.0.0/lib/three-vrm.min.js"></script>
        
        <script>
        let scene, camera, renderer, vrmModel;
        let currentExpression = "{self.expressions[self.current_personality]}";
        
        async function initVRM() {{
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
            camera.position.set(0, 1.2, 3);
            
            renderer = new THREE.WebGLRenderer({{ canvas: document.getElementById('vrm-canvas'), antialias: true }});
            renderer.setSize(400, 400);
            renderer.setClearColor(0xf0f0f0);
            
            // 照明
            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(1, 1, 1);
            scene.add(light);
            
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambientLight);
            
            // VRMモデル読み込み
            try {{
                const loader = new THREE.VRMLoader();
                const gltf = await loader.loadAsync('{self.vrm_path}');
                vrmModel = await THREE.VRMUtils.importVRM(gltf);
                scene.add(vrmModel);
                
                // 表情設定
                if (vrmModel.blendShapeProxy) {{
                    vrmModel.blendShapeProxy.setValue(currentExpression, 1.0);
                }}
                
                animate();
            }} catch (error) {{
                console.error('VRM読み込みエラー:', error);
                // フォールバック: 簡単な3Dオブジェクトを表示
                const geometry = new THREE.BoxGeometry(1, 2, 1);
                const material = new THREE.MeshBasicMaterial({{ color: 0x4CAF50 }});
                const cube = new THREE.Mesh(geometry, material);
                scene.add(cube);
                animate();
            }}
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            
            if (vrmModel && vrmModel.update) {{
                vrmModel.update(clock.getDelta());
            }}
            
            renderer.render(scene, camera);
        }}
        
        function updateExpression(expression) {{
            if (vrmModel && vrmModel.blendShapeProxy) {{
                // すべての表情をリセット
                vrmModel.blendShapeProxy.clear();
                // 新しい表情を設定
                vrmModel.blendShapeProxy.setValue(expression, 1.0);
            }}
            currentExpression = expression;
        }}
        
        // 初期化
        initVRM();
        
        // 表情更新関数をグローバルに公開
        window.updateVRMExpression = updateExpression;
        </script>
        """

def speech_to_text(audio_data, sample_rate):
    """音声認識"""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", compute_type="float32")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            import wave
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
            
            segments, info = model.transcribe(temp_file.name, language="ja")
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "
            
            return transcription.strip()
            
    except Exception as e:
        return f"音声認識エラー: {str(e)}"

def text_to_speech(text, voice_character="female"):
    """音声合成"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # 音声キャラクター設定
        voices = engine.getProperty('voices')
        if voice_character == "female" and len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        elif voice_character == "male" and len(voices) > 0:
            engine.setProperty('voice', voices[0].id)
        
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 0.9)
        
        # 音声ファイル保存
        filename = f"tts_output_{int(time.time())}.mp3"
        engine.save_to_file(text, filename)
        engine.runAndWait()
        
        return filename
        
    except Exception as e:
        return f"音声合成エラー: {str(e)}"

def save_conversation(conversation_history, personality):
    """会話履歴保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{personality}_{timestamp}.json"
    
    data = {
        "timestamp": timestamp,
        "personality": personality,
        "conversation": conversation_history
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def main():
    # モバイル対応設定
    st.set_page_config(
        page_title="AI Agent System",
        page_icon="🤖", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # モバイル対応CSS
    st.markdown("""
    <style>
    /* モバイル対応スタイル */
    @media (max-width: 768px) {
        .stSelectbox > div > div > select {
            font-size: 16px !important;
        }
        .stButton > button {
            font-size: 16px !important;
            padding: 12px 24px !important;
        }
        .stTextInput > div > input {
            font-size: 16px !important;
        }
        .stTextArea > div > textarea {
            font-size: 16px !important;
        }
        .element-container {
            padding: 0.5rem !important;
        }
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    }
    
    /* タッチ対応 */
    .stButton > button {
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    
    /* VRMコンテナのモバイル対応 */
    #vrm-container {
        max-width: 100%;
        height: auto;
        aspect-ratio: 1/1;
    }
    
    #vrm-canvas {
        width: 100% !important;
        height: 100% !important;
    }
    
    /* 音声コントロールのモバイル対応 */
    .audio-controls {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 10px;
    }
    
    .audio-controls button {
        width: 100%;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🤖 Ollama + VRM + 音声認識 AIエージェント")
    
    # アクセス情報表示
    client_ip = st.experimental_get_query_params().get("client_ip", ["Unknown"])[0]
    user_agent = st.experimental_get_query_params().get("user_agent", ["Unknown"])[0]
    
    # モバイルデバイス検出
    is_mobile = "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent
    
    if is_mobile:
        st.info("📱 モバイルデバイスからアクセスしています。タッチ操作に最適化された表示です。")
    else:
        st.info("🖥️ デスクトップからアクセスしています。")
    
    # Tailscaleアクセス情報
    if "tailscale" in client_ip.lower() or "100." in client_ip.split('.')[0]:
        st.success("🌐 Tailscale経由でアクセスしています。安全なプライベート接続が確立されています。")
    
    # セッション状態初期化
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "current_personality" not in st.session_state:
        st.session_state.current_personality = "friend"
    if "ollama" not in st.session_state:
        st.session_state.ollama = OllamaIntegration()
    if "vrm_controller" not in st.session_state:
        st.session_state.vrm_controller = VRMAvatarController()
    
    # サイドバー：設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 人格切り替え
        st.subheader("🎭 人格切り替え")
        personalities = {
            "friend": {"name": "親友エンジニア", "color": "#4CAF50", "icon": "😊"},
            "copy": {"name": "分身", "color": "#2196F3", "icon": "🪞"},
            "expert": {"name": "エキスパート", "color": "#9C27B0", "icon": "🎓"}
        }
        
        for key, info in personalities.items():
            if st.button(f"{info['icon']} {info['name']}", key=f"personality_{key}"):
                st.session_state.current_personality = key
                expression = st.session_state.vrm_controller.update_personality(key)
                # VRM表情更新（JavaScript呼び出し）
                st.components.v1.html(f"""
                <script>
                if (window.updateVRMExpression) {{
                    window.updateVRMExpression('{expression}');
                }}
                </script>
                """, height=0)
                st.rerun()
        
        # 現在の人格表示
        current_info = personalities[st.session_state.current_personality]
        st.markdown(f"**現在の人格:** {current_info['icon']} {current_info['name']}")
        
        # Ollama設定
        st.subheader("🤖 Ollama設定")
        if st.button("🔍 Ollama接続確認"):
            if st.session_state.ollama.check_connection():
                st.success("✅ Ollamaに接続されています")
                
                # モデルロード状況確認
                models_status = st.session_state.ollama.check_models_loaded()
                if models_status:
                    st.subheader("📦 モデルロード状況")
                    for model_name, is_loaded in models_status.items():
                        if model_name != "total_models":
                            status = "✅ ロード済み" if is_loaded else "❌ 未ロード"
                            st.write(f"{model_name}: {status}")
                    st.write(f"総モデル数: {models_status.get('total_models', 0)}")
                else:
                    st.warning("⚠️ モデル情報を取得できません")
            else:
                st.error("❌ Ollamaに接続できません")
                st.info("コンテナ内のOllamaサービスを確認してください")
        
        # システム情報表示
        st.subheader("📊 システム情報")
        if st.button("🔍 システム状態確認"):
            try:
                # GPU情報（Docker内から取得）
                try:
                    gpu_info = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"], 
                                            capture_output=True, text=True, timeout=10)
                    if gpu_info.returncode == 0:
                        st.success("✅ GPU情報取得")
                        st.code(gpu_info.stdout)
                        gpu_mode = "GPU"
                    else:
                        st.warning("⚠️ GPU情報を取得できません (CPUモードで実行中)")
                        gpu_mode = "CPU"
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    st.warning("⚠️ GPU情報を取得できません (CPUモードで実行中)")
                    gpu_mode = "CPU"
                
                # Ollamaプロセス確認
                try:
                    ollama_process = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True, text=True, timeout=5)
                    if ollama_process.returncode == 0:
                        st.success("✅ Ollamaプロセス実行中")
                    else:
                        st.error("❌ Ollamaプロセスが実行されていません")
                except subprocess.TimeoutExpired:
                    st.warning("⚠️ Ollamaプロセス確認タイムアウト")
                    
                # システムリソース情報
                try:
                    import psutil
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    st.write(f"**実行モード:** {gpu_mode}")
                    st.write(f"**CPU使用率:** {cpu_percent}%")
                    st.write(f"**メモリ使用率:** {memory.percent}%")
                    st.write(f"**利用可能メモリ:** {memory.available / (1024**3):.1f}GB")
                    st.write(f"**ディスク使用率:** {disk.percent}%")
                    st.write(f"**利用可能ディスク:** {disk.free / (1024**3):.1f}GB")
                    
                    # プロセス情報
                    st.write("**実行中のプロセス:**")
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        try:
                            if 'ollama' in proc.info['name'].lower() or 'streamlit' in proc.info['name'].lower() or 'fastapi' in proc.info['name'].lower():
                                st.write(f"- {proc.info['name']} (PID: {proc.info['pid']}, CPU: {proc.info['cpu_percent']}%)")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                            
                except ImportError:
                    st.info("psutilがインストールされていません")
                except Exception as e:
                    st.warning(f"システムリソース情報取得エラー: {str(e)}")
                    
            except Exception as e:
                st.error(f"システム情報取得エラー: {str(e)}")
        
        # モデル事前ロード機能
        st.subheader("📦 モデル管理")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 llama3.1:8b", help="llama3.1:8bモデルをダウンロード"):
                with st.spinner("llama3.1:8bをダウンロード中..."):
                    try:
                        result = subprocess.run(["ollama", "pull", "llama3.1:8b"], 
                                            capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            st.success("✅ llama3.1:8bダウンロード完了")
                        else:
                            st.error(f"❌ ダウンロード失敗: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        st.error("❌ ダウンロードタイムアウト")
                    except Exception as e:
                        st.error(f"❌ ダウンロードエラー: {str(e)}")
        
        with col2:
            if st.button("📥 llama3.2", help="llama3.2モデルをダウンロード"):
                with st.spinner("llama3.2をダウンロード中..."):
                    try:
                        result = subprocess.run(["ollama", "pull", "llama3.2:latest"], 
                                            capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            st.success("✅ llama3.2ダウンロード完了")
                        else:
                            st.error(f"❌ ダウンロード失敗: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        st.error("❌ ダウンロードタイムアウト")
                    except Exception as e:
                        st.error(f"❌ ダウンロードエラー: {str(e)}")
        
        with col3:
            if st.button("📥 llama3.2-vision", help="llama3.2-visionモデルをダウンロード"):
                with st.spinner("llama3.2-visionをダウンロード中..."):
                    try:
                        result = subprocess.run(["ollama", "pull", "llama3.2-vision:latest"], 
                                            capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            st.success("✅ llama3.2-visionダウンロード完了")
                        else:
                            st.error(f"❌ ダウンロード失敗: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        st.error("❌ ダウンロードタイムアウト")
                    except Exception as e:
                        st.error(f"❌ ダウンロードエラー: {str(e)}")
        
        # モデル一括ダウンロード
        if st.button("📦 全モデル一括ダウンロード", help="すべてのモデルを一度にダウンロード"):
            models = ["llama3.1:8b", "llama3.2:latest", "llama3.2-vision:latest"]
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, model in enumerate(models):
                status_text.text(f"{model}をダウンロード中... ({i+1}/{len(models)})")
                try:
                    result = subprocess.run(["ollama", "pull", model], 
                                        capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        st.success(f"✅ {model}ダウンロード完了")
                    else:
                        st.error(f"❌ {model}ダウンロード失敗: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error(f"❌ {model}ダウンロードタイムアウト")
                except Exception as e:
                    st.error(f"❌ {model}ダウンロードエラー: {str(e)}")
                
                progress_bar.progress((i + 1) / len(models))
            
            status_text.text("全モデルダウンロード完了！")
        
        # モデル一覧表示
        if st.button("📋 モデル一覧表示"):
            try:
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ 利用可能なモデル:")
                    st.code(result.stdout)
                else:
                    st.error(f"❌ モデル一覧取得失敗: {result.stderr}")
            except Exception as e:
                st.error(f"❌ モデル一覧取得エラー: {str(e)}")
        
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
                            # faster-whisperで音声認識
                            from faster_whisper import WhisperModel
                            
                            # モデル初期化
                            model = WhisperModel("base", compute_type="int8")
                            
                            # 音声認識実行
                            segments, info = model.transcribe(audio_data, language="ja")
                            
                            # 認識結果を結合
                            recognized_text = " ".join([segment.text for segment in segments])
                            
                            if recognized_text.strip():
                                st.session_state.recognized_text = recognized_text
                                st.success(f"認識結果: {recognized_text}")
                            else:
                                st.warning("音声が認識できませんでした。もう一度お試しください。")
                                 
                        except Exception as e:
                            st.error(f"音声認識エラー: {str(e)}")
                else:
                    st.warning("音声データがありません。録音してください。")
        
        else:  # テキスト入力
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
        
        else:
                    if input_method == "🤖 自動応答":
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
                                personalities = {
                                    "friend": {
                                        "name": "親友エンジニア",
                                        "prompt": "あなたは親しみやすいエンジニアです。カジュアルな口調で、技術的なことを分かりやすく説明してください。",
                                        "icon": "👨‍💻"
                                    },
                                    "copy": {
                                        "name": "分身",
                                        "prompt": "あなたは私の分身です。私の考え方や話し方を真似して、共感的に対応してください。",
                                        "icon": "🪞"
                                    },
                                    "expert": {
                                        "name": "専門家",
                                        "prompt": "あなたはAIの専門家です。正確で詳細な情報を、専門用語を適切に使いながら提供してください。",
                                        "icon": "🎓"
                                    }
                                }
                        
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
                                    response = st.session_state.ollama.generate_response(prompt)
                            
                                    if response:
                                        auto_responses.append(response)
                                
                                        # 会話履歴に追加
                                        st.session_state.conversation_history.append({
                                            "user": f"自動応答 {i+1} ({auto_topic})",
                                            "assistant": response,
                                            "personality": personality,
                                            "timestamp": datetime.now().isoformat()
                                        })
                        
                                # 自動応答結果を表示
                                st.success(f"✅ 自動応答を {len(auto_responses)} 件生成しました！")
                        
                                for i, response in enumerate(auto_responses):
                                    with st.expander(f"🤖 自動応答 {i+1}"):
                                        st.write(response)
                        
                                # VRMアバター表情更新
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
                                personalities = {
                                    "friend": {
                                        "name": "親友エンジニア",
                                        "prompt": "あなたは親しみやすいエンジニアです。カジュアルな口調で、技術的なことを分かりやすく説明してください。",
                                        "icon": "👨‍💻"
                                    },
                                    "copy": {
                                        "name": "分身",
                                        "prompt": "あなたは私の分身です。私の考え方や話し方を真似して、共感的に対応してください。",
                                        "icon": "🪞"
                                    },
                                    "expert": {
                                        "name": "専門家",
                                        "prompt": "あなたはAIの専門家です。正確で詳細な情報を、専門用語を適切に使いながら提供してください。",
                                        "icon": "🎓"
                                    }
                                }
                        
                                current_personality = personalities[personality]
                        
                                # 会話履歴を整形
                                conversation_history = st.session_state.conversation_history[-5:]  # 直近5件を使用
                                history_text = ""
                                for conv in conversation_history:
                                    history_text += f"User: {conv['user']}\nAssistant: {conv['assistant']}\n"
                        
                                # プロンプト構築
                                prompt = f"""{current_personality['prompt']}

        {history_text}User: {st.session_state.recognized_text}
        Assistant:"""
                        
                                # Ollamaで応答生成
                                response = st.session_state.ollama.generate_response(prompt)
                        
                                if response:
                                    # 会話履歴に追加
                                    st.session_state.conversation_history.append({
                                        "user": st.session_state.recognized_text,
                                        "assistant": response,
                                        "personality": personality,
                                        "timestamp": datetime.now().isoformat()
                                    })
                            
                                    # 応答表示
                                    st.subheader(f"🤖 {current_personality['name']}の応答")
                                    st.write(response)
                            
                                    # VRMアバター表情更新
                                    st.session_state.vrm_controller.set_personality(personality)
                            
                                    # 音声合成（オプション）
                                    if st.button("🔊 応答を音声で再生", key="tts_button"):
                                        try:
                                            import pyttsx3
                                            engine = pyttsx3.init()
                                            engine.say(response)
                                            engine.runAndWait()
                                            st.success("音声再生完了")
                                        except Exception as e:
                                            st.error(f"音声合成エラー: {str(e)}")
                            
                                    # 入力をクリア
                                    st.session_state.recognized_text = ""
                                    if input_method == "💬 テキスト入力":
                                        st.session_state.user_input_text = ""
                        
                                else:
                                    st.error("AI応答を生成できませんでした。")
                            
                            except Exception as e:
                                st.error(f"AI応答生成エラー: {str(e)}")
    
            with col2:
                st.header("🤖 VRMアバター")
        
                # VRMアバター表示
                vrm_html = st.session_state.vrm_controller.get_vrm_html()
                st.components.v1.html(vrm_html, height=450)
        
                # 人格情報表示
                st.subheader("🎭 現在の人格")
                personalities = {
                    "friend": {"name": "親友エンジニア", "color": "#4CAF50", "icon": "😊"},
                    "copy": {"name": "分身", "color": "#2196F3", "icon": "🪞"},
                    "expert": {"name": "エキスパート", "color": "#9C27B0", "icon": "🎓"}
                }
                current_info = personalities[st.session_state.current_personality]
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 8px; background-color: {current_info['color']}20; border: 2px solid {current_info['color']};">
                    <h3 style="color: {current_info['color']}; margin: 0;">{current_info['icon']} {current_info['name']}</h3>
                    <p style="margin: 5px 0;">表情: {st.session_state.vrm_controller.expressions[st.session_state.current_personality]}</p>
                </div>
                """, unsafe_allow_html=True)
    
            # 会話履歴表示
            st.header("💬 会話履歴")
    
            if st.session_state.conversation_history:
                for i, msg in enumerate(reversed(st.session_state.conversation_history[-10:])):
                    if msg["role"] == "user":
                        st.markdown(f"👤 **あなた**: {msg['content']}")
                    else:
                        st.markdown(f"🤖 **AI**: {msg['content']}")
                    st.divider()
            else:
                st.info("会話履歴がありません。音声入力またはテキスト入力で会話を始めてください。")
    
            # フッター情報
            st.markdown("---")
            st.markdown("### 📋 使い方")
            st.markdown("""
            1. **🔧 マイクテスト**: マイクが正常に動作するか確認
            2. **🎭 人格選択**: 3つの人格から選択
            3. **🎤 音声入力**: 音声を録音してテキストに変換
            4. **💬 テキスト入力**: 直接テキストを入力して対話
            5. **🤖 AI応答**: Ollamaで応答生成
            6. **🤖 VRM表示**: 3Dアバターで表情表示
            7. **💾 保存**: 会話履歴を保存
            """)
    
            # 技術情報
            with st.expander("🔧 技術情報"):
                st.markdown("""
                **使用技術:**
                - WebRTC/MediaRecorder API (音声録音)
                - faster-whisper (音声認識)
                - Ollama + llama3.1:8b (AI応答)
                - pyttsx3 (音声合成)
                - Three.js + three-vrm (3Dアバター)
                - Streamlit (UIフレームワーク)
        
                **特徴:**
                - ローカルAIモデル (Ollama)
                - 3Dアバター連携 (VRM)
                - マルチ人格システム
                - 音声対話機能
                - 会話履歴管理
                """)

        if __name__ == "__main__":
            main()
