#!/usr/bin/env python3
"""
AI Agent System - 最終検証スクリプト
全機能の動作を包括的にテストする
"""

import sys
import os
import time
import subprocess
from datetime import datetime

def test_all_packages():
    """全パッケージの動作確認"""
    print("🔍 全パッケージ動作確認中...")
    
    packages_to_test = [
        ("streamlit", "streamlit"),
        ("langchain", "langchain"),
        ("langchain-ollama", "langchain_ollama"),
        ("langchain-community", "langchain_community"),
        ("langchain-experimental", "langchain_experimental"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("requests", "requests"),
        ("faster-whisper", "faster_whisper"),
        ("pyttsx3", "pyttsx3"),
        ("sounddevice", "sounddevice"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("pyautogui", "pyautogui"),
        ("pillow", "PIL"),
        ("qrcode", "qrcode"),
        ("openpyxl", "openpyxl"),
        ("pymupdf", "fitz"),  # PyMuPDFはfitzとしてインポート
        ("pandas", "pandas"),
        ("duckduckgo-search", "duckduckgo_search"),
        ("yt-dlp", "yt_dlp"),
        ("sentence-transformers", "sentence_transformers"),
        ("faiss-cpu", "faiss_cpu"),
        ("transformers", "transformers"),
        ("chromadb", "chromadb"),
        ("psutil", "psutil"),
        ("schedule", "schedule")
    ]
    
    results = []
    
    for package_name, import_name in packages_to_test:
        try:
            __import__(import_name)
            results.append(f"✅ {package_name}")
        except ImportError as e:
            results.append(f"❌ {package_name}: {str(e)}")
    
    print(f"\n📦 検証結果:")
    for result in results:
        print(f"  {result}")
    
    return all("✅" in result for result in results)

def test_external_tools():
    """外部ツールの動作確認"""
    print("🛠️ 外部ツール動作確認中...")
    
    tools_to_test = [
        ("Ollama", "ollama"),
        ("PHP", "php"),
        ("Python", "python"),
        ("Web検索", "duckduckgo_search")
    ]
    
    results = []
    
    for tool_name, command in tools_to_test:
        try:
            if tool_name == "Ollama":
                import ollama
                client = ollama.Client()
                models = client.list()
                results.append(f"✅ Ollama: {len(models)}個のモデル利用可能")
            elif tool_name == "PHP":
                result = subprocess.run(["php", "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.split()[1] if len(result.stdout.split()) > 1 else "Unknown"
                    results.append(f"✅ PHP: {version}")
                else:
                    results.append(f"❌ PHP: {result.stderr}")
            elif tool_name == "Python":
                version = sys.version
                results.append(f"✅ Python: {version}")
            elif tool_name == "Web検索":
                from duckduckgo_search import DDGS
                ddgs = DDGS()
                results.append(f"✅ Web検索: DuckDuckGo検索利用可能")
            else:
                results.append(f"❌ {tool_name}: テスト対象外")
    
    print(f"\n🛠️ 外部ツール検証結果:")
    for result in results:
        print(f"  {result}")
    
    return all("✅" in result for result in results)

def test_ai_functionality():
    """AI機能の動作確認"""
    print("🤖 AI機能動作確認中...")
    
    try:
        import ollama
        client = ollama.Client()
        
        # テストプロンプト
        test_prompt = "これはテストです。こんにちは！"
        
        response = client.generate(
            model="llama3.1:8b",
            prompt=test_prompt,
            options={"max_tokens": 50}
        )
        
        print(f"✅ Ollama応答生成: {response['response'][:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ AI機能エラー: {str(e)}")
        return False

def test_file_processing():
    """ファイル処理機能の動作確認"""
    print("📄 ファイル処理動作確認中...")
    
    try:
        # Excelテスト
        import openpyxl
        import pandas as pd
        from io import BytesIO
        
        # テストデータ作成
        test_data = {
            "名前": "テスト",
            "年齢": 30,
            "職業": "エンジニア",
            "給料": "5000000"
        }
        
        # Excelファイルとしてメモリに保存
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df = pd.DataFrame(test_data, index=[0])
            df.to_excel(writer, index=False)
            excel_data = output.getvalue()
        
        # 読み込みテスト
        df_read = pd.read_excel(BytesIO(excel_data))
        
        print(f"✅ Excel処理: 読み込み・書き込み成功")
        
        # PDFテスト
        import pymupdf
        
        # PDFテスト用テキストファイル作成
        pdf_content = "これはPDFテストです。"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name
        
        # PDF読み込みテスト
        doc = pymupdf.open(tmp_file_path)
        text = doc.page(0).get_text()
        
        print(f"✅ PDF処理: 読み込み成功: {text[:50]}...")
        
    except Exception as e:
        print(f"❌ ファイル処理エラー: {str(e)}")
        return False

def test_ui_operations():
    """UI操作機能の動作確認"""
    print("🖥️ UI操作動作確認中...")
    
    try:
        # QRコード生成テスト
        import qrcode
        
        qr = qrcode.QRCode("テスト用QRコード")
        img = qr.make_image(fill_color="black", back_color="white")
        
        print("✅ QRコード生成: 成功")
        
        # 画面キャプチャテスト
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_screenshot_{timestamp}.png"
        screenshot.save(filename)
        
        print(f"✅ 画面キャプチャ: {filename}")
        
    except Exception as e:
        print(f"❌ UI操作エラー: {str(e)}")
        return False

def test_system_monitoring():
    """システム監視機能の動作確認"""
    print("📊 システム監視動作確認中...")
    
    try:
        import psutil
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"✅ CPU使用率: {cpu_percent}%")
        
        # メモリ使用量
        memory = psutil.virtual_memory()
        print(f"✅ メモリ使用率: {memory.percent}%")
        
        # ディスク容量
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        print(f"✅ 空き容量: {free_gb:.1f}GB")
        
    except Exception as e:
        print(f"❌ システム監視エラー: {str(e)}")
        return False

def main():
    """メイン実行"""
    print("🚀 AI Agent System - 最終検証開始")
    print("=" * 50)
    
    start_time = time.time()
    
    # 全パッケージテスト
    package_success = test_all_packages()
    
    # 外部ツールテスト
    tools_success = test_external_tools()
    
    # AI機能テスト
    ai_success = test_ai_functionality()
    
    # ファイル処理テスト
    file_success = test_file_processing()
    
    # UI操作テスト
    ui_success = test_ui_operations()
    
    # システム監視テスト
    monitoring_success = test_system_monitoring()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("=" * 50)
    print("🎉 検証完了")
    print(f"⏱️ 実行時間: {duration:.2f}秒")
    
    # 結果サマリー
    all_tests = [
        ("パッケージ", package_success),
        ("外部ツール", tools_success),
        ("AI機能", ai_success),
        ("ファイル処理", file_success),
        ("UI操作", ui_success),
        ("システム監視", monitoring_success)
    ]
    
    print("\n📊 最終結果サマリー:")
    for test_name, success in all_tests:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    all_success = all(all_tests)
    
    if all_success:
        print("\n🎉 すべてのテストが成功しました！")
        print("🚀 基本基盤（AI・GUI・通信）の構築が完了しました！")
    else:
        print("\n⚠️ 一部のテストで問題が見つかりました")
        print("📋 詳細なエラーの確認と修正が必要です")

if __name__ == "__main__":
    main()
