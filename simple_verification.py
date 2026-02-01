#!/usr/bin/env python3
"""
AI Agent System - 簡単検証スクリプト
"""

import sys

def test_packages():
    """パッケージテスト"""
    packages = [
        "streamlit", "langchain", "langchain_ollama", "langchain_community",
        "langchain_experimental", "fastapi", "uvicorn", "requests",
        "faster_whisper", "pyttsx3", "sounddevice", "numpy", "scipy",
        "pyautogui", "PIL", "qrcode", "openpyxl", "fitz", "pandas",
        "duckduckgo_search", "yt_dlp", "sentence_transformers", "faiss_cpu",
        "transformers", "chromadb", "psutil", "schedule"
    ]
    
    print("🔍 パッケージ検証中...")
    success_count = 0
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
            success_count += 1
        except ImportError:
            print(f"❌ {package}")
    
    print(f"\n📊 結果: {success_count}/{len(packages)} 成功")
    return success_count == len(packages)

def test_external_tools():
    """外部ツールテスト"""
    import subprocess
    
    print("\n🛠️ 外部ツール検証中...")
    
    # Ollamaテスト
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        print(f"✅ Ollama: {len(models)}個のモデル")
    except:
        print("❌ Ollama: 接続失敗")
    
    # PHPテスト
    try:
        result = subprocess.run(["php", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ PHP: {result.stdout.split()[1] if len(result.stdout.split()) > 1 else 'Unknown'}")
        else:
            print("❌ PHP: 実行不可")
    except:
        print("❌ PHP: インストール未")

def main():
    """メイン実行"""
    print("🚀 AI Agent System - 最終検証")
    print("=" * 50)
    
    # パッケージテスト
    package_success = test_packages()
    
    # 外部ツールテスト
    test_external_tools()
    
    print("\n" + "=" * 50)
    print("🎉 検証完了")
    
    if package_success:
        print("✅ すべてのパッケージが正常にインストールされています")
        print("🚀 基本基盤（AI・GUI・通信）の構築完了！")
    else:
        print("❌ 一部のパッケージで問題があります")

if __name__ == "__main__":
    main()
