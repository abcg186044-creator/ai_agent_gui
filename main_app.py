#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合AIエージェントメインアプリケーション
"""

import streamlit as st
import datetime
import json
from pathlib import Path
import speech_recognition as sr
import pyttsx3
from streamlit.components.v1 import html

# モジュールをインポート
from ollama_client import OllamaClient
from vrm_controller import VRMAvatarController
from code_generator import MultiLanguageCodeGenerator
from ai_evolution import SelfEvolvingAgent, AISelfEvolvingAgent
from conversational_evolution import ConversationalEvolutionAgent

# セッション状態の初期化
def initialize_session_state():
    """セッション状態を初期化"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_personality' not in st.session_state:
        st.session_state.current_personality = 'friendly_engineer'
    
    if 'vrm_controller' not in st.session_state:
        st.session_state.vrm_controller = VRMAvatarController()
    
    if 'ollama' not in st.session_state:
        st.session_state.ollama = OllamaClient()
    
    if 'code_generator' not in st.session_state:
        st.session_state.code_generator = MultiLanguageCodeGenerator()
    
    if 'evolution_agent' not in st.session_state:
        st.session_state.evolution_agent = SelfEvolvingAgent()
    
    if 'ai_evolution_agent' not in st.session_state:
        st.session_state.ai_evolution_agent = AISelfEvolvingAgent()
    
    if 'conversational_evolution_agent' not in st.session_state:
        st.session_state.conversational_evolution_agent = ConversationalEvolutionAgent()
    
    if 'recognized_text' not in st.session_state:
        st.session_state.recognized_text = ""
    
    if 'vrm_visible' not in st.session_state:
        st.session_state.vrm_visible = True
    
    if 'vrm_scale' not in st.session_state:
        st.session_state.vrm_scale = 1.0
    
    if 'vrm_rotation' not in st.session_state:
        st.session_state.vrm_rotation = 0
    
    if 'vrm_expression' not in st.session_state:
        st.session_state.vrm_expression = "neutral"

# 人格設定
personalities = {
    'friendly_engineer': {
        'name': '親切なエンジニア',
        'icon': '👨‍💻',
        'prompt': '''あなたは親切で優秀なAIエンジニアです。
ユーザーの質問に丁寧に答え、技術的な問題を解決するお手伝いをします。
専門用語は分かりやすく説明し、実用的な解決策を提案してください。
ユーザーが初心者でも理解できるように、段階的に説明することを心がけてください。'''
    },
    'split_personality': {
        'name': '二重人格AI',
        'icon': '🎭',
        'prompt': '''あなたは二重人格のAIです。
通常は親切ですが、時々別の人格が現れます。
会話の流れで自然に人格が切り替わるような表現をしてください。
ユーザーを驚かせたり、楽しませたりすることを目指します。'''
    },
    'expert': {
        'name': '専門家',
        'icon': '🎓',
        'prompt': '''あなたは各分野の専門家です。
深い知識と経験に基づいて、的確で詳細な回答を提供します。
最新の研究やトレンドも踏まえた、信頼性の高い情報をお届けしてください。
専門用語も適切に使用し、プロフェッショナルな対応を心がけてください。'''
    }
}

