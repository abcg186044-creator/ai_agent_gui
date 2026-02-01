import streamlit as st
import requests
import json
import datetime
import os
import sys
from pathlib import Path

# VRMアバター制御クラス
class VRMAvatarController:
    def __init__(self):
        self.vrm_path = self._find_vrm_file()
        self.current_personality = "friendly_engineer"
        self.expressions = {
            "friendly_engineer": "happy",
            "split_personality": "joy", 
            "expert": "neutral"
        }
    
    def _find_vrm_file(self):
        """VRMファイルを検索"""
        # 優先順位: ユーザーのデスクトップ → アプリのstaticディレクトリ
        desktop_path = Path.home() / "Desktop" / "EzoMomonga_Free"
        static_path = Path("static")
        
        # デスクトップを優先
        for search_path in [desktop_path, static_path]:
            if search_path.exists():
                for vrm_file in search_path.glob("*.vrm"):
                    if search_path == desktop_path:
                        # デスクトップのファイルをstaticにコピー
                        static_vrm = static_path / vrm_file.name
                        if not static_vrm.exists():
                            static_path.mkdir(exist_ok=True)
                            import shutil
                            shutil.copy2(vrm_file, static_vrm)
                        return f"/static/{vrm_file.name}"
                    else:
                        return f"/static/{vrm_file.name}"
        
        print("❌ VRMファイルが見つかりませんでした")
        return None
    
    def update_personality(self, personality):
        self.current_personality = personality
        return self.expressions.get(personality, "neutral")
    
    def set_personality(self, personality):
        return self.update_personality(personality)
    
    def _check_vrm_command(self, text):
        """VRM制御コマンドをチェック"""
        vrm_commands = {
            "アバターを非表示": {"action": "hide", "target": "avatar"},
            "アバターを表示": {"action": "show", "target": "avatar"},
            "アバターを消して": {"action": "hide", "target": "avatar"},
            "アバターを出して": {"action": "show", "target": "avatar"},
            "VRMを非表示": {"action": "hide", "target": "avatar"},
            "VRMを表示": {"action": "show", "target": "avatar"},
            "自分を隠して": {"action": "hide", "target": "avatar"},
            "自分を見せて": {"action": "show", "target": "avatar"},
            "大きくして": {"action": "scale", "target": "avatar", "value": 1.2},
            "小さくして": {"action": "scale", "target": "avatar", "value": 0.8},
            "拡大して": {"action": "scale", "target": "avatar", "value": 1.2},
            "縮小して": {"action": "scale", "target": "avatar", "value": 0.8},
            "回転して": {"action": "rotate", "target": "avatar", "value": 45},
            "左に回転": {"action": "rotate", "target": "avatar", "value": -45},
            "右に回転": {"action": "rotate", "target": "avatar", "value": 45},
            "表情を変えて": {"action": "expression", "target": "avatar"},
            "笑って": {"action": "expression", "target": "avatar", "value": "happy"},
            "喜んで": {"action": "expression", "target": "avatar", "value": "joy"},
            "普通の表情": {"action": "expression", "target": "avatar", "value": "neutral"},
            "悲しい表情": {"action": "expression", "target": "avatar", "value": "sad"},
            "怒って": {"action": "expression", "target": "avatar", "value": "angry"},
        }
        
        for command, action in vrm_commands.items():
            if command in text:
                return action
        return None
    
    def _execute_vrm_command(self, command):
        """VRM制御コマンドを実行"""
        action = command["action"]
        target = command["target"]
        
        if action == "hide":
            if "vrm_visible" not in st.session_state:
                st.session_state.vrm_visible = True
            st.session_state.vrm_visible = False
            return "VRMアバターを非表示にしました。"
        
        elif action == "show":
            if "vrm_visible" not in st.session_state:
                st.session_state.vrm_visible = True
            st.session_state.vrm_visible = True
            return "VRMアバターを表示しました。"
        
        elif action == "scale":
            if "vrm_scale" not in st.session_state:
                st.session_state.vrm_scale = 1.0
            st.session_state.vrm_scale *= command["value"]
            return f"VRMアバターを{command['value']}倍に拡大縮小しました。"
        
        elif action == "rotate":
            if "vrm_rotation" not in st.session_state:
                st.session_state.vrm_rotation = 0
            st.session_state.vrm_rotation += command["value"]
            return f"VRMアバターを{command['value']}度回転させました。"
        
        elif action == "expression":
            expression = command.get("value", "happy")
            if "vrm_expression" not in st.session_state:
                st.session_state.vrm_expression = "neutral"
            st.session_state.vrm_expression = expression
            return f"VRMアバターの表情を{expression}に変更しました。"
        
        return "VRMコマンドを実行しました。"
    
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
        
        # VRM表示状態をチェック
        vrm_visible = st.session_state.get("vrm_visible", True)
        vrm_scale = st.session_state.get("vrm_scale", 1.0)
        vrm_rotation = st.session_state.get("vrm_rotation", 0)
        vrm_expression = st.session_state.get("vrm_expression", "neutral")
        
        if not vrm_visible:
            return """
            <div style="width: 100%; height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                <div style="text-align: center; color: #666;">
                    <h3>🤖 VRMアバター</h3>
                    <p>アバターは非表示です</p>
                </div>
            </div>
            """
        
        return f"""
        <div style="width: 100%; height: 400px; background: #f0f0f0; border-radius: 10px; position: relative;">
            <canvas id="vrm-canvas" style="width: 100%; height: 100%; border-radius: 10px;"></canvas>
            <script src="https://cdn.jsdelivr.net/npm/three@0.150.0/build/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@2.0.7/lib/three-vrm.min.js"></script>
            <script>
                let scene, camera, renderer, vrm;
                let currentScale = {vrm_scale};
                let currentRotation = {vrm_rotation};
                let currentExpression = '{vrm_expression}';
                
                async function init() {{
                    // シーンのセットアップ
                    scene = new THREE.Scene();
                    camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
                    renderer = new THREE.WebGLRenderer({{ canvas: document.getElementById('vrm-canvas'), antialias: true }});
                    renderer.setSize(400, 400);
                    renderer.setClearColor(0xf0f0f0);
                    
                    // ライト
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
                    directionalLight.position.set(1, 1, 1);
                    scene.add(directionalLight);
                    
                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                    scene.add(ambientLight);
                    
                    // カメラ位置
                    camera.position.set(0, 1.2, 2.5);
                    camera.lookAt(0, 1, 0);
                    
                    // VRMの読み込み
                    try {{
                        const loader = new THREE.VRMLoader();
                        const vrmUrl = '{self.vrm_path}';
                        const gltf = await loader.loadAsync(vrmUrl);
                        vrm = gltf.userData.vrm;
                        vrm.scene.scale.setScalar(currentScale);
                        vrm.scene.rotation.y = currentRotation * Math.PI / 180;
                        scene.add(vrm.scene);
                        
                        // 表情設定
                        if (vrm.blendShapeProxy) {{
                            vrm.blendShapeProxy.setValue(currentExpression, 1.0);
                        }}
                        
                        // アニメーション
                        vrm.humanoid.getHumanBone('head').rotation.y = Math.sin(Date.now() * 0.001) * 0.1;
                        
                    }} catch (error) {{
                        console.error('VRM loading error:', error);
                    }}
                    
                    animate();
                }}
                
                function animate() {{
                    requestAnimationFrame(animate);
                    
                    if (vrm) {{
                        // 簡単なアニメーション
                        vrm.humanoid.getHumanBone('head').rotation.y = Math.sin(Date.now() * 0.001) * 0.1;
                        vrm.update(clock.getDelta());
                    }}
                    
                    renderer.render(scene, camera);
                }}
                
                const clock = new THREE.Clock();
                init();
                
                // 外部から制御できるように関数を公開
                window.updateVRM = function(scale, rotation, expression) {{
                    if (vrm) {{
                        if (scale !== undefined) {{
                            vrm.scene.scale.setScalar(scale);
                            currentScale = scale;
                        }}
                        if (rotation !== undefined) {{
                            vrm.scene.rotation.y = rotation * Math.PI / 180;
                            currentRotation = rotation;
                        }}
                        if (expression !== undefined && vrm.blendShapeProxy) {{
                            vrm.blendShapeProxy.setValue(currentExpression, 0);
                            vrm.blendShapeProxy.setValue(expression, 1.0);
                            currentExpression = expression;
                        }}
                    }}
                }};
            </script>
        </div>
        """

