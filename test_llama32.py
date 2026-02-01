#!/usr/bin/env python3
"""
llama3.2 Migration Test Script
"""

import ollama
import time

def test_llama32_models():
    """llama3.2モデルテスト"""
    print("llama3.2 Model Test")
    print("=" * 50)
    
    try:
        client = ollama.Client()
        models = client.list()
        
        # モデル確認
        model_names = [m.get('name', '') for m in models]
        print(f"Available models: {model_names}")
        
        # llama3.2確認
        llama32_available = "llama3.2" in model_names
        llama32_vision_available = "llama3.2-vision" in model_names
        
        print(f"\nllama3.2 available: {llama32_available}")
        print(f"llama3.2-vision available: {llama32_vision_available}")
        
        if not llama32_available:
            print("ERROR: llama3.2 model not found")
            return False
        
        if not llama32_vision_available:
            print("ERROR: llama3.2-vision model not found")
            return False
        
        # llama3.2テスト
        print("\nTesting llama3.2 (text generation)...")
        start_time = time.time()
        
        response = client.generate(
            model="llama3.2",
            prompt="こんにちは！これはllama3.2のテストです。簡潔に答えてください。",
            options={
                "temperature": 0.7,
                "max_tokens": 100
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Response time: {response_time:.2f} seconds")
        print(f"Response: {response['response']}")
        
        # llama3.2-visionテスト（画面キャプチャなしでテキストのみ）
        print("\nTesting llama3.2-vision (text mode)...")
        start_time = time.time()
        
        vision_response = client.generate(
            model="llama3.2-vision",
            prompt="これはビジョンモデルのテストです。自己紹介してください。",
            options={
                "temperature": 0.7,
                "max_tokens": 100
            }
        )
        
        end_time = time.time()
        vision_response_time = end_time - start_time
        
        print(f"Vision model response time: {vision_response_time:.2f} seconds")
        print(f"Vision response: {vision_response['response']}")
        
        print("\n" + "=" * 50)
        print("SUCCESS: llama3.2 models are working correctly!")
        print(f"llama3.2 response time: {response_time:.2f}s")
        print(f"llama3.2-vision response time: {vision_response_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {str(e)}")
        return False

def test_model_routing():
    """モデル・ルーティングテスト"""
    print("\nModel Routing Test")
    print("-" * 30)
    
    test_cases = [
        {"prompt": "こんにちは", "images": None, "expected": "llama3.2"},
        {"prompt": "この画像について説明してください", "images": ["test.jpg"], "expected": "llama3.2-vision"},
        {"prompt": "複雑な技術的質問", "images": None, "expected": "llama3.2"},
        {"prompt": "画面のエラーを確認", "images": ["screenshot.png"], "expected": "llama3.2-vision"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        prompt = test_case["prompt"]
        images = test_case["images"]
        expected = test_case["expected"]
        
        # シンプルなルーティングロジック
        if images and len(images) > 0:
            selected_model = "llama3.2-vision"
        else:
            selected_model = "llama3.2"
        
        status = "✅" if selected_model == expected else "❌"
        print(f"Test {i}: {status} Expected: {expected}, Selected: {selected_model}")

def main():
    """メイン実行"""
    print("llama3.2 Migration Test Suite")
    print("=" * 60)
    
    # モデルテスト
    model_test_passed = test_llama32_models()
    
    # ルーティングテスト
    test_model_routing()
    
    if model_test_passed:
        print("\n" + "=" * 60)
        print("MIGRATION SUCCESSFUL!")
        print("\nNext Steps:")
        print("1. Run: streamlit run llama32_optimized_app.py")
        print("2. Open browser to http://localhost:8501")
        print("3. Test llama3.2 fast responses")
        print("4. Test llama3.2-vision screen analysis")
        print("5. Enable fast mode for quick responses")
    else:
        print("\n" + "=" * 60)
        print("MIGRATION FAILED!")
        print("Please check model availability and Ollama service")

if __name__ == "__main__":
    main()
