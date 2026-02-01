# 🐳 AI Agent System Dockerデプロイガイド

## 🎯 目標

PCの電源を入れるだけで、モデルのダウンロードを待つことなく、即座に「最強の相棒」と対話できる環境を構築します。

---

## 📋 構成要素

### 1. Docker Compose環境
- **Ollama**: GPU対応、llama3.2とllama3.2-visionを自動プリロード
- **App**: Streamlit + FastAPI、Tailscaleネットワーク対応
- **VOICEVOX**: 音声合成エンジン、即座に話せる状態
- **Redis**: キャッシュとセッション管理

### 2. VRMモデル統合
- デスクトップVRMモデルの自動コピー
- デフォルトモデルのフォールバック
- コンテナ内での最適化配置

### 3. 常時待機モード
- PC起動時の自動起動
- モデルの事前ロード（VRAM展開）
- ウォームアップによる即応対応

---

## 🚀 クイックスタート

### 1. 環境準備
```cmd
# Docker Desktopのインストール
# https://www.docker.com/products/docker-desktop/

# NVIDIA Container Toolkitのインストール（GPU使用の場合）
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

# プロジェクトディレクトリへ移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui
```

### 2. 一括起動
```cmd
# Docker環境で起動
docker_startup.bat

# または手動で起動
docker-compose up -d --build
```

### 3. 自動起動設定
```cmd
# 管理者権限で実行
python setup_autostart.py
```

---

## 📁 ファイル構成

```
ai_agent_gui/
├── docker-compose.yml          # Docker Compose設定
├── Dockerfile                 # アプリケーションコンテナ
├── requirements-docker.txt     # Docker用Python依存
├── docker_startup.bat          # Windows起動スクリプト
├── setup_autostart.py         # 自動起動設定ツール
├── scripts/                  # 各種スクリプト
│   ├── setup_vrm.sh         # VRMモデルセットアップ
│   ├── preload_models.py     # モデルプリロード
│   └── start_services.sh    # サービス起動
├── assets/                   # リソースファイル
│   └── vrm/               # VRMモデル配置
└── logs/                     # ログファイル
```

---

## 🔧 詳細設定

### Docker Compose設定

#### Ollamaサービス
```yaml
ollama:
  image: ollama/ollama:latest
  container_name: ai-ollama
  restart: unless-stopped
  ports:
    - "11434:11434"
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - OLLAMA_HOST=0.0.0.0
    - OLLAMA_ORIGINS=*
```

#### アプリケーションサービス
```yaml
ai-app:
  build:
    context: .
    dockerfile: Dockerfile
  depends_on:
    ollama:
      condition: service_healthy
  environment:
    - OLLAMA_HOST=http://ollama:11434
    - OLLAMA_MODEL=llama3.2
```

### モデルプリロード

#### 自動ダウンロード
- llama3.2: テキスト生成用
- llama3.2-vision: 画像認識用
- 起動時に自動でプル

#### ウォームアップ
```python
# ダミー推論によるVRAM展開
warmup_prompts = [
    "こんにちは",
    "Hello, how are you?",
    "今日の天気は？"
]

for prompt in warmup_prompts:
    response = requests.post(
        f"{ollama_host}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
```

---

## 🌐 アクセス方法

### ローカルアクセス
- **Streamlit**: http://localhost:8501
- **Ollama API**: http://localhost:11434
- **VOICEVOX**: http://localhost:50021

### モバイルアクセス
- **Tailscale対応**: モバイルからもアクセス可能
- **同一ネットワーク**: スマートフォンからアクセス

---

## 🔄 自動起動設定

### Windowsタスクスケジューラ
```cmd
# タスク作成
schtasks /create /tn "AI Agent System Auto Start" /tr "docker_startup.bat" /sc onlogon

# タスク確認
schtasks /query /tn "AI Agent System Auto Start"

# タスク削除
schtasks /delete /tn "AI Agent System Auto Start"
```

### Docker Desktop設定
- 「Start Docker Desktop when you log in」を有効化
- PC起動時にDockerが自動で起動

---

## 📊 パフォーマンス最適化

### GPUリソース
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### メモリ管理
```yaml
volumes:
  ollama_data:
    driver: local
  redis_data:
    driver: local
```

### ネットワーク最適化
```yaml
networks:
  ai-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 🛠️ トラブルシューティング

### 起動問題
```cmd
# コンテナ状態確認
docker-compose ps

# ログ確認
docker-compose logs -f

# 再起動
docker-compose restart
```

### モデル問題
```cmd
# モデル確認
curl http://localhost:11434/api/tags

# 手動プル
curl -X POST http://localhost:11434/api/pull -d '{"name":"llama3.2"}'
```

### ネットワーク問題
```cmd
# ネットワーク確認
docker network ls
docker network inspect ai-agent_gui_ai-network

# 再作成
docker network rm ai-agent_gui_ai-network
docker-compose up -d
```

---

## 📈 監視とログ

### ヘルスチェック
```bash
# 各サービスの状態
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:8501           # Streamlit
curl http://localhost:50021/docs      # VOICEVOX
```

### ログファイル
- **Streamlit**: `/app/logs/streamlit.log`
- **Docker**: `docker-compose logs`
- **システム**: コンテナ内の標準出力

---

## 🎯 成功指標

### 起動時間
- **目標**: PC起動から5分以内に利用可能
- **現状**: モデルダウンロード待ちなし
- **改善**: プリロードによる即応

### 応答時間
- **目標**: 最初の応答3秒以内
- **現状**: ウォームアップ済みモデル
- **改善**: VRAMに展開済み

### 可用性
- **目標**: 99.9%以上の稼働率
- **現状**: コンテナ自動再起動
- **改善**: ヘルスチェック付き

---

## 🔄 アップデート方法

### イメージ更新
```cmd
# 最新イメージをプル
docker-compose pull

# 再ビルド
docker-compose build --no-cache

# 再起動
docker-compose up -d
```

### モデル更新
```cmd
# 新しいモデルのプル
curl -X POST http://localhost:11434/api/pull -d '{"name":"llama3.2:latest"}'

# 古いモデルの削除
docker exec ai-ollama ollama rm old-model
```

---

## 🎉 完成確認

### ✅ 自動起動テスト
1. PCを再起動
2. 5分待機
3. ブラウザで http://localhost:8501 にアクセス
4. 音声入力で対話テスト

### ✅ モデル即応テスト
1. アクセス直後に音声入力
2. 3秒以内の応答を確認
3. llama3.2-visionの動作確認

### ✅ モバイルアクセステスト
1. スマートフォンからアクセス
2. 音声入力機能の確認
3. VRMアバターの表示確認

---

**🎯 これでPC起動時に即座に利用可能なAI Agent Systemが完成しました！**
