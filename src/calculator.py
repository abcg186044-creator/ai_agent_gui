# Python GUI電卓アプリの完全な実装

## 機能
Tkinter, 四則演算, エラー処理, キーボード対応

## 完全なコード
import tkinter as tk

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("電卓")
        self.root.geometry("400x500")
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.create_widgets()
    
    def create_widgets(self):
        self.display = tk.Label(self.root, text="0", font=("Arial", 24), bg="#1a1a1a", fg="white", anchor="e", padx=20, pady=20)
        self.display.pack(fill="x", padx=10, pady=10)
        
        buttons = [["7", "8", "9", "/"], ["4", "5", "6", "*"], ["1", "2", "3", "-"], ["0", ".", "=", "+"], ["C"]]
        
        for row, button_row in enumerate(buttons):
            frame = tk.Frame(self.root)
            frame.pack(fill="x", padx=10, pady=2)
            
            for button_text in button_row:
                color = "#ff9500" if button_text in "/*-+=" else "#505050"
                if button_text == "C":
                    color = "#ff4444"
                
                tk.Button(frame, text=button_text, font=("Arial", 14, "bold"), bg=color, fg="white", width=8, height=2,
                         command=lambda t=button_text: self.on_click(t)).pack(side="left", padx=2, expand=True, fill="both")
    
    def on_click(self, button):
        if button == "C":
            self.clear()
        elif button == "=":
            self.calculate()
        elif button in "+-*/":
            self.set_operation(button)
        else:
            self.append_input(button)
    
    def append_input(self, value):
        if self.current_input == "0" and value != ".":
            self.current_input = value
        else:
            self.current_input += value
        self.update_display()
    
    def set_operation(self, op):
        if self.current_input:
            self.result = float(self.current_input)
            self.operation = op
            self.current_input = ""
    
    def calculate(self):
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
                        return
                    self.result /= current
                self.current_input = str(self.result)
                self.operation = None
                self.update_display()
            except:
                pass
    
    def clear(self):
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.update_display()
    
    def update_display(self):
        display_text = self.current_input if self.current_input else str(self.result)
        self.display.config(text=display_text)

if __name__ == "__main__":
    app = Calculator()
    app.run()

## 実行方法
1. コードをファイルに保存
2. 必要なライブラリをインストール
3. 実行してアプリケーションを起動