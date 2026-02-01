# AI Agent System - 実装ガイド

## 🚀 ゼロから構築手順

### ステップ1: 環境構築 (15分)

#### 1.1 Python環境準備
```bash
# Python 3.10+ がインストール済みか確認
python --version

# 仮想環境作成
python -m venv ai_agent_env

# 環境有効化
# Windows
ai_agent_env\Scripts\activate
# macOS/Linux  
source ai_agent_env/bin/activate
```

#### 1.2 必須ライブラリ一括インストール
```bash
# requirements.txt 作成
cat > requirements.txt << 'EOF'
streamlit==1.28.1
langchain==0.1.0
langchain-community==0.0.4
langchain-ollama==0.1.1
langchain-experimental==0.4.1
openai-whisper==20231117
faster-whisper==0.9.0
pydub==0.25.1
sounddevice==0.4.6
numpy==1.24.3
opencv-python==4.8.1.78
Pillow==10.4.0
python-dotenv==1.0.0
requests==2.32.5
beautifulsoup4==4.12.2
selenium==4.15.2
pyautogui==0.9.54
pynput==1.7.6
openpyxl==3.1.2
PyMuPDF==1.23.8
sentence-transformers==2.2.2
faiss-cpu==1.7.4
qrcode[pil]==7.4.2
fastapi==0.128.0
uvicorn==0.40.0
pyttsx3==2.99
pandas==2.1.0
torch==2.1.0
librosa==0.10.1
scipy==1.11.4
matplotlib==3.7.2
plotly==5.17.0
tiktoken==0.7.0
chromadb==0.4.22
transformers==4.36.0
pygame==2.5.2
psutil==5.9.6
EOF

# 一括インストール
pip install -r requirements.txt
```

#### 1.3 Ollamaインストール
```bash
# Windows (winget)
winget install Ollama.Ollama

# macOS (Homebrew)
brew install ollama

# Linux (curl)
curl -fsSL https://ollama.com/install.sh | sh

# Ollamaサービス起動
ollama serve
```

#### 1.4 PHPインストール
```bash
# Windows (winget)
winget install PHP.PHP.8.4

# macOS (Homebrew)
brew install php

# Linux (apt)
sudo apt update && sudo apt install php-cli

# インストール確認
php --version
```

### ステップ2: モデル準備 (10分)

#### 2.1 LLMモデルダウンロード
```bash
# メインモデル (4.9GB)
ollama pull llama3.1:8b

# 埋め込み用モデル (274MB)
ollama pull nomic-embed-text:latest

# 確認
ollama list
```

#### 2.2 VRMアバター準備
```bash
# staticディレクトリ作成
mkdir -p static

# VRMファイル配置 (既存ファイルをコピー)
# copy path/to/avatar.vrm static/avatar.vrm
```

### ステップ3: プロジェクト構築 (30分)

#### 3.1 基本ファイル作成
```bash
# メインアプリケーション
touch app.py

# 設定ファイル
touch .env
touch memory_db.json

# ディレクトリ構成
mkdir -p knowledge_base/documents
mkdir -p logs
mkdir -p temp
mkdir -p backups
```

#### 3.2 コアモジュール実装
```python
# 1. app.py 基本構造
import streamlit as st
import os
import json
from datetime import datetime

# 基本設定
st.set_page_config(
    page_title="AI Agent System",
    page_icon="🤖",
    layout="wide"
)

# メイン関数
def main():
    st.title("🤖 AI Agent System")
    st.write("システム構築中...")

if __name__ == "__main__":
    main()
```

#### 3.3 基本動作テスト
```bash
# 起動テスト
streamlit run app.py

# エラー確認
# ブラウザで http://localhost:8501 にアクセス
```

### ステップ4: AI機能実装 (60分)

#### 4.1 Ollama連携
```python
# ollama_integration.py
import ollama

class OllamaManager:
    def __init__(self):
        self.client = ollama.Client()
        self.model = "llama3.1:8b"
    
    def generate_response(self, prompt: str) -> str:
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "max_tokens": 4096
            }
        )
        return response['response']
```

#### 4.2 音声処理
```python
# voice_processor.py
import faster_whisper
import pyttsx3

class VoiceProcessor:
    def __init__(self):
        self.whisper_model = faster_whisper.WhisperModel("base")
        self.tts_engine = pyttsx3.init()
    
    def speech_to_text(self, audio_file: str) -> str:
        result = self.whisper_model.transcribe(audio_file)
        return result["text"]
    
    def text_to_speech(self, text: str):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
```

