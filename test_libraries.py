#!/usr/bin/env python3
"""
Library Test Script - Check all installed packages
"""

def test_libraries():
    """Test all required libraries"""
    print("Library Test")
    print("=" * 50)
    
    libraries = [
        ("streamlit", "streamlit"),
        ("ollama", "ollama"),
        ("faster_whisper", "faster_whisper"),
        ("pyttsx3", "pyttsx3"),
        ("pyautogui", "pyautogui"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("PIL", "PIL"),
        ("qrcode", "qrcode"),
        ("openpyxl", "openpyxl"),
        ("fitz", "fitz"),
        ("duckduckgo_search", "duckduckgo_search"),
        ("chromadb", "chromadb"),
        ("sentence_transformers", "sentence_transformers"),
        ("faiss", "faiss"),
        ("psutil", "psutil"),
        ("schedule", "schedule")
    ]
    
    results = []
    success_count = 0
    
    for lib_name, import_name in libraries:
        try:
            __import__(import_name)
            results.append(f"OK: {lib_name}")
            success_count += 1
        except ImportError as e:
            results.append(f"FAIL: {lib_name} - {str(e)}")
    
    print("Test Results:")
    for result in results:
        print(f"  {result}")
    
    print(f"\nSummary: {success_count}/{len(libraries)} libraries working")
    return success_count == len(libraries)

def test_pip_version():
    """Check pip version"""
    import subprocess
    try:
        result = subprocess.run(["pip", "--version"], capture_output=True, text=True)
        print(f"\nPip version: {result.stdout.strip()}")
        return True
    except:
        print("\nFailed to get pip version")
        return False

def main():
    """Main execution"""
    print("Comprehensive Library Test")
    print("=" * 60)
    
    # Test pip version
    pip_ok = test_pip_version()
    
    # Test libraries
    lib_ok = test_libraries()
    
    print("\n" + "=" * 60)
    if pip_ok and lib_ok:
        print("SUCCESS: All systems ready!")
        print("Next: streamlit run llama32_vrm_app.py")
    else:
        print("ISSUES: Some problems detected")
        if not pip_ok:
            print("- Pip version issue")
        if not lib_ok:
            print("- Library import issues")

if __name__ == "__main__":
    main()
