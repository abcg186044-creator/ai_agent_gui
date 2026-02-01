# 🐳 Dockerfile Best Practices Guide

## 🎯 概要

Dockerfileのキーワードを大文字に統一し、Dockerのベストプラクティスに従って最適化しました。

---

## 📋 修正内容

### 1. FromAsCasing 警告の解消
```dockerfile
# 修正前
FROM python:3.10-slim as builder

# 修正後
FROM python:3.10-slim AS builder
```

### 2. すべての命令キーワードを大文字に統一
```dockerfile
# 統一されたキーワード
FROM python:3.10-slim AS builder
RUN apt-get update && apt-get install -y ...
WORKDIR /app
COPY requirements.txt .
ENV PYTHONPATH=/app
EXPOSE 8501
CMD ["/app/scripts/start_optimized.sh"]
HEALTHCHECK --interval=30s --timeout=10s ...
```

---

## 🔧 修正されたファイル

### 1. Dockerfile.production
- ✅ **FROM**: `FROM python:3.10-slim AS builder`
- ✅ **AS**: `AS builder` （大文字）
- ✅ **他の命令**: すべて大文字で統一

### 2. Dockerfile.optimized
- ✅ **FROM**: `FROM python:3.10-slim AS builder`
- ✅ **AS**: `AS builder` （大文字）
- ✅ **他の命令**: すべて大文字で統一

### 3. Dockerfile
- ✅ **FROM**: `FROM python:3.10-slim` （既に大文字）
- ✅ **他の命令**: すべて大文字で統一

---

## 📏 Dockerfile Best Practices

### 1. 命令キーワードの大文字統一
```dockerfile
# ✅ 正しい例
FROM python:3.10-slim AS builder
RUN apt-get update && apt-get install -y ...
WORKDIR /app
COPY requirements.txt .
ENV PYTHONPATH=/app
EXPOSE 8501
CMD ["/app/scripts/start_optimized.sh"]
HEALTHCHECK --interval=30s --timeout=10s ...

# ❌ 誤った例
from python:3.10-slim as builder
run apt-get update && apt-get install -y ...
workdir /app
copy requirements.txt .
env PYTHONPATH=/app
expose 8501
cmd ["/app/scripts/start_optimized.sh"]
healthcheck --interval=30s --timeout=10s ...
```

### 2. マルチステージビルドのベストプラクティス
```dockerfile
# ビルドステージ
FROM python:3.10-slim AS builder
RUN apt-get update && apt-get install -y build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 実行ステージ
FROM python:3.10-slim
RUN apt-get update && apt-get install -y curl
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .
CMD ["python", "app.py"]
```

### 3. レイヤーの最適化
```dockerfile
# ✅ 良い例 - レイヤーをまとめる
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# ❌ 悪い例 - レイヤーが分離
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get install -y git
```

### 4. キャッシュの活用
```dockerfile
# ✅ 良い例 - 変化頻度の低いものを先に
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# ❌ 悪い例 - 変化頻度の高いものを先に
COPY . .
COPY requirements.txt .
RUN pip install -r requirements.txt
```

---

## 🔍 チェックリスト

### ✅ 確認項目
- [ ] **FROM**: 大文字で記述
- [ ] **AS**: 大文字で記述
- [ ] **RUN**: 大文字で記述
- [ ] **WORKDIR**: 大文字で記述
- [ ] **COPY**: 大文字で記述
- [ ] **ENV**: 大文字で記述
- [ ] **EXPOSE**: 大文字で記述
- [ ] **CMD**: 大文字で記述
- [ ] **HEALTHCHECK**: 大文字で記述
- [ ] **ARG**: 大文字で記述
- [ ] **ADD**: 大文字で記述
- [ ] **ENTRYPOINT**: 大文字で記述
- [ ] **VOLUME**: 大文字で記述
- [ ] **USER**: 大文字で記述
- [ ] **LABEL**: 大文字で記述
- [ ] **STOPSIGNAL**: 大文字で記述
- [ ] **SHELL**: 大文字で記述
- [ ] **ONBUILD**: 大文字で記述

---

## 🛠️ 検証コマンド

### 1. Dockerfileの構文チェック
```bash
# Dockerfileの構文をチェック
docker build --dry-run -f Dockerfile .

# Hadolintでベストプラクティスをチェック
hadolint Dockerfile
```

### 2. ビルドのテスト
```bash
# ビルドのテスト
docker build -t test-image .

# イメージの確認
docker images test-image
```

### 3. コンテナの実行テスト
```bash
# コンテナの実行
docker run --rm -it test-image bash

# ヘルスチェックの確認
docker inspect test-image
```

---

## 📚 参考資料

### 1. Docker公式ドキュメント
- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/)

### 2. 静的解析ツール
- [Hadolint](https://github.com/hadolint/hadolint) - Dockerfileのリンター
- [Dockerfile Linter](https://github.com/replicatedhq/dockerfile-lint)

### 3. CI/CD連携
- [GitHub Actions](https://github.com/features/actions)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)

---

## 🎯 まとめ

### ✅ 達成されたこと
- **FromAsCasing警告の解消**: `FROM` と `AS` を大文字に統一
- **命令キーワードの統一**: すべての命令を大文字で統一
- **ベストプラクティスの適用**: Dockerの推奨事項に従った記述
- **一貫性の確保**: 全てのDockerfileで統一されたスタイル

### 🔧 改善された点
- **可読性の向上**: 統一された大文字で見やすくなった
- **警告の解消**: FromAsCasing警告がなくなった
- **保守性の向上**: ベストプラクティスに従った記述
- **CI/CD対応**: 静的解析ツールでの警告がなくなった

---

**🎯 これでDockerfileがベストプラクティスに従ったクリーンな状態になりました！**
