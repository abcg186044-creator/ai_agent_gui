# PulseAudio over TCP 設定ガイド

## 即効性のある解決策：PulseAudio over TCP

### Windowsホスト側の設定

#### 1. PulseAudio for Windowsのインストール
```bash
# Chocolateyを使用してインストール
choco install pulseaudio

# または手動ダウンロード
# https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/
```

#### 2. PulseAudioサーバーの起動
```bash
# TCPモードでPulseAudioサーバーを起動
pulseaudio.exe --load=module-native-protocol-tcp --exit-idle-time=-1 --log-level=debug

# バックグラウンドで実行
start /b pulseaudio.exe --load=module-native-protocol-tcp --exit-idle-time=-1
```

#### 3. ファイアウォール設定
```cmd
# Windowsファイアウォールでポート4713を許可
netsh advfirewall firewall add rule name="PulseAudio TCP" dir=in action=allow protocol=TCP localport=4713
```

### Dockerコンテナ側の設定

#### 1. Dockerfileの更新
```dockerfile
FROM python:3.10-slim

# PulseAudioクライアントのインストール
RUN apt-get update && apt-get install -y \
    pulseaudio-utils \
    libpulse-dev \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 環境変数の設定
ENV PULSE_SERVER=tcp://host.docker.internal:4713
ENV PULSE_RUNTIME_PATH=/tmp/pulse
ENV SDL_AUDIODRIVER=pulse

# 音声ライブラリのインストール
RUN pip install sounddevice==0.4.6
```

#### 2. Dockerコンテナの実行
```bash
docker run -d \
  --name audio-test \
  -p 8501:8501 \
  -e PULSE_SERVER=tcp://host.docker.internal:4713 \
  -e PULSE_RUNTIME_PATH=/tmp/pulse \
  --add-host=host.docker.internal:host-gateway \
  audio-app
```

### 動作確認
```python
import sounddevice as sd

# デバイスの確認
devices = sd.query_devices()
print(f"検出されたデバイス数: {len(devices)}")

# デフォルトデバイスの確認
default_input = sd.default.device[0]
print(f"デフォルト入力デバイス: {default_input}")

# 録音テスト
duration = 3
sample_rate = 16000
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()
print(f"録音完了: {len(recording)} サンプル")
```

---

## 2. 堅牢性（2026年標準）：Streamlitカスタムコンポーネント

### ブラウザベースの音声入力実装

#### 1. カスタムコンポーネントの作成
```python
# audio_recorder_component.py
import streamlit.components.v1 as components
import streamlit as st
import base64
import io
import wave

def audio_recorder(key="audio_recorder"):
    """ブラウザベースの音声録音コンポーネント"""
    
    html_code = """
    <div id="audio-recorder">
        <button id="start-record" onclick="startRecording()">🎙️ 録音開始</button>
        <button id="stop-record" onclick="stopRecording()" disabled>⏹️ 録音停止</button>
        <audio id="audio-player" controls style="display:none;"></audio>
        <div id="status">準備完了</div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audioPlayer = document.getElementById('audio-player');
                    audioPlayer.src = audioUrl;
                    audioPlayer.style.display = 'block';
                    
                    // Streamlitにデータを送信
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            key: '""" + key + """',
                            value: base64Audio
                        }, '*');
                    };
                    reader.readAsDataURL(audioBlob);
                };

                mediaRecorder.start();
                isRecording = true;
                document.getElementById('start-record').disabled = true;
                document.getElementById('stop-record').disabled = false;
                document.getElementById('status').textContent = '録音中...';
            } catch (err) {
                console.error('Error accessing microphone:', err);
                document.getElementById('status').textContent = 'エラー: ' + err.message;
            }
        }

        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                document.getElementById('start-record').disabled = false;
                document.getElementById('stop-record').disabled = true;
                document.getElementById('status').textContent = '録音完了';
            }
        }
    </script>

    <style>
        #audio-recorder {
            padding: 20px;
            border: 2px solid #ddd;
            border-radius: 10px;
            text-align: center;
            background-color: #f9f9f9;
        }
        
        button {
            margin: 5px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        
        #start-record {
            background-color: #4CAF50;
            color: white;
        }
        
        #stop-record {
            background-color: #f44336;
            color: white;
        }
        
        #status {
            margin-top: 10px;
            font-weight: bold;
        }
        
        #audio-player {
            margin-top: 10px;
            width: 100%;
        }
    </style>
    """
    
    # コンポーネントのレンダリング
    components.html(html_code, height=200)
    
    # 音声データの受信
    audio_data = st.session_state.get(key, None)
    
    if audio_data:
        # Base64デコード
        audio_bytes = base64.b64decode(audio_data)
        
        # WAVファイルとして保存
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            frames = wav_file.readframes(-1)
            audio_array = np.frombuffer(frames, dtype=np.int16)
            
            # float32に変換
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            return audio_float, sample_rate
    
    return None, None
```

