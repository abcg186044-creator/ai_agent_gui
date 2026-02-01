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
    print("🔍 Vision AI Integration Test")
    print("=" * 50)
    
    try:
        # Ollamaクライアント初期化
        client = ollama.Client()
        print("✅ Ollama client initialized")
        
        # 利用可能モデル確認
        models = client.list()
        vision_models = [m['name'] for m in models if 'vision' in m['name'].lower()]
        
        print(f"📋 Available vision models: {vision_models}")
        
        if not vision_models:
            print("❌ No vision models found")
            return False
        
        # 画面キャプチャテスト
        print("\n📸 Testing screen capture...")
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_path = f"test_vision_{timestamp}.png"
        screenshot.save(temp_path)
        print(f"✅ Screen captured: {temp_path}")
        
        # ビジョン分析テスト
        print("\n👁️ Testing vision analysis...")
        response = client.generate(
            model="llama3.2-vision",
            prompt="この画面について簡潔に説明してください",
            images=[temp_path]
        )
        
        print("✅ Vision analysis completed")
        print(f"📊 Analysis result: {response['response'][:200]}...")
        
        # OCRテスト
        print("\n📝 Testing OCR functionality...")
        ocr_response = client.generate(
            model="llama3.2-vision",
            prompt="この画像からすべてのテキストを抽出してください",
            images=[temp_path]
        )
        
        print("✅ OCR completed")
        print(f"📝 OCR result: {ocr_response['response'][:200]}...")
        
        # UI要素分析テスト
        print("\n🎨 Testing UI element analysis...")
        ui_response = client.generate(
            model="llama3.2-vision",
            prompt="この画面のUI要素（ボタン、メニュー、入力フィールドなど）を分析してください",
            images=[temp_path]
        )
        
        print("✅ UI analysis completed")
        print(f"🎨 UI analysis result: {ui_response['response'][:200]}...")
        
        # 一時ファイル削除
        try:
            os.unlink(temp_path)
            print(f"\n🗑️ Temporary file deleted: {temp_path}")
        except:
            pass
        
        print("\n" + "=" * 50)
        print("🎉 Vision AI Integration Test Completed Successfully!")
        print("✅ All vision features are working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

def test_model_availability():
    """モデル利用可能性テスト"""
    print("\n🔍 Model Availability Test")
    print("-" * 30)
    
    try:
        client = ollama.Client()
        models = client.list()
        
        print("📋 Available models:")
        for model in models:
            name = model.get('name', 'Unknown')
            size = model.get('size', 'Unknown')
            modified = model.get('modified', 'Unknown')
            print(f"  - {name} ({size}) - {modified}")
        
        # llama3.2-visionの確認
        vision_available = any('llama3.2-vision' in m.get('name', '') for m in models)
        
        if vision_available:
            print("\n✅ llama3.2-vision model is available")
        else:
            print("\n❌ llama3.2-vision model not found")
        
        return vision_available
        
    except Exception as e:
        print(f"❌ Model availability test failed: {str(e)}")
        return False

def main():
    """メイン実行"""
    print("🚀 Vision AI System Integration Test")
    print("=" * 60)
    
    # モデル利用可能性確認
    model_available = test_model_availability()
    
    if not model_available:
        print("\n❌ Please ensure llama3.2-vision model is installed")
        print("Run: ollama pull llama3.2-vision")
        return
    
    # ビジョンシステムテスト
    vision_test_passed = test_vision_system()
    
    if vision_test_passed:
        print("\n🎯 Next Steps:")
        print("1. Run: streamlit run vision_enhanced_app.py")
        print("2. Open browser to http://localhost:8501")
        print("3. Test vision features in the web interface")
        print("4. Upload images or capture screen for analysis")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
