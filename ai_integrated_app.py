import streamlit as st
import numpy as np
import tempfile
import json
import requests
import time
from browser_audio_component import audio_recorder_component
from datetime import datetime

# OpenAI API設定
OPENAI_API_KEY = "your-openai-api-key-here"  # 実際のAPIキーに置き換えてください

def ai_response_generator(user_input, conversation_history):
    """AI応答を生成"""
    try:
        # 会話履歴をフォーマット
        messages = [
            {"role": "system", "content": "あなたは親切で知的なAIアシスタントです。日本語で自然な会話をしてください。"},
        ]
        
        # 会話履歴を追加
        for msg in conversation_history[-5:]:  # 直近5件の履歴を使用
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_input})
        
        # OpenAI API呼び出し
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return ai_response
        else:
            return f"AI応答エラー: {response.status_code}"
            
    except Exception as e:
        return f"AI応答エラー: {str(e)}"

def save_conversation(conversation_history):
    """会話履歴を保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=2)
    
    return filename

def main():
    st.title("🤖 AI音声対話システム")
    
    # セッション状態の初期化
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    
    # サイドバー：設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # OpenAI APIキー設定
        api_key = st.text_input("OpenAI APIキー", type="password", value=OPENAI_API_KEY)
        if api_key != OPENAI_API_KEY:
            st.session_state.openai_api_key = api_key
        else:
            st.session_state.openai_api_key = OPENAI_API_KEY
        
        # 会話履歴管理
        st.subheader("💬 会話履歴")
        if st.button("🗑️ 履歴をクリア"):
            st.session_state.conversation_history = []
            st.rerun()
        
        if st.button("💾 履歴を保存"):
            if st.session_state.conversation_history:
                filename = save_conversation(st.session_state.conversation_history)
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
        
        # 音声録音コンポーネント
        audio_data, sample_rate = audio_recorder_component(key="ai_audio")
        
        if audio_data is not None and not st.session_state.is_processing:
            st.success("✅ 音声データを受信しました！")
            
            # 音声認識ボタン
            if st.button("🤖 音声認識とAI応答", type="primary"):
                with st.spinner("音声認識とAI応答を生成中..."):
                    st.session_state.is_processing = True
                    
                    try:
                        # 音声認識
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
                            
                            user_text = transcription.strip()
                            
                            if user_text:
                                st.success(f"✅ 音声認識完了: {user_text}")
                                
                                # AI応答生成
                                ai_response = ai_response_generator(
                                    user_text, 
                                    st.session_state.conversation_history
                                )
                                
                                st.info(f"🤖 AI応答: {ai_response}")
                                
                                # 会話履歴に追加
                                st.session_state.conversation_history.append({
                                    "role": "user",
                                    "content": user_text,
                                    "timestamp": datetime.now().isoformat()
                                })
                                st.session_state.conversation_history.append({
                                    "role": "assistant", 
                                    "content": ai_response,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                # TTSでAI応答を音声化（オプション）
                                if st.button("🔊 AI応答を音声で再生"):
                                    try:
                                        import pyttsx3
                                        engine = pyttsx3.init()
                                        engine.save_to_file(ai_response, "ai_response.mp3")
                                        engine.runAndWait()
                                        st.audio("ai_response.mp3")
                                    except Exception as e:
                                        st.warning(f"音声再生エラー: {str(e)}")
                            else:
                                st.warning("音声認識結果が空です")
                                
                    except Exception as e:
                        st.error(f"処理エラー: {str(e)}")
                    finally:
                        st.session_state.is_processing = False
                        st.rerun()
    
    with col2:
        st.header("💬 会話履歴")
        
        # 会話履歴の表示
        if st.session_state.conversation_history:
            for i, msg in enumerate(reversed(st.session_state.conversation_history[-10:])):
                if msg["role"] == "user":
                    st.markdown(f"👤 **あなた**: {msg['content']}")
                else:
                    st.markdown(f"🤖 **AI**: {msg['content']}")
                st.divider()
        else:
            st.info("会話履歴がありません。音声入力で会話を始めてください。")
    
    # フッター情報
    st.markdown("---")
    st.markdown("### 📋 使い方")
    st.markdown("""
    1. **🔧 マイクテスト**: マイクが正常に動作するか確認
    2. **🎙️ 録音開始**: 音声を録音
    3. **🤖 音声認識とAI応答**: 音声をテキスト変換し、AI応答を生成
    4. **💬 会話**: 自動的に会話履歴に保存
    5. **💾 保存**: 会話履歴をJSONファイルで保存
    """)
    
    # 技術情報
    with st.expander("🔧 技術情報"):
        st.markdown("""
        **使用技術:**
        - WebRTC/MediaRecorder API (音声録音)
        - faster-whisper (音声認識)
        - OpenAI GPT-3.5-turbo (AI応答)
        - pyttsx3 (音声合成)
        - Streamlit (UIフレームワーク)
        
        **特徴:**
        - ブラウザベースの音声入力
        - リアルタイム音量確認
        - 高精度日本語音声認識
        - 自然なAI対話
        - 会話履歴の保存
        """)

if __name__ == "__main__":
    main()
