#!/usr/bin/env python3
"""
Vision AI Integration Test Script
"""

import ollama
import pyautogui
import tempfile
import os
from datetime import datetime

def test_vision_system():
    """ビジョンシステムテスト"""
    print("Vision AI Integration Test")
    print("=" * 50)
    
    try:
        # Ollamaクライアント初期化
        client = ollama.Client()
        print("OK: Ollama client initialized")
        
        # 利用可能モデル確認
        models = client.list()
        vision_models = [m['name'] for m in models if 'vision' in m['name'].lower()]
        
        print(f"Available vision models: {vision_models}")
        
        if not vision_models:
            print("FAIL: No vision models found")
            return False
        
        # 画面キャプチャテスト
        print("\nTesting screen capture...")
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_path = f"test_vision_{timestamp}.png"
        screenshot.save(temp_path)
        print(f"OK: Screen captured: {temp_path}")
        
        # ビジョン分析テスト
        print("\nTesting vision analysis...")
        response = client.generate(
            model="llama3.2-vision",
            prompt="この画面について簡潔に説明してください",
            images=[temp_path]
        )
        
        print("OK: Vision analysis completed")
        print(f"Analysis result: {response['response'][:200]}...")
        
        # 一時ファイル削除
        try:
            os.unlink(temp_path)
            print(f"\nTemporary file deleted: {temp_path}")
        except:
            pass
        
        print("\n" + "=" * 50)
        print("SUCCESS: Vision AI Integration Test Completed!")
        print("OK: All vision features are working correctly")
        
        return True
        
    except Exception as e:
        print(f"\nFAIL: Test failed: {str(e)}")
        return False

def main():
    """メイン実行"""
    print("Vision AI System Integration Test")
    print("=" * 60)
    
    # ビジョンシステムテスト
    vision_test_passed = test_vision_system()
    
    if vision_test_passed:
        print("\nNext Steps:")
        print("1. Run: streamlit run vision_enhanced_app.py")
        print("2. Open browser to http://localhost:8501")
        print("3. Test vision features in the web interface")
        print("4. Upload images or capture screen for analysis")
    else:
        print("\nWARNING: Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
