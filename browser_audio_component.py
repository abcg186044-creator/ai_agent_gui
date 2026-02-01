import streamlit.components.v1 as components
import streamlit as st
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
    
    if audio_data:
        try:
            audio_bytes = base64.b64decode(audio_data)
            
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
                    
        except Exception as e:
            st.error(f"音声データ処理エラー: {str(e)}")
            return None, None
    
    return None, None
