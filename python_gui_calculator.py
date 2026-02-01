#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python GUI電卓アプリケーション
tkinterを使用したクリック操作可能な電卓
"""

import tkinter as tk
from tkinter import messagebox
import math

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python GUI電卓")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # 計算用変数
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.new_number = True
        
        # 色の設定
        self.bg_color = "#f0f0f0"
        self.button_color = "#ffffff"
        self.operator_color = "#ffa500"
        self.equals_color = "#4CAF50"
        self.clear_color = "#f44336"
        
        self.create_widgets()
        
    def create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 表示欄
        self.display_var = tk.StringVar(value="0")
        display = tk.Entry(
            main_frame,
            textvariable=self.display_var,
            font=("Arial", 24, "bold"),
            justify="right",
            bd=10,
            relief=tk.RIDGE,
            bg="white"
        )
        display.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")
        
        # ボタンの配置
        buttons = [
            # 1行目
            ("C", 1, 0, self.clear, self.clear_color),
            ("±", 1, 1, self.toggle_sign, self.button_color),
            ("%", 1, 2, self.percentage, self.button_color),
            ("÷", 1, 3, lambda: self.set_operation("/"), self.operator_color),
            
            # 2行目
            ("7", 2, 0, lambda: self.append_number("7"), self.button_color),
            ("8", 2, 1, lambda: self.append_number("8"), self.button_color),
            ("9", 2, 2, lambda: self.append_number("9"), self.button_color),
            ("×", 2, 3, lambda: self.set_operation("*"), self.operator_color),
            
            # 3行目
            ("4", 3, 0, lambda: self.append_number("4"), self.button_color),
            ("5", 3, 1, lambda: self.append_number("5"), self.button_color),
            ("6", 3, 2, lambda: self.append_number("6"), self.button_color),
            ("−", 3, 3, lambda: self.set_operation("-"), self.operator_color),
            
            # 4行目
            ("1", 4, 0, lambda: self.append_number("1"), self.button_color),
            ("2", 4, 1, lambda: self.append_number("2"), self.button_color),
            ("3", 4, 2, lambda: self.append_number("3"), self.button_color),
            ("+", 4, 3, lambda: self.set_operation("+"), self.operator_color),
            
            # 5行目
            ("0", 5, 0, lambda: self.append_number("0"), self.button_color),
            (".", 5, 1, self.append_decimal, self.button_color),
            ("⌫", 5, 2, self.backspace, self.button_color),
            ("=", 5, 3, self.calculate, self.equals_color)
        ]
        
        # ボタンを作成
        for text, row, col, command, color in buttons:
            btn = tk.Button(
                main_frame,
                text=text,
                font=("Arial", 18, "bold"),
                bg=color,
                fg="black",
                width=5,
                height=2,
                relief=tk.RAISED,
                bd=2,
                command=command
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            
            # グリッドの重みを設定
            main_frame.grid_columnconfigure(col, weight=1)
            main_frame.grid_rowconfigure(row, weight=1)
    
    def append_number(self, number):
        """数字を追加"""
        if self.new_number:
            self.current_input = ""
            self.new_number = False
        
        self.current_input += str(number)
        self.update_display()
    
    def append_decimal(self):
        """小数点を追加"""
        if self.new_number:
            self.current_input = "0"
            self.new_number = False
        
        if "." not in self.current_input:
            self.current_input += "."
            self.update_display()
    
    def set_operation(self, op):
        """演算子を設定"""
        if self.current_input:
            if self.operation and not self.new_number:
                self.calculate()
            
            self.result = float(self.current_input)
            self.operation = op
            self.new_number = True
    
    def calculate(self):
        """計算を実行"""
        if self.operation and self.current_input:
            try:
                current = float(self.current_input)
                
                if self.operation == "+":
                    self.result += current
                elif self.operation == "-":
                    self.result -= current
                elif self.operation == "*":
                    self.result *= current
                elif self.operation == "/":
                    if current == 0:
                        messagebox.showerror("エラー", "ゼロで除算できません")
                        return
                    self.result /= current
                
                self.current_input = str(self.result)
                self.operation = None
                self.new_number = True
                self.update_display()
                
            except Exception as e:
                messagebox.showerror("エラー", f"計算エラー: {e}")
                self.clear()
    
    def clear(self):
        """クリア"""
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.new_number = True
        self.update_display()
    
    def toggle_sign(self):
        """符号を切り替え"""
        if self.current_input:
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
            self.update_display()
    
    def percentage(self):
        """パーセント計算"""
        if self.current_input:
            try:
                value = float(self.current_input) / 100
                self.current_input = str(value)
                self.update_display()
            except:
                messagebox.showerror("エラー", "無効な数値です")
    
    def backspace(self):
        """バックスペース"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            if not self.current_input:
                self.current_input = "0"
                self.new_number = True
            self.update_display()
    
    def update_display(self):
        """表示を更新"""
        if self.current_input:
            # 表示を整形（長すぎる場合は科学表記）
            try:
                value = float(self.current_input)
                if abs(value) >= 1e10 or (abs(value) < 1e-10 and value != 0):
                    display_text = f"{value:.2e}"
                else:
                    # 小数点以下の不要なゼロを削除
                    display_text = str(value).rstrip('0').rstrip('.') if '.' in str(value) else str(value)
                self.display_var.set(display_text)
            except:
                self.display_var.set(self.current_input)
        else:
            self.display_var.set("0")
    
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()

if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
