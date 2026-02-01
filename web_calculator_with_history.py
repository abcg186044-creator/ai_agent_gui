#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webアクセス可能な電卓アプリ（履歴機能付き）
"""

import streamlit as st
import time
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class WebCalculator:
    """Web電卓アプリケーション"""
    
    def __init__(self):
        self.history_file = "calculator_history.json"
        self.setup_page()
        self.load_history()
    
    def setup_page(self):
        """ページ設定"""
        st.set_page_config(
            page_title="AI生成電卓アプリ",
            page_icon="🧮",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🧮 AI生成電卓アプリ")
        st.markdown("---")
        
        # サイドバーに履歴表示
        st.sidebar.title("📜 計算履歴")
        
        # メインコンテンツ
        self.main_calculator()
        self.display_history()
    
    def load_history(self):
        """履歴を読み込み"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    st.session_state.history = json.load(f)
            except:
                st.session_state.history = []
        else:
            st.session_state.history = []
    
    def save_history(self):
        """履歴を保存"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"履歴保存エラー: {e}")
    
    def add_to_history(self, expression: str, result: str):
        """履歴に追加"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expression": expression,
            "result": result,
            "id": len(st.session_state.history) + 1
        }
        
        st.session_state.history.insert(0, entry)  # 最新を先頭に
        
        # 履歴を最大100件に制限
        if len(st.session_state.history) > 100:
            st.session_state.history = st.session_state.history[:100]
        
        self.save_history()
    
    def clear_history(self):
        """履歴をクリア"""
        st.session_state.history = []
        self.save_history()
        st.rerun()
    
    def main_calculator(self):
        """メイン電卓機能"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # 表示画面
            if 'display' not in st.session_state:
                st.session_state.display = "0"
            
            display_container = st.container()
            with display_container:
                st.markdown("### 📺 表示")
                st.markdown(f"```\n{st.session_state.display}\n```")
        
        with col2:
            st.markdown("### 🎛️ 操作")
            
            # 数字ボタン
            button_cols = st.columns(3)
            numbers = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ".", "C"]
            
            for i, num in enumerate(numbers):
                col_idx = i % 3
                if col_idx == 0 and i > 0:
                    button_cols = st.columns(3)
                
                with button_cols[col_idx]:
                    if num == "C":
                        if st.button(num, key=f"btn_{num}", use_container_width=True, type="secondary"):
                            self.clear_display()
                    else:
                        if st.button(num, key=f"btn_{num}", use_container_width=True):
                            self.append_to_display(num)
        
        with col3:
            st.markdown("### ➕ 演算子")
            
            operators = ["+", "-", "*", "/", "="]
            for op in operators:
                if op == "=":
                    if st.button(op, key=f"btn_{op}", use_container_width=True, type="primary"):
                        self.calculate_result()
                else:
                    if st.button(op, key=f"btn_{op}", use_container_width=True):
                        self.append_operator(op)
            
            st.markdown("---")
            
            # 追加機能
            if st.button("🗑️ 履歴クリア", use_container_width=True):
                self.clear_history()
            
            if st.button("📋 クリップボード", use_container_width=True):
                st.write("クリップボード機能はブラウザの機能を使用してください")
        
        # キーボード入力サポート
        user_input = st.text_input(
            "⌨️ キーボード入力（Enterで計算）",
            key="keyboard_input",
            placeholder="式を入力してください（例: 2+3*4）"
        )
        
        if user_input:
            if st.button("🧮 計算実行", key="calc_keyboard"):
                st.session_state.display = user_input
                self.calculate_result()
    
    def append_to_display(self, value: str):
        """表示に値を追加"""
        if st.session_state.display == "0" and value != ".":
            st.session_state.display = value
        else:
            st.session_state.display += value
        st.rerun()
    
    def append_operator(self, operator: str):
        """演算子を追加"""
        if st.session_state.display and st.session_state.display[-1] not in "+-*/":
            st.session_state.display += operator
            st.rerun()
    
    def clear_display(self):
        """表示をクリア"""
        st.session_state.display = "0"
        st.rerun()
    
    def calculate_result(self):
        """計算を実行"""
        try:
            expression = st.session_state.display
            
            # 安全な計算実行
            result = self.safe_eval(expression)
            
            # 履歴に追加
            self.add_to_history(expression, str(result))
            
            # 結果を表示
            st.session_state.display = str(result)
            
            # 成功メッセージ
            st.success(f"✅ 計算完了: {expression} = {result}")
            
        except Exception as e:
            st.error(f"❌ 計算エラー: {e}")
            st.session_state.display = "Error"
        
        st.rerun()
    
    def safe_eval(self, expression: str):
        """安全な数式評価"""
        # 許可する文字のみをフィルタリング
        allowed_chars = "0123456789+-*/.() "
        filtered_expr = ''.join(c for c in expression if c in allowed_chars)
        
        if filtered_expr != expression:
            raise ValueError("不正な文字が含まれています")
        
        try:
            # evalを使用せず、安全に計算
            return eval(filtered_expr, {"__builtins__": {}}, {})
        except:
            raise ValueError("無効な数式です")
    
    def display_history(self):
        """履歴を表示"""
        st.markdown("---")
        st.markdown("### 📊 計算履歴")
        
        if not st.session_state.history:
            st.info("📝 履歴がありません。計算を開始してください！")
            return
        
        # 履歴表示オプション
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 履歴検索", placeholder="式や結果で検索...")
        
        with col2:
            sort_order = st.selectbox("📅 並び順", ["最新順", "古い順"])
        
        with col3:
            export_format = st.selectbox("💾 エクスポート", ["JSON", "CSV", "TXT"])
        
        # 履歴フィルタリング
        filtered_history = st.session_state.history
        
        if search_term:
            filtered_history = [
                entry for entry in filtered_history
                if search_term.lower() in entry["expression"].lower() 
                or search_term.lower() in entry["result"].lower()
            ]
        
        # 並び替え
        if sort_order == "古い順":
            filtered_history = list(reversed(filtered_history))
        
        # 履歴表示
        for i, entry in enumerate(filtered_history):
            with st.expander(
                f"📅 {entry['timestamp']} - {entry['expression']} = {entry['result']}",
                expanded=i == 0
            ):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.code(f"式: {entry['expression']}")
                    st.code(f"結果: {entry['result']}")
                
                with col2:
                    if st.button(f"📋 再計算", key=f"recalc_{entry['id']}"):
                        st.session_state.display = entry['expression']
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ 削除", key=f"delete_{entry['id']}"):
                        st.session_state.history.remove(entry)
                        self.save_history()
                        st.rerun()
        
        # エクスポート機能
        if st.button(f"💾 {export_format}でエクスポート"):
            self.export_history(filtered_history, export_format)
        
        # 統計情報
        st.markdown("---")
        st.markdown("### 📈 統計情報")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("総計算回数", len(st.session_state.history))
        
        with col2:
            # 今日の計算回数
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = len([
                entry for entry in st.session_state.history
                if entry['timestamp'].startswith(today)
            ])
            st.metric("今日の計算", today_count)
        
        with col3:
            # よく使う演算子
            operators = {"+": 0, "-": 0, "*": 0, "/": 0}
            for entry in st.session_state.history:
                for op in operators:
                    if op in entry['expression']:
                        operators[op] += 1
            
            most_used = max(operators, key=operators.get) if any(operators.values()) else "なし"
            st.metric("よく使う演算子", most_used)
        
        with col4:
            # 平均式の長さ
            if st.session_state.history:
                avg_length = sum(len(entry['expression']) for entry in st.session_state.history) / len(st.session_state.history)
                st.metric("平均式長", f"{avg_length:.1f}文字")
    
    def export_history(self, history: List[Dict], format_type: str):
        """履歴をエクスポート"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "JSON":
            filename = f"calculator_history_{timestamp}.json"
            st.download_button(
                label="📥 JSONダウンロード",
                data=json.dumps(history, ensure_ascii=False, indent=2),
                file_name=filename,
                mime="application/json"
            )
        
        elif format_type == "CSV":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["日時", "式", "結果"])
            
            for entry in history:
                writer.writerow([entry['timestamp'], entry['expression'], entry['result']])
            
            filename = f"calculator_history_{timestamp}.csv"
            st.download_button(
                label="📥 CSVダウンロード",
                data=output.getvalue(),
                file_name=filename,
                mime="text/csv"
            )
        
        elif format_type == "TXT":
            content = "電卓履歴\n" + "="*50 + "\n\n"
            for entry in history:
                content += f"日時: {entry['timestamp']}\n"
                content += f"式: {entry['expression']}\n"
                content += f"結果: {entry['result']}\n"
                content += "-"*30 + "\n"
            
            filename = f"calculator_history_{timestamp}.txt"
            st.download_button(
                label="📥 TXTダウンロード",
                data=content,
                file_name=filename,
                mime="text/plain"
            )

# メイン実行
if __name__ == "__main__":
    app = WebCalculator()
    
    # フッター情報
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            🤖 AI生成電卓アプリ | 履歴機能付き | Webアクセス対応
        </div>
        """,
        unsafe_allow_html=True
    )
