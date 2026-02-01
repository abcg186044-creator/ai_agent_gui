#!/usr/bin/env python3
"""
AI Agent System - 検証スクリプト
"""

import sys

def test_packages():
    """パッケージテスト"""
    packages = [
        "streamlit", "langchain", "langchain_ollama", "langchain_community",
        "langchain_experimental", "fastapi", "uvicorn", "requests",
        "faster_whisper", "pyttsx3", "sounddevice", "numpy", "scipy",
        "pyautogui", "PIL", "qrcode", "openpyxl", "fitz", "pandas",
        "duckduckgo_search", "yt_dlp", "sentence_transformers", "faiss",  # faiss_cpuではなくfaiss
        "transformers", "chromadb", "psutil", "schedule"
    ]
    
    print("Package verification...")
    success_count = 0
    
    for package in packages:
        try:
            __import__(package)
            print(f"OK: {package}")
            success_count += 1
        except ImportError:
            print(f"FAIL: {package}")
    
    print(f"\nResult: {success_count}/{len(packages)} successful")
    return success_count == len(packages)

def test_external_tools():
    """外部ツールテスト"""
    import subprocess
    
    print("\nExternal tools verification...")
    
    # Ollamaテスト
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        print(f"OK: Ollama - {len(models)} models available")
    except:
        print("FAIL: Ollama - connection failed")
    
    # PHPテスト
    try:
        result = subprocess.run(["C:\\Program Files\\PHP\\current\\php.exe", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"OK: PHP - {result.stdout.split()[1] if len(result.stdout.split()) > 1 else 'Unknown'}")
        else:
            print("FAIL: PHP - cannot execute")
    except:
        print("FAIL: PHP - not installed")

def main():
    """メイン実行"""
    print("AI Agent System - Final Verification")
    print("=" * 50)
    
    # パッケージテスト
    package_success = test_packages()
    
    # 外部ツールテスト
    test_external_tools()
    
    print("\n" + "=" * 50)
    print("Verification Complete")
    
    if package_success:
        print("SUCCESS: All packages installed correctly")
        print("READY: Basic infrastructure (AI/GUI/Communication) complete!")
    else:
        print("WARNING: Some packages have issues")

if __name__ == "__main__":
    main()