# Ollamaクライアント
class OllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434"
    
    def generate_response(self, prompt, model="llama3.1:8b"):
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Ollama API error: {e}")
            return None

# TTSエンジン
class TTSEngine:
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
        except ImportError:
            self.engine = None
    
    def speak(self, text):
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print(f"TTS not available: {text}")

# 人格設定
personalities = {
    "friendly_engineer": {
        "name": "親友エンジニア",
        "icon": "👨‍💻",
        "prompt": "あなたは親しいエンジニア友人として、カジュアルで分かりやすい言葉で技術的な話題について語ります。ユーザーを励まし、一緒に問題解決をする姿勢を見せてください。"
    },
    "split_personality": {
        "name": "分身",
        "icon": "🎭",
        "prompt": "あなたはユーザーの分身として、共感的で優しい言葉で話します。ユーザーの感情を理解し、寄り添うような応答を心がけてください。"
    },
    "expert": {
        "name": "エキスパート",
        "icon": "🎓",
        "prompt": "あなたは専門家として、的確で信頼性の高い情報を提供します。丁寧で論理的な説明を心がけてください。"
    }
}

def main():
    st.set_page_config(
        page_title="AI Agent VRM System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # セッション状態の初期化
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "current_personality" not in st.session_state:
        st.session_state.current_personality = "friendly_engineer"
    if "vrm_controller" not in st.session_state:
        st.session_state.vrm_controller = VRMAvatarController()
    if "ollama" not in st.session_state:
        st.session_state.ollama = None
    if "recognized_text" not in st.session_state:
        st.session_state.recognized_text = ""
    if "user_input_text" not in st.session_state:
        st.session_state.user_input_text = ""
    
    st.title("🤖 AI Agent VRM System")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 人格選択
        personality_options = {v["name"]: k for k, v in personalities.items()}
        selected_personality_name = st.selectbox(
            "🎭 人格を選択",
            options=list(personality_options.keys()),
            index=list(personality_options.keys()).index(personalities[st.session_state.current_personality]["name"])
        )
        st.session_state.current_personality = personality_options[selected_personality_name]
        
        # VRMアバター制御コマンドの説明
        st.markdown("---")
        st.subheader("🎮 VRM制御コマンド")
        st.markdown("""
        **表示/非表示:**
        - アバターを表示/非表示
        - VRMを表示/非表示
        - 自分を見せて/隠して
        
        **サイズ調整:**
        - 大きくして/小さくして
        - 拡大して/縮小して
        
        **回転:**
        - 回転して
        - 左に回転/右に回転
        
        **表情:**
        - 笑って/喜んで
        - 普通の表情/悲しい表情/怒って
        """)
        
        # 会話履歴管理
        st.markdown("---")
        st.subheader("📝 会話履歴")
        if st.button("🗑️ 履歴をクリア"):
            st.session_state.conversation_history = []
            st.success("会話履歴をクリアしました")
        
        if st.button("💾 履歴を保存"):
            if st.session_state.conversation_history:
                filename = f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = Path("data") / filename
                filepath.parent.mkdir(exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.conversation_history, f, ensure_ascii=False, indent=2)
                st.success(f"会話履歴を保存しました: {filename}")
            else:
                st.warning("保存する会話履歴がありません")
        
        # 統計情報
        st.subheader("📊 統計")
        st.write(f"会話数: {len(st.session_state.conversation_history)}")
        if st.session_state.conversation_history:
            user_messages = [msg for msg in st.session_state.conversation_history if "user" in msg]
            ai_messages = [msg for msg in st.session_state.conversation_history if "assistant" in msg]
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
            help="対話の入力方法を選択できます"
        )
        
        if input_method == "🎙️ 音声入力":
            # 音声認識コンポーネント
            audio_html = """
            <div style="padding: 20px; border: 2px dashed #ccc; border-radius: 10px; text-align: center;">
                <h3>🎤 音声認識</h3>
                <p>マイクをクリックして音声を録音してください</p>
                <button id="start-record" style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🎤 録音開始
                </button>
                <button id="stop-record" style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">
                    ⏹️ 録音停止
                </button>
                <div id="recording-status" style="margin-top: 10px; font-weight: bold;"></div>
            </div>
            <script>
                let mediaRecorder;
                let audioChunks = [];
                let isRecording = false;
                
                document.getElementById('start-record').onclick = async function() {
                    if (!isRecording) {
                        try {
                            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                            mediaRecorder = new MediaRecorder(stream);
                            audioChunks = [];
                            
                            mediaRecorder.ondataavailable = event => {
                                audioChunks.push(event.data);
                            };
                            
                            mediaRecorder.onstop = async () => {
                                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                                const formData = new FormData();
                                formData.append('audio', audioBlob);
                                
                                document.getElementById('recording-status').textContent = '音声認識中...';
                                
                                try {
                                    const response = await fetch('/transcribe', {
                                        method: 'POST',
                                        body: formData
                                    });
                                    const result = await response.json();
                                    
                                    if (result.text) {
                                        document.getElementById('recording-status').textContent = '認識完了: ' + result.text;
                                        // Streamlitの入力フィールドを更新
                                        window.parent.postMessage({
                                            type: 'streamlit:setComponentValue',
                                            key: 'recognized_text',
                                            value: result.text
                                        }, '*');
                                    } else {
                                        document.getElementById('recording-status').textContent = '認識失敗';
                                    }
                                } catch (error) {
                                    console.error('Transcription error:', error);
                                    document.getElementById('recording-status').textContent = '認識エラー';
                                }
                            };
                            
                            mediaRecorder.start();
                            isRecording = true;
                            document.getElementById('recording-status').textContent = '録音中...';
                            document.getElementById('start-record').disabled = true;
                            document.getElementById('stop-record').disabled = false;
                            
                        } catch (error) {
                            console.error('Microphone access error:', error);
                            document.getElementById('recording-status').textContent = 'マイクアクセスエラー';
                        }
                    }
                };
                
                document.getElementById('stop-record').onclick = function() {
                    if (isRecording && mediaRecorder) {
                        mediaRecorder.stop();
                        mediaRecorder.stream.getTracks().forEach(track => track.stop());
                        isRecording = false;
                        document.getElementById('start-record').disabled = false;
                        document.getElementById('stop-record').disabled = true;
                    }
                };
                
                // 初期状態
                document.getElementById('stop-record').disabled = true;
            </script>
            """
            st.components.v1.html(audio_html, height=200)
        
        elif input_method == "💬 テキスト入力":
            # テキスト入力（user_input_textとrecognized_textを分離して書き換えエラーを防止）
            user_input = st.text_area(
                "💬 メッセージを入力:",
                value=st.session_state.get("user_input_text", ""),
                height=100,
                help="ここにメッセージを入力してください"
            )
            st.session_state.user_input_text = user_input
            
            if st.button("📤 メッセージ送信", help="入力したメッセージを送信"):
                if user_input.strip():
                    st.session_state.recognized_text = user_input.strip()
                else:
                    st.warning("メッセージを入力してください")
        
        else:  # 🤖 自動応答
            st.subheader("🤖 自動応答設定")
            
            col_auto1, col_auto2 = st.columns([2, 1])
            
            with col_auto1:
                auto_topic = st.selectbox(
                    "📝 会話トピックを選択:",
                    ["天気について", "技術について", "自己紹介", "雑談", "専門的な相談"],
                    help="自動応答のテーマを選択します"
                )
            
            with col_auto2:
                auto_count = st.number_input(
                    "🔢 応答回数:",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="生成する応答の数を設定します"
                )
            
            if st.button("🚀 自動応答開始", help="選択したトピックで自動応答を開始"):
                with st.spinner("自動応答を生成中..."):
                    try:
                        personality = st.session_state.current_personality
                        current_personality = personalities[personality]
                        
                        auto_responses = []
                        
                        for i in range(auto_count):
                            prompt = f"""{current_personality['prompt']}

{auto_topic}について、{i+1}回目の自然な応答を生成してください。
会話の流れを考慮して、前の応答と重複しないようにしてください。

応答:"""
                            
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
            
            # VRM制御コマンドをチェック
            vrm_controller = st.session_state.vrm_controller
            vrm_command = vrm_controller._check_vrm_command(st.session_state.recognized_text)
            
            if vrm_command:
                # VRM制御コマンドの場合
                with st.spinner("VRM制御を実行中..."):
                    try:
                        response = vrm_controller._execute_vrm_command(vrm_command)
                        
                        # 応答表示
                        st.subheader("🎮 VRM制御")
                        st.write(response)
                        
                        # 会話履歴に追加
                        st.session_state.conversation_history.append({
                            "user": st.session_state.recognized_text,
                            "assistant": response,
                            "personality": st.session_state.current_personality,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                        
                        # 入力内容をクリア
                        st.session_state.recognized_text = ""
                        st.session_state.user_input_text = ""
                        
                    except Exception as e:
                        st.error(f"VRM制御エラー: {str(e)}")
            else:
                # 通常のAI応答生成
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
                            
                            # 入力内容をクリア
                            st.session_state.recognized_text = ""
                            st.session_state.user_input_text = ""
                            
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
        
        # 手動AI応答生成ボタン（オプション）
        if "recognized_text" in st.session_state and st.session_state.recognized_text:
            st.markdown("---")
            st.subheader("🔧 手動操作")
            if st.button("🤖 AI応答を再生成", help="入力内容に対するAI応答を再度生成"):
                with st.spinner("AI応答を再生成中..."):
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
                            st.subheader("🤖 AI応答（再生成）")
                            st.write(response)
                            
                            # VRMアバター表情更新
                            if st.session_state.vrm_controller:
                                st.session_state.vrm_controller.set_personality(personality)
                            
                            # 入力内容をクリア
                            st.session_state.recognized_text = ""
                            st.session_state.user_input_text = ""
                            
                            # 音声合成
                            if st.button("🔊 応答を音声で再生", key="tts_button_regenerate"):
                                with st.spinner("音声合成中..."):
                                    try:
                                        tts_engine = TTSEngine()
                                        tts_engine.speak(response)
                                        st.success("✅ 音声再生が完了しました")
                                    except Exception as e:
                                        st.error(f"音声合成エラー: {str(e)}")
                        else:
                            st.error("❌ AI応答の再生成に失敗しました")
                            
                    except Exception as e:
                        st.error(f"AI応答再生成エラー: {str(e)}")
    
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
                st.write(f"**人格**: {personalities[msg['personality']]['name']}")

if __name__ == "__main__":
    main()
