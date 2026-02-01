#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI電卓アプリケーション
"""

import tkinter as tk

class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("電卓アプリ")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        self.entry_value = ""
        
        # 背景色設定
        self.window.configure(bg="#2b2b2b")
        
        # 表示画面の作成
        self.display_label = tk.Label(
            self.window, 
            text="0", 
            width=20, 
            borderwidth=5,
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Arial", 24, "bold"),
            anchor="e"
        )
        self.display_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        
        # 数字ボタンの作成
        buttons = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            '0', '.', '='
        ]
        
        row_val = 1
        col_val = 0
        
        for button in buttons:
            color = "#ff9500" if button == "=" else "#505050"
            tk.Button(
                self.window, 
                text=button, 
                width=10, 
                height=2,
                bg=color,
                fg="white",
                font=("Arial", 14, "bold"),
                command=lambda b=button: self.click_button(b)
            ).grid(row=row_val, column=col_val, padx=2, pady=2)
            
            col_val += 1
            if col_val > 2:
                col_val = 0
                row_val += 1
        
        # 演算子ボタンの作成
        operator_buttons = [
            ("+", 1, 0), ("-", 1, 1), ("*", 1, 2), ("/", 1, 3)
        ]
        
        for text, row, col in operator_buttons:
            tk.Button(
                self.window, 
                text=text, 
                width=10, 
                height=2,
                bg="#404040",
                fg="white",
                font=("Arial", 14, "bold"),
                command=lambda t=text: self.click_button(t)
            ).grid(row=row, column=col, padx=2, pady=2)
        
        # クリアボタンの作成
        tk.Button(
            self.window, 
            text="C", 
            width=43, 
            height=2,
            bg="#ff4444",
            fg="white",
            font=("Arial", 14, "bold"),
            command=self.clear_entry
        ).grid(row=row_val+1, column=0, columnspan=4, padx=2, pady=2)
        
        # キーボードバインド
        self.window.bind('<Key>', self.keyboard_input)
        
    def click_button(self, button):
        if button == "=":
            try:
                # 安全な計算のためにevalを避け、自前で計算
                result = self.calculate(self.entry_value)
                self.display_label['text'] = result
                self.entry_value = result
            except Exception as e:
                self.display_label['text'] = "エラー"
                self.entry_value = ""
        elif button == "C":
            self.clear_entry()
        else:
            if self.entry_value == "0" and button != ".":
                self.entry_value = button
            else:
                self.entry_value += button
            self.display_label['text'] = self.entry_value
    
    def calculate(self, expression):
        """安全な計算関数"""
        try:
            # 基本的な四則演算のみを許可
            if not expression:
                return "0"
            
            # evalの代わりに安全な計算
            # 簡単な計算式をパース
            tokens = []
            current_num = ""
            
            for char in expression:
                if char.isdigit() or char == '.':
                    current_num += char
                elif char in '+-*/':
                    if current_num:
                        tokens.append(float(current_num))
                        current_num = ""
                    tokens.append(char)
                else:
                    continue
            
            if current_num:
                tokens.append(float(current_num))
            
            if not tokens:
                return "0"
            
            # 計算実行
            result = tokens[0]
            i = 1
            while i < len(tokens):
                op = tokens[i]
                if i + 1 < len(tokens):
                    num = tokens[i + 1]
                    if op == '+':
                        result += num
                    elif op == '-':
                        result -= num
                    elif op == '*':
                        result *= num
                    elif op == '/':
                        if num == 0:
                            return "エラー"
                        result /= num
                i += 2
            
            return str(result)
            
        except:
            return "エラー"
    
    def keyboard_input(self, event):
        """キーボード入力処理"""
        key = event.char
        if key.isdigit() or key in '+-*/.':
            self.click_button(key)
        elif key == '\r':  # Enterキー
            self.click_button('=')
        elif key == '\x1b':  # Escapeキー
            self.clear_entry()
    
    def clear_entry(self):
        self.entry_value = ""
        self.display_label['text'] = "0"
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
