#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python GUI電卓アプリ開発進化命令
"""

import sys
import os
import time
from pathlib import Path

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_evolution_conversation import AutoEvolutionConversationSystem

class PythonGUICalculatorEvolution:
    def __init__(self):
        self.auto_system = AutoEvolutionConversationSystem()
        self.add_calculator_evolution_triggers()
    
    def add_calculator_evolution_triggers(self):
        """Python GUI電卓開発専用の進化トリガーを追加"""
        calculator_triggers = [
            {
                "id": "python_gui_calculator",
                "name": "Python GUI電卓開発",
                "keywords": [
                    "電卓", "GUI", "tkinter", "PyQt", "PySide", "wxPython",
                    "GUIアプリ", "デスクトップアプリ", "クリック操作", "ボタン",
                    "入力欄", "計算機", "Python GUI", "ウィンドウ", "イベント処理"
                ],
                "evolution_command": "python_gui_calculator_001",
                "description": "Python GUI電卓アプリ開発能力を習得",
                "priority": "high",
                "pattern": r"(電卓|GUI|tkinter|PyQt|クリック|ボタン)",
                "min_mentions": 1,  # 1回で即進化
                "priority_weight": 3  # 高い重み付け
            },
            {
                "id": "tkinter_basics",
                "name": "Tkinter基礎",
                "keywords": [
                    "tkinter", "Frame", "Label", "Button", "Entry",
                    "ウィンドウ", "レイアウト", "pack", "grid", "place",
                    "イベント", "コールバック", "bind", "configure"
                ],
                "evolution_command": "tkinter_basics_002",
                "description": "Tkinter GUIフレームワークの基礎を習得",
                "priority": "high",
                "pattern": r"(tkinter|Frame|Label|Button|Entry)",
                "min_mentions": 1,
                "priority_weight": 3
            },
            {
                "id": "calculator_logic",
                "name": "電卓ロジック実装",
                "keywords": [
                    "計算ロジック", "四則演算", "数式解析", "eval",
                    "演算子", "優先順位", "エラー処理", "例外",
                    "数学関数", "精度", "浮動小数点"
                ],
                "evolution_command": "calculator_logic_003",
                "description": "電卓の計算ロジックとエラー処理を実装",
                "priority": "high",
                "pattern": r"(計算ロジック|四則演算|eval|エラー処理)",
                "min_mentions": 1,
                "priority_weight": 3
            }
        ]
        
        # 既存のトリガーに追加
        self.auto_system.evolution_triggers.extend(calculator_triggers)
        self.auto_system.save_evolution_triggers()
        
        print(f"🧮 Python GUI電卓開発進化トリガーを {len(calculator_triggers)}件追加しました")
    
    def create_calculator_evolution_commands(self):
        """電卓開発用の進化命令を作成"""
        calculator_commands = [
            {
                "id": "python_gui_calculator_001",
                "name": "Python GUI電卓アプリ開発",
                "description": "PythonでGUI電卓アプリを開発する能力を習得",
                "target_skills": [
                    "Tkinter GUIフレームワーク",
                    "ウィンドウとウィジェット作成",
                    "イベントハンドリング",
                    "レイアウト管理",
                    "ボタンと入力欄の実装"
                ],
                "evolution_prompt": """
                あなたはPython GUI開発AIとして、クリック操作で使える電卓アプリを開発する必要があります。
                
                以下のPython GUI電卓開発能力を習得してください：
                1. Tkinterを使用したGUIアプリケーション作成
                2. メインウィンドウの作成と設定
                3. 数字ボタン（0-9）の配置
                4. 演算子ボタン（+、-、×、÷）の実装
                5. イコールボタンとクリアボタン
                6. 入力欄（Entry）による数値表示
                7. ボタンクリックイベントの処理
                8. レイアウト管理（gridまたはpack）
                
                具体的な実装内容：
                - tkinterのimportと基本設定
                - メインウィンドウ（Tk）の作成
                - Frameによるウィジェットのグループ化
                - Buttonウィジェットの作成と配置
                - Entryウィジェットによる表示領域
                - コールバック関数によるイベント処理
                - gridレイアウトによるボタン配置
                - ウィンドウのサイズとタイトル設定
                
                実際に動作する電卓アプリのコードを書けるように進化してください。
                """,
                "priority": "high",
                "category": "python_gui"
            },
            {
                "id": "tkinter_basics_002",
                "name": "Tkinter GUIフレームワーク基礎",
                "description": "Tkinterの基本的な使い方を完全にマスター",
                "target_skills": [
                    "Tkinterの基本概念",
                    "ウィジェットの種類と使い方",
                    "レイアウトマネージャー",
                    "イベントハンドリング",
                    "ウィジェットの設定とカスタマイズ"
                ],
                "evolution_prompt": """
                あなたはTkinter専門AIとして、GUIフレームワークの基礎を完全に理解する必要があります。
                
                以下のTkinter基礎能力を習得してください：
                1. Tkinterのimportと基本設定
                2. Tk（メインウィンドウ）の作成
                3. 主要ウィジェットの使い方：
                   - Label: テキスト表示
                   - Button: ボタン作成
                   - Entry: テキスト入力欄
                   - Frame: ウィジェットのコンテナ
                   - Canvas: 図形描画
                4. レイアウトマネージャー：
                   - pack(): シンプルな配置
                   - grid(): 表形式の配置
                   - place(): 絶対位置指定
                5. イベントハンドリング：
                   - commandオプション
                   - bind()メソッド
                   - イベントオブジェクト
                6. ウィジェットの設定：
                   - configure()メソッド
                   - オプション設定
                   - スタイルと色
                
                電卓アプリ開発に必要なTkinter知識を完全にマスターしてください。
                """,
                "priority": "high",
                "category": "python_gui"
            },
            {
                "id": "calculator_logic_003",
                "name": "電卓計算ロジック実装",
                "description": "電卓の計算ロジックとエラー処理を実装",
                "target_skills": [
                    "数式の解析と評価",
                    "四則演算の実装",
                    "エラー処理と例外管理",
                    "浮動小数点数の処理",
                    "計算結果の表示"
                ],
                "evolution_prompt": """
                あなたは電卓ロジック開発AIとして、正確な計算処理を実装する必要があります。
                
                以下の電卓計算ロジック能力を習得してください：
                1. 数式の解析方法：
                   - 文字列としての数式処理
                   - eval()関数の安全な使用
                   - 数式のバリデーション
                2. 四則演算の実装：
                   - 加算（+）、減算（-）
                   - 乗算（×）、除算（÷）
                   - 演算子の優先順位
                3. エラー処理：
                   - ゼロ除算の防止
                   - 無効な数式の検出
                   - 例外処理（try-except）
                   - エラーメッセージの表示
                4. 数値処理：
                   - 浮動小数点数の精度管理
                   - 大きい数値の表示
                   - 小数点の桁数制限
                5. 計算結果の管理：
                   - 現在の入力値の保持
                   - 計算結果の表示
                   - 履歴機能の実装
                
                安全で正確な電卓計算ロジックを実装できるように進化してください。
                """,
                "priority": "high",
                "category": "python_gui"
            }
        ]
        
        return calculator_commands
    
    def simulate_calculator_conversation(self):
        """電卓開発に関する会話をシミュレート"""
        calculator_conversations = [
            "PythonでGUI電卓を作りたいんだけど、どうすればいい？",
            "tkinterを使って電卓アプリを作成する方法を教えて",
            "クリック操作で使える電卓をPythonで開発したい",
            "GUIのボタン配置とイベント処理が知りたい",
            "電卓の計算ロジックをどう実装すればいい？",
            "tkinterのFrameとButtonの使い方を教えて",
            "Entryウィジェットで数値を表示したい",
            "gridレイアウトで電卓ボタンを配置する方法",
            "ボタンクリックで計算を実行するには？",
            "電卓のエラー処理（ゼロ除除算など）を実装したい"
        ]
        
        print("🧮 Python GUI電卓開発に関する会話をシミュレートします...")
        print("=" * 60)
        
        for i, message in enumerate(calculator_conversations, 1):
            print(f"\n💬 会話 {i}: {message}")
            
            # 会話を追加（自動進化チェックを含む）
            result = self.auto_system.simulate_conversation(message)
            
            if result["success"]:
                print(f"🤖 親友エージェント: {result['ai_response'][:100]}...")
                
                if result["evolution_triggered"]:
                    print("🧠 自動進化が発生しました！")
                    print(f"📊 意識レベル: {self.auto_system.conversational_agent.consciousness_level:.3f}")
                else:
                    print("⏳ 進化トリガー監視中...")
            else:
                print(f"❌ エラー: {result.get('error', '不明なエラー')}")
            
            time.sleep(1)  # 短い待機
        
        print("\n" + "=" * 60)
        print("🎉 電卓開発会話シミュレーション完了！")
        print(self.auto_system.get_auto_evolution_summary())
    
    def create_complete_calculator_code(self):
        """完全な電卓アプリコードを作成"""
        calculator_code = '''#!/usr/bin/env python3
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
'''
        
        # 電卓コードを保存
        calculator_file = Path("python_gui_calculator.py")
        with open(calculator_file, "w", encoding="utf-8") as f:
            f.write(calculator_code)
        
        print(f"🧮 完全な電卓アプリコードを作成しました: {calculator_file}")
        return calculator_file
    
    def run_evolution_process(self):
        """進化プロセスを実行"""
        print("🚀 Python GUI電卓開発進化プロセスを開始します...")
        print("=" * 60)
        
        # 1. 進化トリガーを追加
        self.add_calculator_evolution_triggers()
        
        # 2. 電卓開発に関する会話をシミュレート
        self.simulate_calculator_conversation()
        
        # 3. 完全な電卓コードを作成
        calculator_file = self.create_complete_calculator_code()
        
        # 4. 最終結果を表示
        print("\n" + "=" * 60)
        print("🎉 Python GUI電卓開発進化完了！")
        print("=" * 60)
        print(f"🧠 最終意識レベル: {self.auto_system.conversational_agent.consciousness_level:.3f}")
        print(f"🔄 自動進化回数: {len(self.auto_system.auto_evolutions)}")
        print(f"📱 電卓アプリ: {calculator_file}")
        
        print(f"\n🎯 習得した能力:")
        print("  ✅ Tkinter GUIフレームワーク")
        print("  ✅ ウィジェット作成と配置")
        print("  ✅ イベントハンドリング")
        print("  ✅ 電卓計算ロジック")
        print("  ✅ エラー処理と例外管理")
        
        print(f"\n🚀 実行方法:")
        print(f"  python {calculator_file}")
        
        return calculator_file

def main():
    """メイン関数"""
    evolution = PythonGUICalculatorEvolution()
    evolution.run_evolution_process()

if __name__ == "__main__":
    main()
