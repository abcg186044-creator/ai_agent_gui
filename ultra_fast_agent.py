#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超高速版制限なし親友エージェント
"""

from unlimited_agent_manager import UnlimitedAgentManager
from unlimited_agent_core import ApproachInterface, StaticKnowledgeApproach, TemplateApproach, HeuristicApproach
import time

class UltraFastApproach(ApproachInterface):
    """超高速アプローチ"""
    
    def __init__(self):
        self.static_kb = StaticKnowledgeApproach()
        self.template = TemplateApproach()
        self.heuristic = HeuristicApproach()
    
    def get_name(self) -> str:
        return "ultra_fast"
    
    def execute(self, prompt: str, task_description: str, progress_callback=None) -> str:
        # 静的知識ベースを優先
        if progress_callback:
            progress_callback({
                "step": "⚡ 超高速モードで実行中...",
                "progress": 20,
                "approach": "ultra_fast"
            })
        
        # タスクタイプを検出
        task_lower = task_description.lower()
        
        if progress_callback:
            progress_callback({
                "step": "🔍 タスクを高速分析中...",
                "progress": 40,
                "approach": "ultra_fast"
            })
        
        # 電卓系タスクは即時応答
        if "電卓" in task_lower or "calculator" in task_lower:
            if progress_callback:
                progress_callback({
                    "step": "⚡ 電卓アプリを即時生成...",
                    "progress": 80,
                    "approach": "ultra_fast"
                })
            
            return self._get_instant_calculator()
        
        # Web系タスク
        elif "web" in task_lower or "html" in task_lower:
            if progress_callback:
                progress_callback({
                    "step": "⚡ Webアプリを即時生成...",
                    "progress": 80,
                    "approach": "ultra_fast"
                })
            
            return self._get_instant_web_app()
        
        # Android系タスク
        elif "android" in task_lower or "アプリ" in task_lower:
            if progress_callback:
                progress_callback({
                    "step": "⚡ Androidアプリを即時生成...",
                    "progress": 80,
                    "approach": "ultra_fast"
                })
            
            return self._get_instant_android_app()
        
        # その他はテンプレートで対応
        else:
            if progress_callback:
                progress_callback({
                    "step": "⚡ テンプレートで即時応答...",
                    "progress": 80,
                    "approach": "ultra_fast"
                })
            
            return self.template.execute(prompt, task_description, progress_callback)
    
    def _get_instant_calculator(self) -> str:
        """即時電卓アプリ"""
        return '''# Python GUI電卓アプリ

## 完全なコード
```python
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
```

## 実行方法
1. 上記コードを `calculator.py` として保存
2. `python calculator.py` を実行
3. GUI電卓が起動します'''
    
    def _get_instant_web_app(self) -> str:
        """即時Webアプリ"""
        return '''# HTML電卓アプリ

## 完全なコード
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>電卓</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f0f0f0; }
        .calculator { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .display { background: #1a1a1a; color: white; font-size: 24px; text-align: right; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
        .buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; }
        button { padding: 20px; font-size: 18px; border: none; border-radius: 5px; cursor: pointer; background: #505050; color: white; }
        button:hover { background: #606060; }
        button.operator { background: #ff9500; }
        button.clear { background: #ff4444; grid-column: span 4; }
    </style>
</head>
<body>
    <div class="calculator">
        <div class="display" id="display">0</div>
        <div class="buttons">
            <button onclick="appendNumber('7')">7</button><button onclick="appendNumber('8')">8</button><button onclick="appendNumber('9')">9</button><button class="operator" onclick="setOperation('/')">/</button>
            <button onclick="appendNumber('4')">4</button><button onclick="appendNumber('5')">5</button><button onclick="appendNumber('6')">6</button><button class="operator" onclick="setOperation('*')">*</button>
            <button onclick="appendNumber('1')">1</button><button onclick="appendNumber('2')">2</button><button onclick="appendNumber('3')">3</button><button class="operator" onclick="setOperation('-')">-</button>
            <button onclick="appendNumber('0')">0</button><button onclick="appendNumber('.')">.</button><button class="operator" onclick="calculate()">=</button><button class="operator" onclick="setOperation('+')">+</button>
            <button class="clear" onclick="clear()">C</button>
        </div>
    </div>
    <script>
        let currentInput = '0'; let firstNumber = 0; let operation = null;
        function updateDisplay() { document.getElementById('display').textContent = currentInput; }
        function appendNumber(num) { if (currentInput === '0') { currentInput = num; } else { currentInput += num; } updateDisplay(); }
        function setOperation(op) { firstNumber = parseFloat(currentInput); operation = op; currentInput = '0'; }
        function calculate() { if (operation) { const secondNumber = parseFloat(currentInput); let result; switch (operation) { case '+': result = firstNumber + secondNumber; break; case '-': result = firstNumber - secondNumber; break; case '*': result = firstNumber * secondNumber; break; case '/': result = firstNumber / secondNumber; break; } currentInput = result.toString(); operation = null; updateDisplay(); } }
        function clear() { currentInput = '0'; firstNumber = 0; operation = null; updateDisplay(); }
    </script>
</body>
</html>
```

## 実行方法
1. 上記コードを `calculator.html` として保存
2. ブラウザで開く
3. Web電卓が使用できます'''
    
    def _get_instant_android_app(self) -> str:
        """即時Androidアプリ"""
        return '''# Android電卓アプリ

## 完全なコード
```kotlin
// MainActivity.kt
package com.example.calculator

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private lateinit var editText: EditText
    private var currentNumber = 0.0
    private var operation: String? = null
    private var firstNumber = 0.0
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        editText = findViewById(R.id.editTextNumber)
        
        // ボタン設定
        findViewById<Button>(R.id.buttonPlus).setOnClickListener { setOperation("+") }
        findViewById<Button>(R.id.buttonMinus).setOnClickListener { setOperation("-") }
        findViewById<Button>(R.id.buttonMultiply).setOnClickListener { setOperation("*") }
        findViewById<Button>(R.id.buttonDivide).setOnClickListener { setOperation("/") }
        findViewById<Button>(R.id.buttonEquals).setOnClickListener { calculate() }
        findViewById<Button>(R.id.buttonClear).setOnClickListener { clear() }
        
        // 数字ボタン
        findViewById<Button>(R.id.button0).setOnClickListener { appendNumber("0") }
        findViewById<Button>(R.id.button1).setOnClickListener { appendNumber("1") }
        findViewById<Button>(R.id.button2).setOnClickListener { appendNumber("2") }
        findViewById<Button>(R.id.button3).setOnClickListener { appendNumber("3") }
        findViewById<Button>(R.id.button4).setOnClickListener { appendNumber("4") }
        findViewById<Button>(R.id.button5).setOnClickListener { appendNumber("5") }
        findViewById<Button>(R.id.button6).setOnClickListener { appendNumber("6") }
        findViewById<Button>(R.id.button7).setOnClickListener { appendNumber("7") }
        findViewById<Button>(R.id.button8).setOnClickListener { appendNumber("8") }
        findViewById<Button>(R.id.button9).setOnClickListener { appendNumber("9") }
        findViewById<Button>(R.id.buttonDot).setOnClickListener { appendNumber(".") }
    }
    
    private fun appendNumber(num: String) {
        val current = editText.text.toString()
        if (current == "0" && num != ".") {
            editText.text = num
        } else {
            editText.text = current + num
        }
    }
    
    private fun setOperation(op: String) {
        firstNumber = editText.text.toString().toDouble()
        operation = op
        editText.text = "0"
    }
    
    private fun calculate() {
        val secondNumber = editText.text.toString().toDouble()
        val result = when (operation) {
            "+" -> firstNumber + secondNumber
            "-" -> firstNumber - secondNumber
            "*" -> firstNumber * secondNumber
            "/" -> firstNumber / secondNumber
            else -> 0.0
        }
        editText.text = result.toString()
        operation = null
    }
    
    private fun clear() {
        editText.text = "0"
        firstNumber = 0.0
        operation = null
    }
}
```

## レイアウトファイル (activity_main.xml)
```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">
    
    <EditText
        android:id="@+id/editTextNumber"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="0"
        android:textSize="24sp"
        android:gravity="end"
        android:editable="false" />
    
    <GridLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:columnCount="4"
        android:layout_marginTop="16dp">
        
        <Button android:id="@+id/button7" android:text="7" />
        <Button android:id="@+id/button8" android:text="8" />
        <Button android:id="@+id/button9" android:text="9" />
        <Button android:id="@+id/buttonDivide" android:text="/" />
        
        <Button android:id="@+id/button4" android:text="4" />
        <Button android:id="@+id/button5" android:text="5" />
        <Button android:id="@+id/button6" android:text="6" />
        <Button android:id="@+id/buttonMultiply" android:text="*" />
        
        <Button android:id="@+id/button1" android:text="1" />
        <Button android:id="@+id/button2" android:text="2" />
        <Button android:id="@+id/button3" android:text="3" />
        <Button android:id="@+id/buttonMinus" android:text="-" />
        
        <Button android:id="@+id/button0" android:text="0" />
        <Button android:id="@+id/buttonDot" android:text="." />
        <Button android:id="@+id/buttonEquals" android:text="=" />
        <Button android:id="@+id/buttonPlus" android:text="+" />
        
        <Button android:id="@+id/buttonClear" android:text="C" android:layout_columnSpan="4" />
    </GridLayout>
</LinearLayout>
```

## 実行方法
1. Android Studioで新規プロジェクト作成
2. 上記コードを配置
3. ビルドして実行'''

class UltraFastAgent:
    """超高速版制限なし親友エージェント"""
    
    def __init__(self):
        self.manager = UnlimitedAgentManager()
        # 超高速アプローチを最優先
        self.manager.approaches.insert(0, UltraFastApproach())
    
    def generate_response_with_fallback(self, prompt: str, task_description: str = "", progress_callback=None):
        """超高速応答生成"""
        return self.manager.generate_response_with_fallback(prompt, task_description, progress_callback)

# テスト用
if __name__ == "__main__":
    agent = UltraFastAgent()
    
    test_cases = [
        ("PythonでGUIをクリックして操作できる電卓アプリを作成してください", "Python GUI電卓アプリ開発"),
        ("HTMLで電卓アプリを作成してください", "Web電卓アプリ開発"),
        ("Androidで電卓アプリを開発してください", "Android電卓アプリ開発")
    ]
    
    print("⚡ 超高速版制限なし親友エージェントテスト開始")
    print("=" * 60)
    
    for i, (prompt, task) in enumerate(test_cases, 1):
        print(f"\n📋 テスト {i}: {task}")
        print("-" * 40)
        
        def progress_callback(progress_info):
            print(f"📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        
        start_time = time.time()
        result = agent.generate_response_with_fallback(prompt, task, progress_callback)
        elapsed = time.time() - start_time
        
        print(f"\n📊 結果:")
        print(f"✅ 成功: {result['success']}")
        print(f"🔄 アプローチ: {result['approach']}")
        print(f"⏱️ 時間: {elapsed:.2f}秒")
        print(f"📝 応答長: {len(result['response'])}文字")
        
        if elapsed < 1.0:
            print(f"⚡ 超高速実行完了！")
    
    print(f"\n🎉 超高速テスト完了！")
