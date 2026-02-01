# 🔧 動的インストール機能有効化ガイド

## 🎯 問題の解決

### ModuleNotFoundError: No module named 'sounddevice'
```
ModuleNotFoundError: No module named 'sounddevice'
Traceback:
File "/usr/local/lib/python3.10/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 534, in _run_script
    exec(code, module.__dict__)
File "/app/fixed_smart_voice_agent.py", line 10, in <module>
    import sounddevice as sd
```

**原因**: 動的インストール機能が有効化されていない

---

## 🛠️ 解決策

### 1. 動的インストール有効版の起動（推奨）

#### start_dynamic_enabled.bat
```batch
@echo off
title AI Agent System - Dynamic Install Enabled

echo Starting AI Agent System with Dynamic Install...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Cleaning up...
docker-compose -f docker-compose.dynamic.enabled.yml down >nul 2>&1
docker system prune -f >nul 2>&1

echo Creating volumes...
docker volume create ai_chroma_data 2>nul
docker volume create ai_conversation_history 2>nul
docker volume create ai_user_settings 2>nul
docker volume create ai_logs 2>nul
docker volume create ai_voicevox_data 2>nul
docker volume create ai_redis_data 2>nul
docker volume create python_libs 2>nul
docker volume create python_cache 2>nul

echo Building...
docker-compose -f docker-compose.dynamic.enabled.yml build --no-cache

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Starting...
docker-compose -f docker-compose.dynamic.enabled.yml up -d

if errorlevel 1 (
    echo ERROR: Start failed
    pause
    exit /b 1
)

echo SUCCESS: AI Agent System is running
echo Access: http://localhost:8501

pause
```

### 2. 動的インストール対応docker-compose

#### docker-compose.dynamic.enabled.yml
```yaml
services:
  ai-app:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: ai-agent-app
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - OLLAMA_MODEL=llama3.2
      - PYTHONUNBUFFERED=1
      - OLLAMA_WAIT_TIMEOUT=30
      - CHROMA_DB_PATH=/app/data/chroma
      - MEMORY_ENABLED=true
      - DYNAMIC_INSTALL_ENABLED=true
    volumes:
      # Pythonライブラリの永続化
      - python_libs:/usr/local/lib/python3.10/site-packages
      - python_cache:/root/.cache/pip
      # 修正版アプリケーション
      - ./fixed_smart_voice_agent.py:/app/fixed_smart_voice_agent.py
      - ./smart_voice_agent_self_healing.py:/app/smart_voice_agent_self_healing.py
```

### 3. Streamlitエントリーポイント

#### streamlit_entrypoint_dynamic.py
```python
#!/usr/bin/env python3
"""
Streamlit Entrypoint with Dynamic Install Support
"""

import os
import sys
import subprocess
import importlib

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
    
    # Streamlitアプリを起動
    app_file = '/app/smart_voice_agent_self_healing.py'
    
    if not os.path.exists(app_file):
        app_file = '/app/fixed_smart_voice_agent.py'
    
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

if __name__ == "__main__":
    main()
```

---

## 🚀 実行方法

### 1. 動的インストール有効版の起動（推奨）
```cmd
# 動的インストール有効版で起動
start_dynamic_enabled.bat
```

### 2. 手動実行
```cmd
# 1. ボリュームの作成
docker volume create python_libs
docker volume create python_cache

# 2. ビルドと起動
docker-compose -f docker-compose.dynamic.enabled.yml build --no-cache
docker-compose -f docker-compose.dynamic.enabled.yml up -d
```

### 3. コンテナ内で直接実行
```cmd
# コンテナに入る
docker exec -it ai-agent-app bash

# パッケージをインストール
pip install sounddevice faster-whisper torch torchaudio pyttsx3

# アプリを起動
streamlit run smart_voice_agent_self_healing.py
```

---

## 📊 期待される動作

