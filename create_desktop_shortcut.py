#!/usr/bin/env python3
"""
デスクトップショートカット作成スクリプト
"""

import os
import sys
import winshell
from win32com.client import Dispatch
import pythoncom

def create_desktop_shortcut():
    """デスクトップにショートカットを作成"""
    
    # パス設定
    current_dir = os.path.dirname(os.path.abspath(__file__))
    batch_file = os.path.join(current_dir, "start_ai.bat")
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "AI Agent System.lnk")
    
    # ショートカット作成
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    
    # ショートカット設定
    shortcut.Targetpath = batch_file
    shortcut.WorkingDirectory = current_dir
    shortcut.IconLocation = batch_file  # バッチファイルのアイコンを使用
    shortcut.Description = "AI Agent System - スマート音声AIエージェント"
    
    # 保存
    shortcut.save()
    
    print(f"✅ デスクトップにショートカットを作成しました: {shortcut_path}")
    print("🎯 デスクトップの「AI Agent System」アイコンをダブルクリックして起動できます")

def create_icon_file():
    """アイコンファイルを作成（簡易版）"""
    # 実際にはアイコンファイルが必要ですが、ここでは説明のみ
    print("💡 アイコン設定のヒント:")
    print("1. 好みのアイコン画像（.ico形式）をダウンロード")
    print("2. プロジェクトフォルダに 'ai_icon.ico' として保存")
    print("3. start_ai.bat の 'shortcut.IconLocation' を 'ai_icon.ico' に変更")

if __name__ == "__main__":
    try:
        create_desktop_shortcut()
        create_icon_file()
    except Exception as e:
        print(f"❌ ショートカット作成エラー: {str(e)}")
        print("💡 手動でショートカットを作成してください")
