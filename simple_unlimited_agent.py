#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル版制限なし親友エージェント
"""

import time

class SimpleUnlimitedAgent:
    def __init__(self):
        self.approaches = [
            "ollama_primary",      # 主要: Ollama API
            "static_knowledge",    # 代替1: 静的知識ベース
            "template_response",    # 代替2: テンプレート応答
            "heuristic_reasoning",  # 代替3: ヒ�heuristics推論
        ]
        
        self.timeout_threshold = 240
        self.knowledge_base = {
            "calculator": self._get_calculator_knowledge(),
            "android_app": self._get_android_knowledge(),
            "web_app": self._get_web_knowledge(),
            "machine_learning": self._get_ml_knowledge()
        }
    
    def _get_calculator_knowledge(self):
        return '''#!/usr/bin/env python3
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
        if self.new_operation:
            self.current_input = ""
            self.new_operation = False
        if self.current_input == "0" and value != ".":
            self.current_input = value
        else:
            self.current_input += value
        self.update_display()
    
    def set_operation(self, op):
        if self.current_input:
            self.result = float(self.current_input)
            self.operation = op
            self.new_operation = True
    
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
                self.new_operation = True
                self.update_display()
            except:
                pass
    
    def clear(self):
        self.current_input = ""
        self.result = 0
        self.operation = None
        self.new_operation = True
        self.update_display()
    
    def update_display(self):
        display_text = self.current_input if self.current_input else str(self.result)
        self.display.config(text=display_text)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Calculator()
    app.run()'''
    
    def _get_android_knowledge(self):
        return '''// Android電卓アプリ
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
        findViewById<Button>(R.id.buttonEquals).setOnClickListener { calculate() }
        findViewById<Button>(R.id.buttonClear).setOnClickListener { clear() }
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
}'''
    
    def _get_web_knowledge(self):
        return '''<!DOCTYPE html>
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
</html>'''
    
    def _get_ml_knowledge(self):
        return '''#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

class MLPipeline:
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    def load_data(self, filepath):
        try:
            self.data = pd.read_csv(filepath)
            print(f"データ読み込み完了: {self.data.shape}")
            return True
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            return False
    
    def preprocess_data(self, target_column):
        if self.data is None: return False
        self.data = self.data.fillna(self.data.mean())
        X = self.data.drop(columns=[target_column])
        y = self.data[target_column]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.is_trained = True
        print(f"前処理完了: 訓練{self.X_train.shape}, テスト{self.X_test.shape}")
        return True
    
    def train_model(self):
        if not hasattr(self, 'X_train'): return False
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(self.X_train, self.y_train)
        predictions = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, predictions)
        print(f"テスト精度: {accuracy:.4f}")
        return True
    
    def save_model(self, filepath):
        if self.is_trained:
            joblib.dump(self.model, filepath)
            print(f"モデルを保存しました: {filepath}")
    
    def run_pipeline(self, data_file, target_column):
        if self.load_data(data_file):
            if self.preprocess_data(target_column):
                if self.train_model():
                    self.save_model("model.joblib")

if __name__ == "__main__":
    pipeline = MLPipeline()
    pipeline.run_pipeline("data.csv", "target")'''
    
    def generate_response_with_fallback(self, prompt, task_description=""):
        """フォールバック付き応答生成"""
        start_time = time.time()
        
        for approach_index, approach in enumerate(self.approaches):
            print(f"🔄 アプローチ {approach_index + 1}/{len(self.approaches)}: {approach}")
            
            try:
                if approach == "ollama_primary":
                    response = self._try_ollama_approach(prompt, task_description)
                elif approach == "static_knowledge":
                    response = self._try_knowledge_approach(task_description)
                elif approach == "template_response":
                    response = self._try_template_approach(task_description)
                elif approach == "heuristic_reasoning":
                    response = self._try_heuristic_approach(prompt, task_description)
                
                if response and not response.startswith("エラー"):
                    elapsed = time.time() - start_time
                    print(f"✅ 成功: {approach} (所要時間: {elapsed:.2f}秒)")
                    
                    return {
                        "success": True,
                        "approach": approach,
                        "response": response,
                        "elapsed_time": elapsed,
                        "approach_index": approach_index
                    }
                    
            except Exception as e:
                print(f"❌ {approach} でエラー: {str(e)}")
                continue
        
        elapsed = time.time() - start_time
        print(f"❌ すべてのアプローチが失敗 (総時間: {elapsed:.2f}秒)")
        
        return {
            "success": False,
            "error": "すべてのアプローチが失敗しました",
            "total_time": elapsed,
            "attempted_approaches": len(self.approaches)
        }
    
    def _try_ollama_approach(self, prompt, task_description):
        """Ollama APIアプローチ"""
        try:
            from ollama_client_progress import OllamaClient
            client = OllamaClient(timeout=self.timeout_threshold)
            response = client.generate_response(prompt)
            return response
        except Exception as e:
            return f"Ollama APIエラー: {str(e)}"
    
    def _try_knowledge_approach(self, task_description):
        """静的知識ベースアプローチ"""
        task_type = self._detect_task_type(task_description)
        
        if task_type in self.knowledge_base:
            kb_entry = self.knowledge_base[task_type]
            return f"""# {kb_entry['description']}

