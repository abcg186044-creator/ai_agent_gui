#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルな電卓アプリ作成デモ（分割版）
"""

import asyncio
import time
import json
from typing import Dict, List, Any

# シンプルなモッククラス
class SimpleTaskRunner:
    """シンプルなタスクランナー"""
    
    def __init__(self):
        self.tasks = {}
        self.stats = {"total": 0, "completed": 0, "failed": 0}
    
    def add_task(self, description: str, code: str, file_path: str = None) -> str:
        """タスクを追加"""
        task_id = f"task_{int(time.time() * 1000)}"
        self.tasks[task_id] = {
            "id": task_id,
            "description": description,
            "code": code,
            "file_path": file_path,
            "status": "completed",
            "created_at": time.time()
        }
        self.stats["total"] += 1
        self.stats["completed"] += 1
        return task_id
    
    def get_task_status(self, task_id: str):
        """タスクステータスを取得"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        """すべてのタスクを取得"""
        return list(self.tasks.values())
    
    def get_stats(self):
        """統計を取得"""
        return self.stats

class SimpleAIClient:
    """シンプルなAIクライアント"""
    
    def __init__(self):
        self.models = ["mock_model_1", "mock_model_2", "mock_model_3"]
    
    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        """応答を生成"""
        await asyncio.sleep(0.1)  # 少し遅延
        
        # 電卓アプリのコードを生成
        if "電卓" in prompt:
            code = '''import tkinter as tk
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
        else:
            code = f"# 基本的なコード\ndef main():\n    print('Generated for: {prompt}')\n\nif __name__ == '__main__':\n    main()"
        
        return {
            "success": True,
            "response": code,
            "model": "mock_calculator_generator",
            "elapsed_time": 0.1
        }
    
    async def generate_parallel_responses(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """並列応答生成"""
        tasks = []
        for prompt in prompts:
            task = asyncio.create_task(self.generate_response(prompt))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "success": False,
                    "error": str(result),
                    "task_id": i
                })
            else:
                result["task_id"] = i
                formatted_results.append(result)
        
        return formatted_results

class SimpleCalculatorDemo:
    """シンプルな電卓デモ"""
    
    def __init__(self):
        self.ai_client = SimpleAIClient()
        self.task_runner = SimpleTaskRunner()
        self.progress_log = []
    
    def log_progress(self, message: str, progress: float = 0.0):
        """進捗をログ"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message} ({progress:.1f}%)"
        self.progress_log.append(log_entry)
        print(log_entry)
    
    async def run_demo(self):
        """デモを実行"""
        print("🚀 シンプル電卓アプリ作成デモ開始")
        print("=" * 60)
        
        # 電卓アプリの要件
        calculator_prompts = [
            "PythonでGUI電卓アプリを作成してください。tkinterを使用し、四則演算ができるようにしてください。",
            "電卓アプリに履歴機能を追加してください。計算結果を保存して表示できるようにしてください。",
            "電卓アプリのデザインを改善してください。モダンな見た目と使いやすさを向上させてください。"
        ]
        
        self.log_progress("電卓アプリ要件を準備中...", 10.0)
        
        # 並列でAI生成を実行
        self.log_progress("AIで電卓アプリを並列生成中...", 20.0)
        results = await self.ai_client.generate_parallel_responses(calculator_prompts)
        
        successful_results = [r for r in results if r["success"]]
        self.log_progress(f"AI生成完了: {len(successful_results)}/{len(calculator_prompts)} 成功", 40.0)
        
        # 生成されたコードをタスクとして追加
        task_ids = []
        for i, result in enumerate(successful_results):
            file_name = f"calculator_v{i+1}.py"
            task_id = self.task_runner.add_task(
                description=f"電卓アプリ v{i+1}",
                code=result["response"],
                file_path=file_name
            )
            task_ids.append(task_id)
            self.log_progress(f"タスク追加: {file_name}", 50.0 + i * 10)
        
        # ファイルに保存
        self.log_progress("生成されたコードをファイルに保存中...", 80.0)
        for task_id in task_ids:
            task = self.task_runner.get_task_status(task_id)
            if task and task["file_path"]:
                try:
                    with open(task["file_path"], 'w', encoding='utf-8') as f:
                        f.write(task["code"])
                    self.log_progress(f"ファイル保存完了: {task['file_path']}", 85.0)
                except Exception as e:
                    self.log_progress(f"ファイル保存エラー: {e}", 85.0)
        
        # 統計表示
        stats = self.task_runner.get_stats()
        self.log_progress(f"デモ完了！総タスク: {stats['total']}, 完了: {stats['completed']}", 100.0)
        
        print(f"\n📊 最終結果:")
        print(f"   生成した電卓アプリ: {len(successful_results)}個")
        print(f"   保存したファイル: {len(task_ids)}個")
        
        print(f"\n📁 生成されたファイル:")
        for task_id in task_ids:
            task = self.task_runner.get_task_status(task_id)
            if task:
                print(f"   📄 {task['file_path']} ({len(task['code'])} 文字)")
        
        print(f"\n🎯 実行方法:")
        print(f"   python calculator_v1.py  # 基本電卓")
        print(f"   python calculator_v2.py  # 履歴機能付き電卓")
        print(f"   python calculator_v3.py  # 改善版電卓")
        
        print(f"\n🎉 デモ完了！")
        
        return {
            "success": True,
            "generated_apps": len(successful_results),
            "saved_files": len(task_ids),
            "stats": stats
        }

# メイン実行
if __name__ == "__main__":
    demo = SimpleCalculatorDemo()
    asyncio.run(demo.run_demo())
