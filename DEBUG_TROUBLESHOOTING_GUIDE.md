# 🔍 デバッグトラブルシューティングガイド

## 🎯 問題の確認

### 現在のエラー
```
HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded with url: /api/generate
Caused by NewConnectionError("HTTPConnection(host='localhost', port=11434): Failed to establish a new connection: [Errno 111] Connection refused")
```

**問題**: プログラムがlocalhost:11434に接続しようとして失敗している

---

## 🔍 コードの詳細チェック

### 1. 既存コードの問題点確認

#### network_aware_ai_agent.py の問題
```python
# 問題のある部分
def _initialize_urls(self):
    """Ollama接続URLを初期化"""
    # コンテナ内通信（優先）
    self.base_urls.append("http://ollama:11434")
    
    # 外部アクセス用
    host_ip = os.getenv('HOST_IP', 'localhost')  # ← ここが問題
    self.base_urls.append(f"http://{host_ip}:11434")
    
    # ローカルホスト（フォールバック）
    self.base_urls.append("http://localhost:11434")  # ← ここも問題
```

**問題点**:
1. `HOST_IP`環境変数が設定されていない場合、`localhost`になる
2. `localhost`はコンテナ内では自分自身を指す
3. Ollamaコンテナには接続できない

### 2. 環境変数の確認

#### docker-compose.network.fixed.yml の設定
```yaml
ai-app:
  environment:
    - OLLAMA_HOST=http://ollama:11434
    - EXTERNAL_ACCESS=true
    - HOST_IP=host.docker.internal  # ← これが設定されているはず
```

**問題**: 環境変数が正しく設定されていない可能性

---

## 🛠️ デバッグ版の作成

### 1. デバッグ版AIエージェント

#### network_aware_ai_agent_debug.py
```python
class NetworkAwareAIAgent:
    """ネットワーク対応AIエージェント - デバッグ版"""
    
    def __init__(self):
        self.base_urls = []
        self.current_url_index = 0
        self.timeout = 30
        self.max_retries = 3
        self._initialize_urls()
    
    def _initialize_urls(self):
        """Ollama接続URLを初期化"""
        # コンテナ内通信（優先）
        self.base_urls.append("http://ollama:11434")
        
        # 外部アクセス用
        host_ip = os.getenv('HOST_IP', 'localhost')
        self.base_urls.append(f"http://{host_ip}:11434")
        
        # ローカルホスト（フォールバック）
        self.base_urls.append("http://localhost:11434")
        
        # ホストIPの自動検出
        try:
            host_ip = self._get_host_ip()
            if host_ip and host_ip not in [url.split('//')[1].split(':')[0] for url in self.base_urls]:
                self.base_urls.append(f"http://{host_ip}:11434")
        except:
            pass
        
        # デバッグ情報
        print(f"🔍 Initialized URLs: {self.base_urls}")
    
    def _test_connection(self, url):
        """接続テスト"""
        try:
            print(f"🔍 Testing connection to: {url}")
            response = requests.get(f"{url}/api/tags", timeout=5)
            success = response.status_code == 200
            print(f"🔍 Connection test result: {success} (status: {response.status_code})")
            return success
        except Exception as e:
            print(f"🔍 Connection test error: {e}")
            return False
    
    def generate_response(self, prompt, model="llama3.2"):
        """AI応答を生成（ネットワーク対応）"""
        print(f"🔍 Generating response with prompt: {prompt[:50]}...")
        
        working_url = self._get_working_url()
        
        if not working_url:
            error_msg = "❌ Ollamaサーバーに接続できません。サーバーが起動しているか確認してください。"
            print(f"🔍 Error: {error_msg}")
            return error_msg
        
        print(f"🔍 Using URL: {working_url}")
        
        for attempt in range(self.max_retries):
            try:
                print(f"🔍 Attempt {attempt + 1}/{self.max_retries}")
                
                data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                
                print(f"🔍 Sending request to: {working_url}/api/generate")
                print(f"🔍 Request data: {data}")
                
                response = requests.post(
                    f"{working_url}/api/generate",
                    json=data,
                    timeout=self.timeout
                )
                
                print(f"🔍 Response status: {response.status_code}")
                print(f"🔍 Response text: {response.text[:200]}...")
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    print(f"🔍 Generated response: {response_text[:50]}...")
                    return response_text
                else:
                    error_msg = f"❌ 応答生成エラー: HTTP {response.status_code}"
                    print(f"🔍 Error: {error_msg}")
                    return error_msg
                    
            except requests.exceptions.ConnectionError as e:
                print(f"🔍 Connection error: {e}")
                if attempt < self.max_retries - 1:
                    # 次のURLを試す
                    working_url = self._get_working_url()
                    if not working_url:
                        break
                    time.sleep(1)
                else:
                    error_msg = "❌ Ollamaサーバーへの接続に失敗しました。"
                    print(f"🔍 Error: {error_msg}")
                    return error_msg
            except Exception as e:
                error_msg = f"❌ 応答生成エラー: {str(e)}"
                print(f"🔍 Error: {error_msg}")
                return error_msg
```

