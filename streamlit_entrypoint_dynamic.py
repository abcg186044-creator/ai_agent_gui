#!/usr/bin/env python3
"""
Streamlit Entrypoint with Dynamic Install Support
"""

import os
import sys
import subprocess
import importlib
import time

def install_package(package_name):
    """パッケージをインストール"""
    try:
        print(f"📦 Installing {package_name}...")
        result = subprocess.run(
            ["pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully installed {package_name}")
            # キャッシュを無効化
            importlib.invalidate_caches()
            return True
        else:
            print(f"❌ Failed to install {package_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Installation error for {package_name}: {str(e)}")
        return False

def check_and_install_packages():
    """必要なパッケージをチェック・インストール"""
    required_packages = [
        'sounddevice',
        'faster-whisper',
        'torch',
        'torchaudio',
        'pyttsx3'
    ]
    
    failed_packages = []
    
    for package in required_packages:
        try:
            import_name = package.replace('-', '_')
            importlib.import_module(import_name)
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"⚠️ {package} not found, installing...")
            if not install_package(package):
                failed_packages.append(package)
    
    if failed_packages:
        print(f"❌ Failed to install: {failed_packages}")
        return False
    
    return True

def main():
    """メイン処理"""
    print("🚀 Starting Streamlit with Dynamic Install Support...")
    
    # 必要なパッケージをチェック・インストール
    if not check_and_install_packages():
        print("❌ Failed to install required packages")
        sys.exit(1)
    
    # 環境変数を設定
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DYNAMIC_INSTALL_ENABLED'] = 'true'
    
    # Streamlitアプリを起動
    app_file = '/app/smart_voice_agent_self_healing.py'
    
    if not os.path.exists(app_file):
        app_file = '/app/fixed_smart_voice_agent.py'
    
    if not os.path.exists(app_file):
        print("❌ No Streamlit app found")
        sys.exit(1)
    
    print(f"🚀 Starting Streamlit app: {app_file}")
    
    # Streamlitを起動
    cmd = [
        'streamlit', 'run', app_file,
        '--server.port=8501',
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--browser.gatherUsageStats=false'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Streamlit stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
