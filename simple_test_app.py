#!/usr/bin/env python3
"""
Simple Test App - 基本動作確認用
"""

import streamlit as st
import time
import sys

def main():
    st.set_page_config(
        page_title="Simple Test App",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧪 Simple Test App")
    st.markdown("### 基本動作確認")
    
    # 基本情報表示
    st.success("✅ Streamlit is running!")
    
    # Python情報
    st.info(f"Python version: {sys.version}")
    
    # テストセクション
    st.markdown("### 🧪 基本機能テスト")
    
    if st.button("テストボタン"):
        st.write("🎉 ボタンがクリックされました！")
        st.balloons()
    
    # 入力テスト
    user_input = st.text_input("テキストを入力してください:")
    if user_input:
        st.write(f"入力されたテキスト: {user_input}")
    
    # スライダーテスト
    slider_value = st.slider("数値を選択:", 0, 100, 50)
    st.write(f"選択された数値: {slider_value}")
    
    # 時間表示
    st.markdown("### 🕐 現在時刻")
    st.write(f"現在時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # システム情報
    st.markdown("### 📊 システム情報")
    st.write(f"Streamlitバージョン: {st.__version__}")
    
    # リフレッシュボタン
    if st.button("ページをリフレッシュ"):
        st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 次のステップ")
    st.write("1. この基本アプリが正常に動作することを確認")
    st.write("2. 音声機能を追加")
    st.write("3. AI機能を追加")

if __name__ == "__main__":
    main()