#### 2. Streamlitアプリケーションの更新
```python
# browser_audio_app.py
import streamlit as st
import numpy as np
from audio_recorder_component import audio_recorder
from faster_whisper import WhisperModel

def main():
    st.title("🎤 ブラウザ音声入力アプリ")
    
    # 音声録音コンポーネント
    st.markdown("### 🎙️ 音声録音")
    audio_data, sample_rate = audio_recorder(key="browser_audio")
    
    if audio_data is not None:
        st.success("✅ 音声データを受信しました！")
        
        # 波形表示
        st.write("📈 録音波形:")
        st.line_chart(audio_data[:1000])
        
        # 音声認識
        if st.button("🤖 音声認識"):
            with st.spinner("音声認識中..."):
                try:
                    # WAVファイルとして保存
                    import tempfile
                    import wave
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        with wave.open(temp_file.name, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(sample_rate)
                            wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                        
                        # Whisperで認識
                        model = WhisperModel("base", compute_type="float32")
                        segments, info = model.transcribe(temp_file.name, language="ja")
                        
                        transcription = ""
                        for segment in segments:
                            transcription += segment.text + " "
                        
                        st.success("✅ 音声認識完了！")
                        st.write(f"認識結果: {transcription.strip()}")
                        
                except Exception as e:
                    st.error(f"❌ 音声認識エラー: {str(e)}")

if __name__ == "__main__":
    main()
```

---

## Windsurfへの指示

### 最短ルートでの実装指示

```
音声入力デバイスの取得をsounddeviceから、ブラウザ経由のストリーミングまたはバイナリ送信に変更してください。

具体的な要件：
1. WebRTC/MediaRecorder APIを使用してブラウザから音声を取得
2. 取得した音声データをBase64エンコードしてサーバーに送信
3. サーバー側でデコードしてWAVファイルに変換
4. faster-whisperで音声認識を実行
5. Streamlitカスタムコンポーネントとして実装

実装の優先順位：
1. 即効性：PulseAudio over TCPの設定
2. 堅牢性：ブラウザベースの音声入力コンポーネント
```

---

## 実装計画

### フェーズ1：即効性（1-2日）
- [ ] PulseAudio for Windowsのインストール
- [ ] TCPサーバーの設定
- [ ] Dockerコンテナの環境変数設定
- [ ] sounddeviceでの動作確認

### フェーズ2：堅牢性（3-5日）
- [ ] Streamlitカスタムコンポーネントの作成
- [ ] WebRTC/MediaRecorder APIの実装
- [ ] 音声データの送受信処理
- [ ] faster-whisperとの連携

### フェーズ3：最適化（1週間）
- [ ] エラーハンドリングの改善
- [ ] UI/UXの最適化
- [ ] パフォーマンスの改善
- [ ] クロスブラウザ対応

---

## 期待される効果

### 即効性のある解決策
- ✅ 現在のsounddeviceベースのコードを維持
- ✅ 最小限の変更で音声入力を実現
- ✅ 開発環境での迅速なテスト

### 堅牢性のある解決策
- ✅ ブラウザ標準APIを使用
- ✅ Docker環境に依存しない
- ✅ クロスプラットフォーム対応
- ✅ セキュリティ面での優位性