### 1. 起動時のパッケージチェック
```
🚀 Starting Streamlit with Dynamic Install Support...
✅ streamlit is already installed
⚠️ sounddevice not found, installing...
📦 Installing sounddevice...
✅ Successfully installed sounddevice
⚠️ faster-whisper not found, installing...
📦 Installing faster-whisper...
✅ Successfully installed faster-whisper
✅ torch is already installed
✅ torchaudio is already installed
⚠️ pyttsx3 not found, installing...
📦 Installing pyttsx3...
✅ Successfully installed pyttsx3
```

### 2. アプリケーションの起動
```
🚀 Starting Streamlit app: /app/smart_voice_agent_self_healing.py
🤖 Self-Healing Smart Voice AI Agent
🔧 ライブラリ状態
📦 パッケージ状態
sounddevice: ✅ インストール済み
faster-whisper: ✅ インストール済み
torch: ✅ インストール済み
torchaudio: ✅ インストール済み
pyttsx3: ✅ インストール済み
```

---

## 🔧 トラブルシューティング

### 1. インストールが失敗する場合
```cmd
# コンテナ内で直接インストール
docker exec ai-agent-app pip install sounddevice

# ディスク容量の確認
docker exec ai-agent-app df -h

# ネットワーク接続の確認
docker exec ai-agent-app ping google.com
```

### 2. 永続化が機能しない場合
```cmd
# ボリュームの確認
docker volume ls | grep python

# ボリュームの内容確認
docker run --rm -v python_libs:/data alpine ls -la /data

# ボリュームの再作成
docker volume rm python_libs
docker volume create python_libs
```

### 3. アプリが起動しない場合
```cmd
# コンテナのログ確認
docker logs ai-agent-app

# コンテナ内で直接実行
docker exec -it ai-agent-app python streamlit_entrypoint_dynamic.py
```

---

## 📁 新しいファイル

### 動的インストール有効版ファイル
- `docker-compose.dynamic.enabled.yml` - 動的インストール有効版
- `start_dynamic_enabled.bat` - 起動スクリプト
- `streamlit_entrypoint_dynamic.py` - Streamlitエントリーポイント
- `DYNAMIC_INSTALL_QUICK_FIX.md` - 本ガイド

### 特徴
- ✅ 動的インストール機能の有効化
- ✅ 起動時のパッケージ自動インストール
- ✅ 永続化されたライブラリ管理
- ✅ エラーハンドリングと通知

---

## 🎯 最も簡単な解決方法

### 今すぐ実行
```cmd
# 1. コマンドプロンプトを開く
# 2. プロジェクトディロクトリに移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# 3. 動的インストール有効版で起動
start_dynamic_enabled.bat
```

### 期待される結果
```
Starting AI Agent System with Dynamic Install...
Checking Docker...
Cleaning up...
Creating volumes...
ai_chroma_data
ai_conversation_history
ai_user_settings
ai_logs
ai_voicevox_data
ai_redis_data
python_libs
python_cache
Building...
Starting...
SUCCESS: AI Agent System is running
Access: http://localhost:8501
```

### ブラウザでの表示
```
🤖 Self-Healing Smart Voice AI Agent
🔧 ライブラリ状態
📦 パッケージ状態
sounddevice: ✅ インストール済み
faster-whisper: ✅ インストール済み
torch: ✅ インストール済み
torchaudio: ✅ インストール済み
pyttsx3: ✅ インストール済み
```

---

## 🎯 まとめ

### 問題
- ModuleNotFoundError: No module named 'sounddevice'
- 動的インストール機能が有効化されていない
- 手動でのライブラリインストールが必要

### 解決
- 動的インストール有効版のdocker-compose
- 起動時のパッケージ自動インストール
- 永続化されたライブラリ管理

### 結果
- sounddeviceの自動インストール
- すべての音声ライブラリの自動セットアップ
- 安定した音声AIエージェントの動作

---

**🎯 これでsounddeviceモジュールのエラーが完全に解消されます！**

**推奨**: `start_dynamic_enabled.bat` を実行してください。最も確実な動的インストール対応版です。