## 機能
{', '.join(kb_entry['features'])}

## 完全なコード
{kb_entry}

## 実行方法
1. コードをファイルに保存
2. 必要なライブラリをインストール
3. 実行してアプリケーションを起動"""
        
        return "該当する静的知識が見つかりません"
    
    def _try_template_approach(self, task_description):
        """テンプレート応答アプローチ"""
        return f"""# {task_description}

## 基本構造
```python
def main():
    print("{task_description}を開始します")
    # 実装を追加
    pass

if __name__ == "__main__":
    main()
```

## 拡張案
1. 必要なライブラリをインポート
2. クラス構造を設計
3. エラー処理を実装
4. テストケースを追加"""
    
    def _try_heuristic_approach(self, prompt, task_description):
        """ヒューリスティクス推論アプローチ"""
        return f"""# ヒューリスティクス推論による解決策

## タスク分析
{task_description}

## 推論プロセス
1. 要件分解
2. アーキテクチャ設計
3. 実装計画
4. テストとデバッグ

## 推奨アプローチ
- 段階的開発
- 継続的インテグレーション
- ユーザーフィードバックの収集"""
    
    def _detect_task_type(self, task_description):
        """タスクタイプを検出"""
        task_lower = task_description.lower()
        
        if "電卓" in task_lower or "calculator" in task_lower:
            return "calculator"
        elif "android" in task_lower or "アプリ" in task_lower:
            return "android_app"
        elif "web" in task_lower or "html" in task_lower:
            return "web_app"
        elif "機械学習" in task_lower or "ml" in task_lower or "ai" in task_lower:
            return "machine_learning"
        
        return "general"

# テスト
if __name__ == "__main__":
    agent = SimpleUnlimitedAgent()
    
    test_prompt = "PythonでGUIをクリックして操作できる電卓アプリを作成してください"
    test_task = "Python GUI電卓アプリ開発"
    
    print("🚀 制限なし親友エージェントテスト開始")
    print("=" * 60)
    
    result = agent.generate_response_with_fallback(test_prompt, test_task)
    
    print("\n📊 結果:")
    print(f"✅ 成功: {result['success']}")
    if result['success']:
        print(f"🔄 使用アプローチ: {result['approach']}")
        print(f"⏱️ 所要時間: {result['elapsed_time']:.2f}秒")
        print(f"📝 応答長: {len(result['response'])}文字")
    else:
        print(f"❌ エラー: {result['error']}")
        print(f"⏱️ 総時間: {result['total_time']:.2f}秒")
        print(f"🔄 試行アプローチ数: {result['attempted_approaches']}")