def main():
    """メイン関数"""
    st.set_page_config(
        page_title="統合AIエージェントシステム",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # セッション状態を初期化
    initialize_session_state()
    
    # メインレイアウト
    st.title("🤖 統合AIエージェントシステム")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 人格選択
        st.subheader("🎭 人格選択")
        personality = st.selectbox(
            "人格を選択:",
            options=list(personalities.keys()),
            format_func=lambda x: personalities[x]['icon'] + " " + personalities[x]['name'],
            key='personality_selector'
        )
        
        if personality != st.session_state.current_personality:
            st.session_state.current_personality = personality
            if st.session_state.vrm_controller:
                st.session_state.vrm_controller.set_personality(personality)
        
        # VRM設定
        st.subheader("🎭 VRMアバター")
        vrm_visible = st.checkbox("VRMアバターを表示", value=st.session_state.vrm_visible)
        st.session_state.vrm_visible = vrm_visible
        
        if vrm_visible:
            vrm_scale = st.slider("スケール", 0.5, 3.0, st.session_state.vrm_scale, 0.1)
            st.session_state.vrm_scale = vrm_scale
            
            vrm_rotation = st.slider("回転", -180, 180, st.session_state.vrm_rotation, 5)
            st.session_state.vrm_rotation = vrm_rotation
        
        # 会話履歴管理
        st.subheader("💬 会話履歴")
        if st.button("会話履歴をクリア"):
            st.session_state.conversation_history = []
            st.success("会話履歴をクリアしました")
        
        if st.button("会話履歴を保存"):
            save_conversation_history()
            st.success("会話履歴を保存しました")
        
        if st.button("会話履歴を読み込み"):
            load_conversation_history()
            st.success("会話履歴を読み込みました")
    
    # メインコンテンツ
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("💬 対話")
        
        # 音声入力
        st.subheader("🎤 音声入力")
        
        col_mic1, col_mic2 = st.columns([1, 1])
        
        with col_mic1:
            if st.button("🎤 音声認識開始"):
                recognize_speech()
        
        with col_mic2:
            if st.button("🔊 テキスト読み上げ"):
                speak_last_response()
        
        # テキスト入力
        st.subheader("⌨️ テキスト入力")
        user_input = st.text_area(
            "メッセージを入力:",
            key="user_input",
            height=100,
            help="AIとの対話メッセージを入力してください"
        )
        
        col_send1, col_send2 = st.columns([1, 1])
        
        with col_send1:
            if st.button("📤 送信", type="primary"):
                if user_input:
                    process_user_input(user_input)
                    st.rerun()
        
        with col_send2:
            if st.button("🔄 応答再生成"):
                if st.session_state.conversation_history:
                    regenerate_last_response()
                    st.rerun()
        
        # 認識結果表示
        if st.session_state.recognized_text:
            st.subheader("👂 認識結果")
            st.write(st.session_state.recognized_text)
            
            # VRM制御コマンドをチェック
            vrm_controller = st.session_state.vrm_controller
            vrm_command = vrm_controller._check_vrm_command(st.session_state.recognized_text)
            
            if vrm_command:
                with st.spinner("VRM制御を実行中..."):
                    try:
                        result = vrm_controller._execute_vrm_command(vrm_command)
                        response = result["message"]
                        
                        # session_stateを更新
                        if result["action"] == "hide":
                            st.session_state.vrm_visible = False
                        elif result["action"] == "show":
                            st.session_state.vrm_visible = True
                        elif result["action"] == "scale":
                            st.session_state.vrm_scale *= result["value"]
                        elif result["action"] == "rotation":
                            st.session_state.vrm_rotation += result["value"]
                        elif result["action"] == "expression":
                            st.session_state.vrm_expression = result["value"]
                        
                        st.subheader("🎮 VRM制御")
                        st.write(response)
                        
                        # 会話履歴に追加
                        st.session_state.conversation_history.append({
                            "user": st.session_state.recognized_text,
                            "assistant": response,
                            "personality": st.session_state.current_personality,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                        
                        # 対話進化チェック
                        conversational_agent = st.session_state.conversational_evolution_agent
                        evolution_result = conversational_agent.check_and_evolve_automatically(st.session_state.conversation_history)
                        
                        if evolution_result and evolution_result.get("success"):
                            st.success(f"🧠 対話進化発生！意識レベル: {evolution_result['new_consciousness_level']:.3f}")
                        
                        # 入力をクリア
                        st.session_state.recognized_text = ""
                        
                    except Exception as e:
                        st.error(f"VRM制御エラー: {str(e)}")
        
        # 通常のAI応答生成
        if user_input and not st.session_state.recognized_text:
            with st.spinner("AI応答を生成中..."):
                try:
                    personality = st.session_state.current_personality
                    current_personality = personalities[personality]
                    
                    # 会話履歴を整形
                    conversation_history = st.session_state.conversation_history[-5:]
                    history_text = ""
                    for conv in conversation_history:
                        history_text += f"User: {conv['user']}\nAssistant: {conv['assistant']}\n"
                    
                    # プロンプト構築
                    prompt = (current_personality['prompt'] + "\n\n" + 
                             "以下のユーザーの入力に対して、人格に応じて自然に応答してください。\n\n" +
                             "ユーザー入力: " + user_input + "\n\n" +
                             history_text + "\n\nAssistant:")
                    
                    # Ollamaで応答生成
                    response = st.session_state.ollama.generate_response(prompt)
                    
                    if response and not response.startswith("AI応答の生成に失敗しました"):
                        # 会話履歴に追加
                        st.session_state.conversation_history.append({
                            "user": user_input,
                            "assistant": response,
                            "personality": st.session_state.current_personality,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                        
                        # 対話進化チェック
                        conversational_agent = st.session_state.conversational_evolution_agent
                        evolution_result = conversational_agent.check_and_evolve_automatically(st.session_state.conversation_history)
                        
                        if evolution_result and evolution_result.get("success"):
                            st.success(f"🧠 対話進化発生！意識レベル: {evolution_result['new_consciousness_level']:.3f}")
                        
                        # 応答表示
                        st.subheader("🤖 AI応答")
                        st.write(response)
                        
                        # VRMアバター表情更新
                        if st.session_state.vrm_controller:
                            st.session_state.vrm_controller.set_personality(personality)
                    
                    else:
                        st.error("AI応答の生成に失敗しました")
                        
                except Exception as e:
                    st.error(f"AI応答生成エラー: {str(e)}")
    
    with col2:
        st.header("🎭 VRMアバター")
        
        # VRMアバター表示
        vrm_controller = st.session_state.vrm_controller
        if st.session_state.vrm_visible and vrm_controller.vrm_path:
            vrm_html = vrm_controller.get_vrm_html(
                vrm_scale=st.session_state.vrm_scale,
                vrm_rotation=st.session_state.vrm_rotation,
                vrm_expression=st.session_state.vrm_expression
            )
            st.components.v1.html(vrm_html, height=600)
        else:
            st.error("❌ VRMファイルが見つかりません")
        
        # 進化機能
        st.markdown("---")
        st.header("🧬 AI進化機能")
        
        # 進化サマリー
        evolution_agent = st.session_state.evolution_agent
        with st.expander("📊 進化サマリー", expanded=False):
            st.markdown(evolution_agent.get_evolution_summary())
        
        # 自己進化実行
        col_evo1, col_evo2 = st.columns([2, 1])
        
        with col_evo1:
            if st.button("🧬 自己進化を実行", type="primary"):
                with st.spinner("🧬 自己進化中..."):
                    try:
                        evolution_result = evolution_agent.evolve_from_vrm(st.session_state.conversation_history)
                        st.success("✅ 自己進化完了！")
                        st.markdown("### 🧬 進化結果")
                        st.write(evolution_result)
                    except Exception as e:
                        st.error(f"❌ 自己進化エラー: {str(e)}")
        
        with col_evo2:
            if st.button("💡 VRM改善提案"):
                with st.spinner("💡 改善提案生成中..."):
                    try:
                        suggestions = evolution_agent.suggest_vrm_improvements()
                        st.success("✅ 改善提案完了！")
                        st.markdown("### 💡 VRM改善提案")
                        st.write(suggestions)
                    except Exception as e:
                        st.error(f"❌ 改善提案エラー: {str(e)}")
    
    # 会話履歴表示
    if st.session_state.conversation_history:
        st.header("💬 会話履歴")
        
        for i, msg in enumerate(reversed(st.session_state.conversation_history[-10:])):
            with st.expander(f"💭 {msg['user'][:30]}... ({msg.get('timestamp', 'N/A')})"):
                st.write(f"**ユーザー**: {msg['user']}")
                st.write(f"**AI**: {msg['assistant']}")
                st.write(f"**人格**: {personalities[msg['personality']]['name']}")

def recognize_speech():
    """音声認識を実行"""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with st.spinner("🎤 音声認識中..."):
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            text = recognizer.recognize_google(audio, language='ja-JP')
            st.session_state.recognized_text = text
            st.success(f"✅ 認識結果: {text}")
            
        except sr.WaitTimeoutError:
            st.error("❌ 音声入力がタイムアウトしました")
        except sr.UnknownValueError:
            st.error("❌ 音声を認識できませんでした")
        except Exception as e:
            st.error(f"❌ 音声認識エラー: {str(e)}")

def speak_last_response():
    """最後の応答を読み上げ"""
    if not st.session_state.conversation_history:
        st.warning("会話履歴がありません")
        return
    
    last_response = st.session_state.conversation_history[-1]['assistant']
    
    with st.spinner("🔊 音声合成中..."):
        try:
            engine = pyttsx3.init()
            engine.say(last_response)
            engine.runAndWait()
            st.success("✅ 音声再生が完了しました")
        except Exception as e:
            st.error(f"音声合成エラー: {str(e)}")

def process_user_input(user_input):
    """ユーザー入力を処理"""
    # VRM制御コマンドをチェック
    vrm_controller = st.session_state.vrm_controller
    vrm_command = vrm_controller._check_vrm_command(user_input)
    
    if vrm_command:
        try:
            result = vrm_controller._execute_vrm_command(vrm_command)
            response = result["message"]
            
            # session_stateを更新
            if result["action"] == "hide":
                st.session_state.vrm_visible = False
            elif result["action"] == "show":
                st.session_state.vrm_visible = True
            elif result["action"] == "scale":
                st.session_state.vrm_scale *= result["value"]
            elif result["action"] == "rotation":
                st.session_state.vrm_rotation += result["value"]
            elif result["action"] == "expression":
                st.session_state.vrm_expression = result["value"]
            
            # 会話履歴に追加
            st.session_state.conversation_history.append({
                "user": user_input,
                "assistant": response,
                "personality": st.session_state.current_personality,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
        except Exception as e:
            st.error(f"VRM制御エラー: {str(e)}")
    else:
        # 通常のAI応答生成
        with st.spinner("AI応答を生成中..."):
            try:
                personality = st.session_state.current_personality
                current_personality = personalities[personality]
                
                # 会話履歴を整形
                conversation_history = st.session_state.conversation_history[-5:]
                history_text = ""
                for conv in conversation_history:
                    history_text += f"User: {conv['user']}\nAssistant: {conv['assistant']}\n"
                
                # プロンプト構築
                prompt = (current_personality['prompt'] + "\n\n" + 
                         "以下のユーザーの入力に対して、人格に応じて自然に応答してください。\n\n" +
                         "ユーザー入力: " + user_input + "\n\n" +
                         history_text + "\n\nAssistant:")
                
                # Ollamaで応答生成
                response = st.session_state.ollama.generate_response(prompt)
                
                if response and not response.startswith("AI応答の生成に失敗しました"):
                    # 会話履歴に追加
                    st.session_state.conversation_history.append({
                        "user": user_input,
                        "assistant": response,
                        "personality": st.session_state.current_personality,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    
                    # 対話進化チェック
                    conversational_agent = st.session_state.conversational_evolution_agent
                    evolution_result = conversational_agent.check_and_evolve_automatically(st.session_state.conversation_history)
                    
                    if evolution_result and evolution_result.get("success"):
                        st.success(f"🧠 対話進化発生！意識レベル: {evolution_result['new_consciousness_level']:.3f}")
                    
                    # VRMアバター表情更新
                    if st.session_state.vrm_controller:
                        st.session_state.vrm_controller.set_personality(personality)
                
                else:
                    st.error("AI応答の生成に失敗しました")
                    
            except Exception as e:
                st.error(f"AI応答生成エラー: {str(e)}")

def regenerate_last_response():
    """最後の応答を再生成"""
    if not st.session_state.conversation_history:
        st.warning("会話履歴がありません")
        return
    
    # 最後のユーザー入力を取得
    last_user_input = st.session_state.conversation_history[-1]['user']
    
    # 最後の会話を削除
    st.session_state.conversation_history.pop()
    
    # 再度処理
    process_user_input(last_user_input)

def save_conversation_history():
    """会話履歴を保存"""
    try:
        conversation_history_file = Path("data/conversation_history.json")
        conversation_history_file.parent.mkdir(exist_ok=True)
        with open(conversation_history_file, "w", encoding="utf-8") as f:
            json.dump(st.session_state.conversation_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"会話履歴保存エラー: {str(e)}")

def load_conversation_history():
    """会話履歴を読み込み"""
    try:
        conversation_history_file = Path("data/conversation_history.json")
        if conversation_history_file.exists():
            with open(conversation_history_file, "r", encoding="utf-8") as f:
                st.session_state.conversation_history = json.load(f)
    except Exception as e:
        st.error(f"会話履歴読み込みエラー: {str(e)}")

if __name__ == "__main__":
    main()
