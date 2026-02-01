import streamlit as st
import numpy as np
import tempfile
from browser_audio_component import audio_recorder_component

def main():
    st.title("🎤 ブラウザ音声入力アプリ")
    
    # 音声録音コンポーネント
    st.markdown("### 🎙️ 音声録音")
    audio_data, sample_rate = audio_recorder_component(key="browser_audio")
    
    if audio_data is not None:
        st.success("✅ 音声データを受信しました！")
        st.line_chart(audio_data[:1000])
        
        # 音声認識
        if st.button("🤖 音声認識"):
            with st.spinner("音声認識中..."):
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
                        
                        st.success("✅ 音声認識完了！")
                        st.write(f"認識結果: {transcription.strip()}")
                        
                except Exception as e:
                    st.error(f"❌ 音声認識エラー: {str(e)}")

if __name__ == "__main__":
    main()
