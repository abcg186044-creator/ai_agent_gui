# 🔧 Docker Ollama Unhealthy 問題解決ガイド

## 🎯 問題の概要

`ai-ollama` コンテナが `unhealthy` 状態になり、`dependency failed to start` エラーが発生する問題を解決します。

---

## 🔍 問題の根本原因

### 1. ヘルスチェックのタイムアウト
- **問題**: Ollamaの起動に時間がかかりすぎる
- **原因**: モデルの読み込みやGPU初期化に時間が必要
- **解決**: ヘルスチェックの猶予時間を延長

### 2. GPU設定の問題
- **問題**: NVIDIA GPUが正しく認識されない
- **原因**: ドライバー不足や設定ミス
- **解決**: GPU設定の見直しとCPU版の用意

### 3. モデルダウンロードのタイムアウト
- **問題**: モデルのダウンロードが完了しない
- **原因**: ネットワーク問題やディスク容量不足
- **解決**: バックグラウンドダウンロードと手動管理

---

## 🛠️ 解決策

### 1. ヘルスチェックの改善

#### docker-compose.fixed.yml
```yaml
services:
  ollama:
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:11434/api/tags || exit 1"]
      interval: 30s        # チェック間隔
      timeout: 30s         # タイムアウト
      retries: 10          # リトライ回数
      start_period: 60s    # 起動猶予時間
```

#### 改善点
- ✅ **retries**: 3→10に増加
- ✅ **timeout**: 10s→30sに延長
- ✅ **start_period**: 40s→60sに延長

### 2. GPU設定の最適化

#### docker-compose.gpu.yml
```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all      # 全てのGPUを使用
              capabilities: [gpu]
```

#### 改善点
- ✅ **count**: 1→allに変更
- ✅ **CPU版**: GPUなし環境用の準備

### 3. エントリーポイントの強化

#### scripts/ollama_entrypoint.sh
```bash
# 起動前の猶予
sleep 10

# ヘルスチェックループ
MAX_RETRIES=30
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollamaサーバーが正常に起動しました"
        break
    fi
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done
```

#### 改善点
- ✅ **起動猶予**: 10秒の待機時間
- ✅ **ヘルスチェック**: 30回のリトライ
- ✅ **詳細ログ**: 進捗状況の表示

---

## 🚀 起動方法

### 1. 自動起動（推奨）
```cmd
# GPU/CPU自動判定で起動
docker_fixed_start.bat
```

### 2. 手動起動
```cmd
# GPU版
docker-compose -f docker-compose.gpu.yml up -d

# CPU版
docker-compose -f docker-compose.fixed.yml up -d
```

---

## 🔍 デバッグ手順

### 1. コンテナ状態の確認
```cmd
# コンテナ一覧
docker-compose -f docker-compose.fixed.yml ps

# 詳細情報
docker inspect ai-ollama
```

### 2. ログの確認
```cmd
# 基本ログ
docker logs ai-ollama

# 詳細ログ
docker logs ai-ollama --tail=50

# リアルタイムログ
docker logs -f ai-ollama
```

### 3. ヘルスチェックの確認
```cmd
# 手動ヘルスチェック
docker exec ai-ollama curl -f http://localhost:11434/api/tags

# 外部から確認
curl -f http://localhost:11434/api/tags
```

### 4. コンテナ内部の確認
```cmd
# コンテナに接続
docker exec -it ai-ollama bash

# プロセス確認
ps aux

# ポート確認
netstat -tlnp | grep :11434

# GPU確認
nvidia-smi
```

---

## 📥 モデル管理

### 1. モデルの確認
```cmd
# 利用可能なモデル
curl -s http://localhost:11434/api/tags

# コンテナ内から確認
docker exec ai-ollama ollama list
```

### 2. モデルのダウンロード
```cmd
# 手動ダウンロード
docker exec -it ai-ollama ollama pull llama3.2

# バックグラウンドダウンロード
docker exec -d ai-ollama ollama pull llama3.2-vision
```

### 3. モデルの削除
```cmd
# モデル削除
docker exec -it ai-ollama ollama rm llama3.2
```

---

## 🎯 成功確認

### 1. 全てのコンテナが起動
```cmd
docker-compose -f docker-compose.fixed.yml ps
```

期待される出力:
```
NAME           IMAGE                     COMMAND                  CREATED         STATUS                    PORTS
ai-ollama      ollama/ollama:latest     "/bin/sh -c 'ollama…"   2 minutes ago   Up 2 minutes (healthy)   0.0.0.0:11434->11434/tcp
ai-agent-app   ai-agent_gui_ai-app      "/app/scripts/start…"   2 minutes ago   Up 2 minutes (healthy)   0.0.0.0:8501->8501/tcp
ai-voicevox     voicevox/voicevox_e...   "/app/run.sh"            2 minutes ago   Up 2 minutes (healthy)   0.0.0.0:50021->50021/tcp
ai-redis        redis:7-alpine           "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes (healthy)   6379/tcp
```

### 2. APIアクセスの確認
```cmd
# Ollama API
curl -f http://localhost:11434/api/tags

# Streamlit
curl -f http://localhost:8501

# VOICEVOX
curl -f http://localhost:50021/docs
```

### 3. ブラウザアクセス
- **Streamlit**: http://localhost:8501
- **Ollama API**: http://localhost:11434
- **VOICEVOX**: http://localhost:50021

---

## 🛠️ トラブルシューティング

### 1. Ollamaが起動しない
```cmd
# 原因の特定
docker logs ai-ollama --tail=50

# GPUの確認
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# CPU版で試す
docker-compose -f docker-compose.fixed.yml up -d
```

### 2. ヘルスチェックが失敗
```cmd
# 手動テスト
docker exec ai-ollama curl -f http://localhost:11434/api/tags

# ポート確認
docker exec ai-ollama netstat -tlnp | grep :11434

# プロセス確認
docker exec ai-ollama ps aux | grep ollama
```

### 3. モデルダウンロードが失敗
```cmd
# ディスク容量確認
docker exec ai-ollama df -h

# ネットワーク確認
docker exec ai-ollama ping -c 3 google.com

# 手動ダウンロード
docker exec -it ai-ollama ollama pull llama3.2
```

---

## 🎉 解決完了の確認

### ✅ 全てのコンテナがhealthy
- ai-ollama: healthy
- ai-agent-app: healthy
- ai-voicevox: healthy
- ai-redis: healthy

### ✅ APIアクセスが成功
- Ollama API: 200 OK
- Streamlit: 200 OK
- VOICEVOX: 200 OK

### ✅ ブラウザから利用可能
- http://localhost:8501 でAIと対話可能
- 音声入力で即座に応答

---

**🎯 これでOllamaコンテナのunhealthy問題が完全に解決されました！**