#### 4.3 人格システム
```python
# personality_manager.py
from enum import Enum

class Personality(Enum):
    FRIEND = "friend"
    COPY = "copy" 
    EXPERT = "expert"

class PersonalityManager:
    def __init__(self):
        self.current = Personality.FRIEND
        self.traits = {
            Personality.FRIEND: {
                "name": "親友エンジニア",
                "vrm_expression": "happy",
                "voice": "normal",
                "theme": {"primary": "#4CAF50"}
            },
            Personality.COPY: {
                "name": "分身",
                "vrm_expression": "joy", 
                "voice": "similar",
                "theme": {"primary": "#2196F3"}
            },
            Personality.EXPERT: {
                "name": "エキスパート",
                "vrm_expression": "neutral",
                "voice": "professional", 
                "theme": {"primary": "#9C27B0"}
            }
        }
```

### ステップ5: 高度機能実装 (45分)

#### 5.1 知識検索システム
```python
# knowledge_system.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class KnowledgeSystem:
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)
        self.documents = []
    
    def add_document(self, text: str, metadata: dict):
        # チャンク分割
        chunks = self.chunk_text(text)
        
        # 埋め込み生成
        embeddings = self.encoder.encode(chunks)
        
        # インデックス追加
        for i, embedding in enumerate(embeddings):
            self.index.add(np.array([embedding]))
            self.documents.append({
                "text": chunks[i],
                "metadata": metadata
            })
    
    def search(self, query: str, top_k: int = 5):
        query_embedding = self.encoder.encode([query])
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            results.append({
                "document": self.documents[idx],
                "score": float(1 / (1 + distance))
            })
        
        return results
```

#### 5.2 検証プロトコル
```python
# verification_protocols.py
import ast
import subprocess
import tempfile

class VerificationProtocols:
    def __init__(self):
        self.max_iterations = 3
    
    def verify_code(self, code: str, language: str = "python"):
        current_code = code
        
        for iteration in range(self.max_iterations):
            # 静的解析
            try:
                ast.parse(current_code)
            except SyntaxError as e:
                current_code = self.fix_syntax_error(current_code, str(e))
                continue
            
            # 実行テスト
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(current_code)
                temp_file = f.name
            
            result = subprocess.run(['python', temp_file], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "final_code": current_code,
                    "iterations": iteration + 1,
                    "output": result.stdout
                }
            
            # エラー修正
            current_code = self.fix_runtime_error(current_code, result.stderr)
        
        return {
            "success": False,
            "final_code": current_code,
            "iterations": self.max_iterations,
            "errors": ["最大反復回数到達"]
        }
```

### ステップ6: UI実装 (30分)

#### 6.1 Streamlitレイアウト
```python
# app.py UI実装
def main():
    # サイドバー
    with st.sidebar:
        st.header("🤖 AI Agent Control")
        
        # 人格選択
        personality = st.selectbox(
            "人格選択",
            ["親友エンジニア", "分身", "エキスパート"],
            key="personality"
        )
        
        # 診断ボタン
        if st.button("🔍 起動時診断"):
            run_startup_diagnostic()
        
        if st.button("🔧 コード検証テスト"):
            test_code_verification()
    
    # メインエリア
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 チャット")
        # チャットインターフェース実装
        
    with col2:
        st.header("🤖 VRMアバター")
        # VRM表示実装
```

#### 6.2 Web Canvasプレビュー
```python
# web_canvas.py
def render_web_canvas():
    st.subheader("🎨 Web Canvas Preview")
    
    # エディタとプレビュー
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # コードエディタ
        html_code = st.text_area("HTML", height=300, key="html")
        css_code = st.text_area("CSS", height=300, key="css") 
        js_code = st.text_area("JavaScript", height=300, key="js")
    
    with col2:
        # ライブプレビュー
        if st.button("🔄 プレビュー更新"):
            update_preview(html_code, css_code, js_code)
        
        st.components.v1.iframe(
            src="http://localhost:8001/preview",
            height=600,
            width=400
        )
```

### ステップ7: 統合テスト (20分)

