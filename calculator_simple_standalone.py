#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スタンドアロン電卓アプリ作成デモ（ワークスペース不要）
"""

import asyncio
import time
import json
import os
from typing import Dict, List, Any

class SimpleCalculatorDemo:
    """シンプルな電卓デモ"""
    
    def __init__(self):
        self.timeout = 240
        self.progress_log = []
    
    def log_progress(self, message: str, progress: float = 0.0):
        """進捗をログ"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message} ({progress:.1f}%)"
        self.progress_log.append(log_entry)
        print(log_entry)
    
    def generate_calculator_code(self) -> str:
        """電卓コードを生成"""
        return '''import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("電卓アプリ")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.history = []
        self.history_file = "calculator_history.json"
        
        self.load_history()
        self.setup_ui()
    
    def load_history(self):
        """履歴を読み込み"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def save_history(self):
        """履歴を保存"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def setup_ui(self):
        """UIをセットアップ"""
        # 表示画面
        self.display = tk.Label(
            self.root, 
            text="0", 
            font=("Arial", 24, "bold"),
            bg="#1a1a1a", 
            fg="white", 
            anchor="e", 
            padx=20, 
            pady=20
        )
        self.display.pack(fill="x", padx=10, pady=10)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ボタン配置
        buttons = [
            ["C", "±", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "=", "⌫"]
        ]
        
        colors = {
            "C": "#ff4444", "±": "#505050", "%": "#505050", "÷": "#ff9500",
            "7": "#505050", "8": "#505050", "9": "#505050", "×": "#ff9500",
            "4": "#505050", "5": "#505050", "6": "#505050", "-": "#ff9500",
            "1": "#505050", "2": "#505050", "3": "#505050", "+": "#ff9500",
            "0": "#505050", ".": "#505050", "=": "#ff9500", "⌫": "#505050"
        }
        
        for row, button_row in enumerate(buttons):
            for col, button_text in enumerate(button_row):
                btn = tk.Button(
                    button_frame,
                    text=button_text,
                    font=("Arial", 18, "bold"),
                    bg=colors[button_text],
                    fg="white",
                    width=5,
                    height=2,
                    relief="flat",
                    command=lambda t=button_text: self.on_click(t)
                )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
            # グリッドの重みを設定
            button_frame.grid_columnconfigure(col, weight=1)
        
        for row in range(len(buttons)):
            button_frame.grid_rowconfigure(row, weight=1)
        
        # 履歴ボタン
        history_btn = tk.Button(
            self.root,
            text="履歴",
            font=("Arial", 12),
            bg="#333333",
            fg="white",
            command=self.show_history
        )
        history_btn.pack(fill="x", padx=10, pady=5)
    
    def on_click(self, button_text):
        """ボタンクリック処理"""
        if button_text == "C":
            self.clear()
        elif button_text == "⌫":
            self.backspace()
        elif button_text == "±":
            self.toggle_sign()
        elif button_text == "%":
            self.percentage()
        elif button_text == "=":
            self.calculate()
        elif button_text in "÷×-+":
            self.set_operation(button_text)
        else:
            self.append_input(button_text)
    
    def append_input(self, value):
        """入力を追加"""
        if self.current_input == "0" and value != ".":
            self.current_input = value
        else:
            self.current_input += value
        self.update_display()
    
    def clear(self):
        """クリア"""
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.update_display()
    
    def backspace(self):
        """バックスペース"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            if not self.current_input:
                self.current_input = "0"
            self.update_display()
    
    def toggle_sign(self):
        """符号を切り替え"""
        if self.current_input and self.current_input != "0":
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
            self.update_display()
    
    def percentage(self):
        """パーセント計算"""
        try:
            value = float(self.current_input)
            self.current_input = str(value / 100)
            self.update_display()
        except:
            pass
    
    def set_operation(self, op):
        """演算子を設定"""
        if self.current_input:
            self.result = float(self.current_input)
            self.operation = op
            self.current_input = ""
            self.update_display()
    
    def calculate(self):
        """計算実行"""
        if self.operation and self.current_input:
            try:
                current = float(self.current_input)
                expression = f"{self.result} {self.operation} {current}"
                
                if self.operation == "+":
                    self.result += current
                elif self.operation == "-":
                    self.result -= current
                elif self.operation == "×":
                    self.result *= current
                elif self.operation == "÷":
                    if current == 0:
                        messagebox.showerror("エラー", "ゼロで除算できません")
                        return
                    self.result /= current
                
                # 履歴に追加
                self.history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "expression": expression,
                    "result": str(self.result)
                })
                self.save_history()
                
                self.current_input = str(self.result)
                self.operation = None
                self.update_display()
                
            except Exception as e:
                messagebox.showerror("エラー", f"計算エラー: {e}")
    
    def update_display(self):
        """表示を更新"""
        display_text = self.current_input if self.current_input else str(self.result)
        self.display.config(text=display_text)
    
    def show_history(self):
        """履歴を表示"""
        if not self.history:
            messagebox.showinfo("履歴", "履歴がありません")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("計算履歴")
        history_window.geometry("500x400")
        
        # 履歴リスト
        listbox = tk.Listbox(history_window, font=("Arial", 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for entry in reversed(self.history[-50:]):  # 最新50件
            listbox.insert(tk.END, f"{entry['timestamp']} - {entry['expression']} = {entry['result']}")
        
        # クリアボタン
        def clear_history():
            self.history = []
            self.save_history()
            listbox.delete(0, tk.END)
            messagebox.showinfo("完了", "履歴をクリアしました")
        
        clear_btn = tk.Button(
            history_window,
            text="履歴をクリア",
            command=clear_history
        )
        clear_btn.pack(pady=5)
    
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()

if __name__ == "__main__":
    app = Calculator()
    app.run()
'''
    
    def create_calculator_files(self):
        """電卓ファイルを作成"""
        self.log_progress("電卓アプリの作成を開始します...", 10.0)
        
        # 基本電卓
        calculator_code = self.generate_calculator_code()
        
        files_created = []
        
        # 基本電卓アプリ
        basic_file = "calculator_basic.py"
        with open(basic_file, 'w', encoding='utf-8') as f:
            f.write(calculator_code)
        files_created.append(basic_file)
        self.log_progress(f"基本電卓アプリを作成: {basic_file}", 30.0)
        
        # Web電卓アプリ
        web_file = "calculator_web.py"
        web_code = '''import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Web電卓", page_icon="🧮")

st.title("🧮 Web電卓アプリ")

# 履歴ファイル
history_file = "web_calculator_history.json"

def load_history():
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass

# 履歴読み込み
if 'history' not in st.session_state:
    st.session_state.history = load_history()

# 電卓入力
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    expression = st.text_input("計算式を入力:", placeholder="例: 2+3*4")

with col2:
    if st.button("計算", type="primary"):
        try:
            result = eval(expression)
            
            # 履歴に追加
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "expression": expression,
                "result": str(result)
            }
            st.session_state.history.insert(0, entry)
            save_history(st.session_state.history)
            
            st.success(f"結果: {result}")
        except Exception as e:
            st.error(f"エラー: {e}")

with col3:
    if st.button("クリア"):
        st.session_state.history = []
        save_history(st.session_state.history)
        st.rerun()

# 履歴表示
st.markdown("---")
st.subheader("📜 計算履歴")

if st.session_state.history:
    for i, entry in enumerate(st.session_state.history[:10]):
        with st.expander(f"📅 {entry['timestamp']} - {entry['expression']} = {entry['result']}"):
            st.code(f"式: {entry['expression']}")
            st.code(f"結果: {entry['result']}")
else:
    st.info("履歴がありません")
'''
        
        with open(web_file, 'w', encoding='utf-8') as f:
            f.write(web_code)
        files_created.append(web_file)
        self.log_progress(f"Web電卓アプリを作成: {web_file}", 60.0)
        
        # 起動スクリプト
        start_script = "start_calculator.bat"
        script_content = '''@echo off
echo 🧮 電卓アプリ起動メニュー
echo.
echo 1. 基本電卓アプリ (tkinter)
echo 2. Web電卓アプリ (Streamlit)
echo 3. 終了
echo.
set /p choice="選択してください (1-3): "

if "%choice%"=="1" (
    echo 基本電卓アプリを起動します...
    python calculator_basic.py
) else if "%choice%"=="2" (
    echo Web電卓アプリを起動します...
    streamlit run calculator_web.py
) else if "%choice%"=="3" (
    echo 終了します。
    exit
) else (
    echo 無効な選択です。
    pause
)
'''
        
        with open(start_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        files_created.append(start_script)
        self.log_progress(f"起動スクリプトを作成: {start_script}", 80.0)
        
        # README
        readme_file = "CALCULATOR_README.md"
        readme_content = '''# 電卓アプリ

## 作成されたファイル

1. **calculator_basic.py** - tkinterベースのデスクトップ電卓アプリ
2. **calculator_web.py** - StreamlitベースのWeb電卓アプリ
3. **start_calculator.bat** - 起動メニュースクリプト

## 実行方法

### 方法1: 起動メニューを使用
```
start_calculator.bat
```

### 方法2: 直接実行
```
# 基本電卓
python calculator_basic.py

# Web電卓
streamlit run calculator_web.py
```

## 機能

- 基本四則演算
- 履歴機能
- エラーハンドリング
- モダンなUI
'''
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files_created.append(readme_file)
        self.log_progress(f"READMEファイルを作成: {readme_file}", 90.0)
        
        self.log_progress(f"すべてのファイル作成完了！計{len(files_created)}個", 100.0)
        
        return files_created
    
    def run_demo(self):
        """デモを実行"""
        print("🚀 スタンドアロン電卓アプリ作成デモ")
        print("=" * 50)
        
        files_created = self.create_calculator_files()
        
        print(f"\n✅ 作成完了！")
        print(f"📁 生成されたファイル:")
        for file in files_created:
            size = os.path.getsize(file)
            print(f"   📄 {file} ({size} バイト)")
        
        print(f"\n🎯 実行方法:")
        print(f"   1. start_calculator.bat を実行")
        print(f"   2. または直接 python calculator_basic.py")
        print(f"   3. Web版: streamlit run calculator_web.py")
        
        print(f"\n🎉 デモ完了！")

if __name__ == "__main__":
    demo = SimpleCalculatorDemo()
    demo.run_demo()