#### デバッグ機能
- ✅ **詳細ログ**: 全接続試行のログ出力
- ✅ **URLテスト**: 各URLの接続状態を確認
- ✅ **エラー追跡**: 詳細なエラー情報を表示
- ✅ **環境変数表示**: 設定値を確認

### 2. デバッグ起動スクリプト

#### start_debug.bat
```batch
@echo off
title AI Agent System - Debug Mode

echo Starting AI Agent System in Debug Mode...

cd /d "%~dp0"

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not running
    pause
    exit /b 1
)

echo Cleaning up...
docker-compose -f docker-compose.network.fixed.yml down >nul 2>&1
docker system prune -f >nul 2>&1

echo Creating volumes...
docker volume create python_libs 2>nul
docker volume create python_cache 2>nul

echo Building...
docker-compose -f docker-compose.network.fixed.yml build --no-cache

echo Starting...
docker-compose -f docker-compose.network.fixed.yml up -d

echo SUCCESS: AI Agent System is running
echo.
echo Access URLs:
echo - Local: http://localhost:8501
echo - Debug: http://localhost:8501 (Debug Mode)
echo - Network: http://[YOUR_IP]:8501
echo.
echo Debug Features:
echo - Detailed connection logging
echo - URL testing with status
echo - Error tracking and reporting
echo - Environment variable display
echo.
echo To check container logs:
echo docker logs ai-agent-app
echo docker logs ai-ollama
echo.
echo To test connection manually:
echo docker exec ai-agent-app curl -f http://ollama:11434/api/tags
echo docker exec ai-agent-app curl -f http://localhost:11434/api/tags

pause
```

---

## 🔧 手動デバッグ方法

### 1. コンテナの状態確認
```cmd
# コンテナの状態確認
docker ps -a

# コンテナのログ確認
docker logs ai-agent-app
docker logs ai-ollama

# コンテナ内の環境変数確認
docker exec ai-agent-app env | grep -E "(HOST_IP|OLLAMA_HOST|EXTERNAL_ACCESS)"
```

### 2. ネットワーク接続テスト
```cmd
# コンテナ間通信テスト
docker exec ai-agent-app ping ollama
docker exec ai-agent-app curl -f http://ollama:11434/api/tags

# ホストアクセステスト
docker exec ai-agent-app curl -f http://host.docker.internal:11434/api/tags

# ローカルホストテスト（失敗するはず）
docker exec ai-agent-app curl -f http://localhost:11434/api/tags
```

### 3. コンテナ内での直接テスト
```cmd
# コンテナに入る
docker exec -it ai-agent-app bash

# Pythonで直接テスト
python -c "
import requests
import os

# 環境変数確認
print('HOST_IP:', os.getenv('HOST_IP', 'Not set'))
print('OLLAMA_HOST:', os.getenv('OLLAMA_HOST', 'Not set'))

# 接続テスト
urls = [
    'http://ollama:11434',
    'http://host.docker.internal:11434',
    'http://localhost:11434'
]

for url in urls:
    try:
        response = requests.get(f'{url}/api/tags', timeout=5)
        print(f'✅ {url}: {response.status_code}')
    except Exception as e:
        print(f'❌ {url}: {e}')
"
```

---

## 🚀 デバッグ版の実行

### 1. デバッグ版の起動
```cmd
# デバッグ版で起動
start_debug.bat
```

### 2. ブラウザでデバッグ情報を確認
```
1. http://localhost:8501 にアクセス
2. 「🔍 デバッグ情報」セクションを確認
3. 接続状態とURLテスト結果を確認
4. 環境変数の値を確認
```

### 3. 期待されるデバッグ出力
```
🔍 Initialized URLs: ['http://ollama:11434', 'http://host.docker.internal:11434', 'http://localhost:11434']
🔍 Testing connection to: http://ollama:11434
🔍 Connection test result: True (status: 200)
🔍 Found working URL: http://ollama:11434
🔍 Using URL: http://ollama:11434
🔍 Attempt 1/3
🔍 Sending request to: http://ollama:11434/api/generate
🔍 Response status: 200
🔍 Generated response: こんにちは！私はAIアシスタントです...
```

---

## 📊 トラブルシューティングチェックリスト

