#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI電卓アプリケーション
Tkinterを使用したクリック操作可能な電卓
"""

import tkinter as tk
from tkinter import messagebox
import math

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI電卓")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # 変数初期化
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.new_operation = True
        
        # 色設定
        self.bg_color = "#2b2b2b"
        self.button_color = "#404040"
        self.operator_color = "#ff9500"
        self.number_color = "#505050"
        self.text_color = "#ffffff"
        
        self.root.configure(bg=self.bg_color)
        
        self.create_widgets()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # 表示画面
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        display_frame = tk.Frame(self.root, bg=self.bg_color)
        display_frame.pack(pady=20, padx=20, fill="x")
        
        self.display = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            anchor="e",
            padx=20,
            pady=20
        )
        self.display.pack(fill="x")
        
        # ボタンフレーム
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10, padx=20)
        
        # ボタン配置
        buttons = [
            ("C", 0, 0, self.clear, self.operator_color),
            ("±", 0, 1, self.toggle_sign, self.operator_color),
            ("%", 0, 2, self.percentage, self.operator_color),
            ("÷", 0, 3, lambda: self.set_operation("/"), self.operator_color),
            
            ("7", 1, 0, lambda: self.append_number("7"), self.number_color),
            ("8", 1, 1, lambda: self.append_number("8"), self.number_color),
            ("9", 1, 2, lambda: self.append_number("9"), self.number_color),
            ("×", 1, 3, lambda: self.set_operation("*"), self.operator_color),
            
            ("4", 2, 0, lambda: self.append_number("4"), self.number_color),
            ("5", 2, 1, lambda: self.append_number("5"), self.number_color),
            ("6", 2, 2, lambda: self.append_number("6"), self.number_color),
            ("−", 2, 3, lambda: self.set_operation("-"), self.operator_color),
            
            ("1", 3, 0, lambda: self.append_number("1"), self.number_color),
            ("2", 3, 1, lambda: self.append_number("2"), self.number_color),
            ("3", 3, 2, lambda: self.append_number("3"), self.number_color),
            ("+", 3, 3, lambda: self.set_operation("+"), self.operator_color),
            
            ("0", 4, 0, lambda: self.append_number("0"), self.number_color),
            (".", 4, 1, self.append_decimal, self.number_color),
            ("⌫", 4, 2, self.backspace, self.operator_color),
            ("=", 4, 3, self.calculate, self.operator_color)
        ]
        
        # ボタン作成
        for text, row, col, command, color in buttons:
            button = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 18, "bold"),
                bg=color,
                fg=self.text_color,
                width=5,
                height=2,
                command=command,
                relief="flat",
                bd=0
            )
            button.grid(row=row, column=col, padx=5, pady=5)
            
            # ホバーエフェクト
            button.bind("<Enter>", lambda e, b=button: b.config(bg=self.lighten_color(b["bg"])))
            button.bind("<Leave>", lambda e, b=button, c=color: b.config(bg=c))
        
        # 0ボタンは2列分の幅
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        
        zero_button = tk.Button(
            button_frame,
            text="0",
            font=("Arial", 18, "bold"),
            bg=self.number_color,
            fg=self.text_color,
            height=2,
            command=lambda: self.append_number("0"),
            relief="flat",
            bd=0
        )
        zero_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        zero_button.bind("<Enter>", lambda e: zero_button.config(bg=self.lighten_color(self.number_color)))
        zero_button.bind("<Leave>", lambda e: zero_button.config(bg=self.number_color))
    
    def lighten_color(self, color):
        """色を明るくする"""
        if color == self.number_color:
            return "#606060"
        elif color == self.operator_color:
            return "#ffb040"
        return color
    
    def append_number(self, number):
        """数字を追加"""
        if self.new_operation:
            self.current_input = ""
            self.new_operation = False
        
        if self.current_input == "0":
            self.current_input = number
        else:
            self.current_input += number
        
        self.update_display()
    
    def append_decimal(self):
        """小数点を追加"""
        if self.new_operation:
            self.current_input = "0."
            self.new_operation = False
        elif "." not in self.current_input:
            self.current_input += "."
        
        self.update_display()
    
    def set_operation(self, op):
        """演算子を設定"""
        if self.current_input:
            if self.operation and not self.new_operation:
                self.calculate()
            
            self.result = float(self.current_input)
            self.operation = op
            self.new_operation = True
    
    def calculate(self):
        """計算を実行"""
        if self.operation and self.current_input:
            try:
                current_value = float(self.current_input)
                
                if self.operation == "+":
                    self.result += current_value
                elif self.operation == "-":
                    self.result -= current_value
                elif self.operation == "*":
                    self.result *= current_value
                elif self.operation == "/":
                    if current_value == 0:
                        messagebox.showerror("エラー", "ゼロで割ることはできません")
                        return
                    self.result /= current_value
                
                self.current_input = str(self.result)
                self.operation = None
                self.new_operation = True
                self.update_display()
                
            except ValueError:
                messagebox.showerror("エラー", "無効な入力です")
                self.clear()
    
    def clear(self):
        """クリア"""
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.new_operation = True
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
        if self.current_input:
            try:
                value = float(self.current_input)
                self.current_input = str(value / 100)
                self.update_display()
            except ValueError:
                pass
    
    def backspace(self):
        """バックスペース"""
        if self.current_input and len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        elif self.current_input and len(self.current_input) == 1:
            self.current_input = "0"
            self.new_operation = True
        
        self.update_display()
    
    def update_display(self):
        """表示を更新"""
        if self.current_input:
            # 表示用にフォーマット
            try:
                value = float(self.current_input)
                if value.is_integer():
                    display_text = str(int(value))
                else:
                    display_text = f"{value:.10g}"
            except ValueError:
                display_text = self.current_input
        else:
            display_text = "0"
        
        self.display_var.set(display_text)
    
    def handle_keypress(self, event):
        """キーボード入力を処理"""
        if event.char.isdigit():
            self.append_number(event.char)
        elif event.char == ".":
            self.append_decimal()
        elif event.char == "+":
            self.set_operation("+")
        elif event.char == "-":
            self.set_operation("-")
        elif event.char == "*":
            self.set_operation("*")
        elif event.char == "/":
            self.set_operation("/")
        elif event.keysym == "Return" or event.char == "=":
            self.calculate()
        elif event.keysym == "Escape" or event.char.lower() == "c":
            self.clear()
        elif event.keysym == "BackSpace":
            self.backspace()

def main():
    """メイン関数"""
    root = tk.Tk()
    calculator = Calculator(root)
    
    # キーボードイベントをバインド
    root.bind("<Key>", calculator.handle_keypress)
    
    # ウィンドウを中央に配置
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    print("🧮 GUI電卓アプリを起動しました")
    print("📝 操作方法:")
    print("   - 数字ボタンまたはキーボードで数字入力")
    print("   - 演算子ボタンまたはキーボード(+,-,*,/)で計算")
    print("   - Enterキーまたは=ボタンで計算実行")
    print("   - EscキーまたはCボタンでクリア")
    print("   - Backspaceキーまたは⌫ボタンで一文字削除")
    
    root.mainloop()

if __name__ == "__main__":
    main()