#### 7.1 機能テスト
```python
# test_integration.py
import unittest

class TestAIIntegration(unittest.TestCase):
    def test_ollama_connection(self):
        # Ollama接続テスト
        pass
    
    def test_voice_processing(self):
        # 音声処理テスト
        pass
    
    def test_personality_switch(self):
        # 人格切り替えテスト
        pass
    
    def test_knowledge_search(self):
        # 知識検索テスト
        pass
    
    def test_code_verification(self):
        # コード検証テスト
        pass

if __name__ == "__main__":
    unittest.main()
```

#### 7.2 パフォーマンステスト
```python
# performance_test.py
import time
import psutil

def measure_response_time():
    start_time = time.time()
    # LLM推論テスト
    end_time = time.time()
    return end_time - start_time

def measure_memory_usage():
    return psutil.virtual_memory().percent

def run_performance_suite():
    tests = [
        ("LLM応答時間", measure_response_time),
        ("メモリ使用率", measure_memory_usage),
        ("音声認識速度", measure_speech_processing),
        ("知識検索速度", measure_search_performance)
    ]
    
    for test_name, test_func in tests:
        result = test_func()
        print(f"{test_name}: {result}")
```

### ステップ8: 本番デプロイ (15分)

#### 8.1 本番環境設定
```bash
# 本番用設定ファイル
cat > .env.production << 'EOF'
ENVIRONMENT=production
OLLAMA_MODEL=llama3.1:8b
LOG_LEVEL=INFO
MAX_CONCURRENT_USERS=10
EOF

# 本番起動スクリプト
cat > start_production.py << 'EOF'
import uvicorn
from app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info"
    )
EOF
```

#### 8.2 サービス化
```bash
# Windowsサービス
# sc create AI-Agent binPath=python start= start_production.py

# Linux systemd
sudo tee /etc/systemd/ai-agent.service > /dev/null <<EOF
[Unit]
Description=AI Agent Service
After=network.target

[Service]
Type=simple
User=ai-agent
WorkingDirectory=/path/to/ai-agent
ExecStart=/path/to/ai-agent/venv/bin/python start_production.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ai-agent
sudo systemctl start ai-agent
```

---

## 🎯 完成チェックリスト

### ✅ 基本機能
- [ ] Python 3.10+ 環境
- [ ] 必須ライブラリ全てインストール済み
- [ ] Ollama llama3.1:8b モデル利用可能
- [ ] PHP 8.5+ 実行環境
- [ ] Streamlit UI 起動
- [ ] FastAPI バックエンド起動

### ✅ AI機能
- [ ] LLM推論機能
- [ ] 音声認識機能
- [ ] 音声合成機能
- [ ] 3人格切り替え機能
- [ ] 知識検索機能
- [ ] コード自動検証機能

### ✅ 高度機能
- [ ] VRMアバター表示
- [ ] Web Canvasプレビュー
- [ ] 起動時自己診断
- [ ] Excel/PDF解析機能
- [ ] RAG検索機能
- [ ] パーソナライズ機能

### ✅ 品質保証
- [ ] 単体テスト実施
- [ ] 統合テスト実施
- [ ] パフォーマンス測定
- [ ] エラーハンドリング実装
- [ ] ログ出力実装
- [ ] セキュリティ対策実装

---

## 🚨 トラブルシューティング

### よくある問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|--------|
| `ImportError` | ライブラリ未インストール | `pip install [ライブラリ]` |
| `Ollama接続エラー` | サービス未起動 | `ollama serve` 実行 |
| `音声認識されない` | マイク未許可 | OSのマイク設定確認 |
| `VRM表示されない` | ファイルパス間違い | `./static/avatar.vrm` 確認 |
| `メモリ不足` | 大容量モデル | llama3.1:8b 使用 |
| `PHP実行エラー` | PATH未設定 | 環境変数PATH確認 |

---

## 📞 サポート

### 📧 技術サポート
- **ドキュメント**: 各モジュールdocstring参照
- **エラーログ**: `./logs/` ディレクトリ確認
- **デバッグモード**: `DEBUG=True` 環境変数設定

### 🔧 開発ツール
- **IDE**: VS Code + Python拡張機能
- **バージョン管理**: Git + GitHub
- **テスト**: pytest + unittest
- **デバッグ**: pdb + logging

---

*このガイドに従うことで、約3時間で完全なAIエージェントシステムを構築できます。*