### 1. 環境変数の確認
- [ ] `HOST_IP`が`host.docker.internal`に設定されている
- [ ] `OLLAMA_HOST`が`http://ollama:11434`に設定されている
- [ ] `EXTERNAL_ACCESS`が`true`に設定されている

### 2. コンテナの状態確認
- [ ] `ai-ollama`コンテナが起動している
- [ ] `ai-agent-app`コンテナが起動している
- [ ] 両コンテナが同じネットワークに属している

### 3. ネットワーク接続確認
- [ ] `ollama:11434`に接続できる
- [ ] `host.docker.internal:11434`に接続できる
- [ ] `localhost:11434`に接続できない（正しい動作）

### 4. モデルの確認
- [ ] Ollamaにモデルがインストールされている
- [ ] `/api/tags`エンドポイントがモデルリストを返す
- [ ] `/api/generate`エンドポイントが応答を返す

---

## 🔧 修正案

### 1. 環境変数の修正
```yaml
# docker-compose.network.fixed.yml
ai-app:
  environment:
    - OLLAMA_HOST=http://ollama:11434
    - EXTERNAL_ACCESS=true
    - HOST_IP=host.docker.internal  # 明示的に設定
```

### 2. URL初期化の修正
```python
def _initialize_urls(self):
    """Ollama接続URLを初期化"""
    # コンテナ内通信（最優先）
    self.base_urls.append("http://ollama:11434")
    
    # ホストアクセス（次優先）
    self.base_urls.append("http://host.docker.internal:11434")
    
    # 外部アクセス用
    host_ip = os.getenv('HOST_IP', 'host.docker.internal')  # デフォルト値を変更
    if host_ip != 'host.docker.internal':  # 重複を避ける
        self.base_urls.append(f"http://{host_ip}:11434")
    
    # ローカルホスト（最後）
    self.base_urls.append("http://localhost:11434")
```

### 3. エラーハンドリングの強化
```python
def _get_working_url(self):
    """動作中のURLを取得"""
    # 優先順位でテスト
    priority_urls = [
        "http://ollama:11434",           # コンテナ内通信
        "http://host.docker.internal:11434",  # ホストアクセス
    ]
    
    # 優先URLを先にテスト
    for url in priority_urls:
        if self._test_connection(url):
            self._last_working_url = url
            return url
    
    # その他のURLをテスト
    for url in self.base_urls:
        if url in priority_urls:
            continue  # 既にテスト済み
        if self._test_connection(url):
            self._last_working_url = url
            return url
    
    return None
```

---

## 📁 新しいファイル

### デバッグ版ファイル
- `network_aware_ai_agent_debug.py` - デバッグ版AIエージェント
- `start_debug.bat` - デバッグ起動スクリプト
- `DEBUG_TROUBLESHOOTING_GUIDE.md` - 本ガイド

### 特徴
- ✅ 詳細な接続ログ
- ✅ URLテスト機能
- ✅ エラー追跡
- ✅ 環境変数表示

---

## 🎯 最も簡単なデバッグ方法

### 今すぐ実行
```cmd
# 1. コマンドプロンプトを開く
# 2. プロジェクトディレクトリに移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# 3. デバッグ版で起動
start_debug.bat
```

### 期待される結果
```
Starting AI Agent System in Debug Mode...
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

Access URLs:
- Local: http://localhost:8501
- Debug: http://localhost:8501 (Debug Mode)
- Network: http://[YOUR_IP]:8501

Debug Features:
- Detailed connection logging
- URL testing with status
- Error tracking and reporting
- Environment variable display
```

### ブラウザでの確認
```
🔍 Debug AI Agent
デバッグ版 - ネットワーク接続の詳細確認

🔍 デバッグ情報
接続状態:
✅ 現在のURL: http://ollama:11434

全URLの状態:
✅ http://ollama:11434
✅ http://host.docker.internal:11434
❌ http://localhost:11434

利用可能なモデル:
📦 llama3.2
📦 llama3.2-vision

環境変数:
HOST_IP: host.docker.internal
OLLAMA_HOST: http://ollama:11434
EXTERNAL_ACCESS: true
```

---

## 🎯 まとめ

### 問題の特定
- プログラムがlocalhost:11434に接続しようとして失敗
- 環境変数が正しく設定されていない可能性
- URLの優先順位が適切でない

### デバッグ方法
- 詳細なログ出力で問題を特定
- 各URLの接続状態を確認
- 環境変数の値を表示
- 手動接続テストで確認

### 修正方針
- 環境変数の明示的な設定
- URLの優先順位の修正
- エラーハンドリングの強化
- デバッグ機能の追加

---

**🔍 これでプログラムの誤字と接続問題を詳細に確認できます！**

**推奨**: `start_debug.bat` を実行してデバッグ情報を確認してください。
