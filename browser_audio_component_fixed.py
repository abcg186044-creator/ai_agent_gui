import streamlit.components.v1 as components
import base64
import io
import wave
import numpy as np

def audio_recorder_component(key="audio_recorder"):
    html = """
    <div id="audio-recorder">
        <button id="start-record" onclick="startRecording()">🎙️ 録音開始</button>
        <button id="stop-record" onclick="stopRecording()" disabled>⏹️ 録音停止</button>
        <button id="test-mic" onclick="testMicrophone()">🔧 マイクテスト</button>
        <audio id="audio-player" controls style="display:none;"></audio>
        <div id="status">準備完了</div>
    </div>
    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        
        // コンソール警告を完全にフィルタリング
        const originalConsoleWarn = console.warn;
        const originalConsoleError = console.error;
        const originalConsoleLog = console.log;
        
        // すべてのコンソール出力をフィルタリング
        function filterConsole(originalFn, ...args) {
            const message = args.join(' ');
            const filterKeywords = [
                'Unrecognized feature',
                'iframe which has both',
                'was preloaded using link preload',
                'SourceSansPro',
                'SourceSerifPro',
                'ambient-light-sensor',
                'battery',
                'document-domain',
                'layout-animations',
                'legacy-image-formats',
                'oversized-images',
                'vr',
                'wake-lock'
            ];
            
            if (filterKeywords.some(keyword => message.includes(keyword))) {
                return; // 警告を無視
            }
            return originalFn.apply(console, args);
        }
        
        console.warn = function(...args) { return filterConsole(originalConsoleWarn, ...args); };
        console.error = function(...args) { return filterConsole(originalConsoleError, ...args); };
        console.log = function(...args) { return filterConsole(originalConsoleLog, ...args); };
        
        // Streamlitとの通信を安全に設定
        window.addEventListener('message', function(event) {
            // 必要に応じてメッセージ処理
        });
        
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                
                // マイク入力確認
                const audioContext = new AudioContext();
                const source = audioContext.createMediaStreamSource(stream);
                const analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                source.connect(analyser);
                
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                // 音量レベルを監視
                function checkAudioLevel() {
                    if (!isRecording) return;
                    
                    analyser.getByteFrequencyData(dataArray);
                    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
                    
                    // 音量レベルを表示
                    const volumeLevel = Math.round(average);
                    document.getElementById('status').textContent = `録音中... 音量レベル: ${volumeLevel}/255`;
                    
                    if (isRecording) {
                        requestAnimationFrame(checkAudioLevel);
                    }
                }
                
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        // Streamlitに安全にデータを送信
                        if (window.parent && window.parent.postMessage) {
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                key: """ + key + """",
                                value: base64Audio
                            }, '*');
                        }
                    };
                    reader.readAsDataURL(audioBlob);
                    
                    // リソースをクリーンアップ
                    source.disconnect();
                    audioContext.close();
                };
                
                mediaRecorder.start(100); // 100msごとにデータ収集
                isRecording = true;
                document.getElementById('start-record').disabled = true;
                document.getElementById('stop-record').disabled = false;
                document.getElementById('status').textContent = '録音中... 音量レベルを確認中...';
                
                // 音量レベル監視を開始
                setTimeout(() => {
                    if (isRecording) {
                        checkAudioLevel();
                    }
                }, 500);
                
            } catch (err) {
                console.error('Error accessing microphone:', err);
                document.getElementById('status').textContent = 'エラー: ' + err.message;
            }
        }
        
        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                document.getElementById('start-record').disabled = false;
                document.getElementById('stop-record').disabled = true;
                document.getElementById('status').textContent = '録音完了！';
            }
        }
        
        // マイクテスト機能
        async function testMicrophone() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                
                const audioContext = new AudioContext();
                const source = audioContext.createMediaStreamSource(stream);
                const analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                source.connect(analyser);
                
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                // 3秒間テスト
                let testCount = 0;
                const maxTests = 30; // 3秒 x 10回/秒
                
                function testAudioLevel() {
                    if (testCount >= maxTests) {
                        source.disconnect();
                        audioContext.close();
                        stream.getTracks().forEach(track => track.stop());
                        document.getElementById('status').textContent = 'マイクテスト完了！正常に動作しています。';
                        return;
                    }
                    
                    analyser.getByteFrequencyData(dataArray);
                    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
                    const volumeLevel = Math.round(average);
                    
                    document.getElementById('status').textContent = `マイクテスト中... 音量レベル: ${volumeLevel}/255 (${testCount}/${maxTests})`;
                    
                    testCount++;
                    setTimeout(testAudioLevel, 100);
                }
                
                document.getElementById('status').textContent = 'マイクテスト開始...';
                testAudioLevel();
                
            } catch (err) {
                console.error('Error testing microphone:', err);
                document.getElementById('status').textContent = 'マイクテストエラー: ' + err.message;
            }
        }
        
        // ページアンロード時にクリーンアップ
        window.addEventListener('beforeunload', () => {
            if (isRecording) {
                stopRecording();
            }
        });
    </script>
    
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        #audio-recorder { 
            text-align: center; 
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 100%;
            box-sizing: border-box;
        }
        button { 
            padding: 15px 30px;
            margin: 8px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            min-height: 50px;
            width: 100%;
            max-width: 200px;
        }
        #start-record { 
            background-color: #4CAF50; 
            color: white; 
        }
        #start-record:hover {
            background-color: #45a049;
            transform: translateY(-1px);
        }
        #stop-record { 
            background-color: #f44336; 
            color: white; 
        }
        #stop-record:hover {
            background-color: #da190b;
            transform: translateY(-1px);
        }
        #test-mic { 
            background-color: #2196F3; 
            color: white; 
        }
        #test-mic:hover {
            background-color: #1976D2;
            transform: translateY(-1px);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        #status { 
            margin-top: 15px; 
            font-weight: bold; 
            color: #333;
            font-size: 16px;
            padding: 10px;
            border-radius: 6px;
            background-color: #e9ecef;
        }
        #audio-player {
            margin-top: 15px;
            width: 100%;
            max-width: 300px;
        }
        
        /* モバイル対応 */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            #audio-recorder {
                padding: 15px;
            }
            button {
                font-size: 18px;
                padding: 18px 20px;
                min-height: 60px;
                margin: 10px 5px;
            }
            #status {
                font-size: 18px;
                padding: 15px;
            }
        }
        
        /* タッチデバイス対応 */
        @media (hover: none) and (pointer: coarse) {
            button {
                padding: 20px 25px;
                font-size: 18px;
                min-height: 65px;
            }
        }
    </style>
    """
    
    # HTMLコンポーネントを埋め込み
    component = components.html(html, height=400, width=400)
    
    # Streamlitからのデータ受信
    audio_data = None
    sample_rate = 16000
    
    if component:
        try:
            # componentが文字列の場合のみbase64デコード
            if isinstance(component, str) and component:
                audio_bytes = base64.b64decode(component)
                
                # WebM形式をWAVに変換
                import tempfile
                import subprocess
                
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
                    webm_file.write(audio_bytes)
                    webm_path = webm_file.name
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
                    wav_path = wav_file.name
                
                # FFmpegを使用してWebMをWAVに変換
                try:
                    subprocess.run([
                        'ffmpeg', '-i', webm_path, '-ar', '16000', '-ac', '1', wav_path, '-y'
                    ], check=True, capture_output=True)
                    
                    with wave.open(wav_path, 'rb') as wav_file:
                        sample_rate = wav_file.getframerate()
                        frames = wav_file.readframes(-1)
                        audio_array = np.frombuffer(frames, dtype=np.int16)
                        audio_float = audio_array.astype(np.float32) / 32768.0
                        
                        return audio_float, sample_rate
                        
                except subprocess.CalledProcessError as e:
                    # FFmpegが利用できない場合のフォールバック
                    import streamlit as st
                    st.warning("FFmpegが利用できないため、音声変換をスキップします")
                    return None, None
                    
                finally:
                    # 一時ファイルを削除
                    import os
                    try:
                        os.unlink(webm_path)
                        os.unlink(wav_path)
                    except:
                        pass
            else:
                # componentが空または文字列でない場合
                return None, None
                    
        except Exception as e:
            import streamlit as st
            st.error(f"音声データ処理エラー: {str(e)}")
            return None, None
    
    return None, None
