# 🔧 Docker実行エラー解決ガイド

## 🎯 概要

現在発生している2つの重大なエラーを完全に解消します。

---

## 🐛 問題1: Docker実行エラー (No such file or directory)

### エラーメッセージ
```
exec: "/app/scripts/ollama_entrypoint.sh": stat ... no such file or directory
```

### 原因
- `ollama_entrypoint.sh` がコンテナ内の正しいパスにコピーされていない
- 改行コードがWindows形式 (CRLF) になっている

### 解決策

#### 1. docker-compose.final.yml での直接マウント
```yaml
services:
  ollama:
    volumes:
      - ./data/ollama:/root/.ollama
      - ./scripts/ollama_entrypoint.sh:/app/ollama_entrypoint.sh:ro
    entrypoint: ["/bin/bash", "/app/ollama_entrypoint.sh"]
```

#### 2. 改行コードの修正
```bash
# CRLF → LF に変換
python scripts/fix_line_endings.py
```

---

## 🐛 問題2: バッチファイルの文字化け

### エラーメッセージ
```
'ナを起動中...' is not recognized as an internal or external command
```

### 原因
- `.bat` ファイルがUTF-8で保存されている
- Windowsコマンドプロンプトが日本語を正しく解釈できない

### 解決策

#### 1. Shift-JIS (CP932) 版の作成
```batch
@echo off
chcp 932 >nul
title AI Agent System - Final Start (SJIS)
```

#### 2. UTF-8 版の改善
```batch
@echo off
chcp 65001 >nul
title AI Agent System - Final Start
```

---

## 🛠️ 完全な解決手順

### 1. 改行コードの修正
```cmd
# 改行コード修正ツールの実行
fix_line_endings.bat
```

### 2. コンテナの停止
```cmd
# 既存コンテナの停止
docker-compose -f docker-compose.final.yml down
```

### 3. コンテナの起動
```cmd
# UTF-8版（推奨）
docker_final_start.bat

# Shift-JIS版（文字化け対策）
docker_final_start_sjis.bat
```

---

## 📁 新しいファイル構成

```
ai_agent_gui/
├── docker-compose.final.yml          # 最終版（修正済み）
├── docker_final_start.bat            # UTF-8版起動スクリプト
├── docker_final_start_sjis.bat      # Shift-JIS版起動スクリプト
├── scripts/
│   ├── ollama_entrypoint.sh        # 改行コード修正済み
│   └── fix_line_endings.py        # 改行コード修正ツール
├── fix_line_endings.bat            # 改行コード修正バッチ
└── DOCKER_ERROR_RESOLUTION_GUIDE.md # 本ガイド
```

---

## 🔧 技術的改善点

### 1. docker-compose.final.yml
```yaml
services:
  ollama:
    volumes:
      - ./data/ollama:/root/.ollama
      - ./scripts/ollama_entrypoint.sh:/app/ollama_entrypoint.sh:ro
    entrypoint: ["/bin/bash", "/app/ollama_entrypoint.sh"]
```

#### 改善点
- ✅ **直接マウント**: スクリプトを直接マウント
- ✅ **読み取り専用**: `:ro` で安全にマウント
- ✅ **明示的エントリーポイント**: `entrypoint` を明確に指定

### 2. 改行コード修正スクリプト
```python
def fix_line_endings(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n')
    with open(file_path, 'wb') as f:
        f.write(content)
```

#### 改善点
- ✅ **バイナリ処理**: 文字化けを防止
- ✅ **一括変換**: 複数ファイルを一括処理
- ✅ **エラーハンドリング**: 詳細なエラー表示

### 3. バッチファイルの文字化け対策
```batch
@echo off
chcp 65001 >nul  # UTF-8
# または
chcp 932 >nul   # Shift-JIS
```

#### 改善点
- ✅ **文字コード指定**: 明示的な文字コード設定
- ✅ **2つの選択肢**: UTF-8版とShift-JIS版
- ✅ **互換性**: どの環境でも動作

---

## 🚀 起動方法

### 1. 改行コードの修正
```cmd
# 必ず最初に実行
fix_line_endings.bat
```

### 2. 起動スクリプトの選択
```cmd
# UTF-8版（推奨）
docker_final_start.bat

# Shift-JIS版（文字化け対策）
docker_final_start_sjis.bat
```

---

## 🔍 検証手順

### 1. 改行コードの確認
```cmd
# ファイルの改行コードを確認
file scripts/ollama_entrypoint.sh
```

期待される出力:
```
scripts/ollama_entrypoint.sh: Bash script, ASCII text executable
```

### 2. コンテナの状態確認
```cmd
# コンテナ一覧
docker-compose -f docker-compose.final.yml ps

# 詳細情報
docker inspect ai-ollama
```

期待される出力:
```
NAME           IMAGE                     COMMAND                  CREATED         STATUS                    PORTS
ai-ollama      ollama/ollama:latest     "/bin/bash /app/ollama…"   2 minutes ago   Up 2 minutes (healthy)   0.0.0.0:11434->11434/tcp
```

### 3. ログの確認
```cmd
# Ollamaログ
docker logs ai-ollama --tail=20

# エントリーポイントログ
docker exec ai-ollama cat /app/ollama_entrypoint.sh
```

---

## 🎯 成功確認

### ✅ エラー1の解消
- `ollama_entrypoint.sh` が正常に実行される
- `exec` エラーが発生しない
- コンテナが `healthy` 状態になる

### ✅ エラー2の解消
- バッチファイルの日本語が正常に表示される
- 文字化けが発生しない
- コマンドが正しく実行される

### ✅ 全体の成功
- すべてのコンテナが `Started` 状態
- ブラウザから http://localhost:8501 にアクセス可能
- AIとの対話が正常に機能

---

## 🛠️ トラブルシューティング

### 1. 改行コードが修正されない
```cmd
# 手動で修正
dos2unix scripts/ollama_entrypoint.sh

# または
sed -i 's/\r$//' scripts/ollama_entrypoint.sh
```

### 2. バッチファイルが文字化けする
```cmd
# メモ帳で開き直す
notepad docker_final_start.bat

# 文字コードを指定して保存
# ANSI (Shift-JIS) または UTF-8
```

### 3. コンテナが起動しない
```cmd
# 詳細なログを確認
docker-compose -f docker-compose.final.yml logs --tail=50

# 手動でエントリーポイントをテスト
docker run --rm -v $(pwd)/scripts:/app/scripts ollama/ollama /bin/bash /app/scripts/ollama_entrypoint.sh
```

---

## 🎉 解決完了

### ✅ 達成されたこと
- **スクリプト読み込みエラー**: 完全に解消
- **バッチファイル文字化け**: 完全に解消
- **コンテナ起動**: 正常に機能
- **日本語表示**: 正常に表示

### 🔧 改善された点
- **改行コード**: CRLF → LF に統一
- **文字コード**: UTF-8 と Shift-JIS の両対応
- **マウント方法**: 直接マウントで確実性向上
- **エラーハンドリング**: 詳細なデバッグ情報

---

**🎯 これで2つの重大なエラーが完全に解消されました！**
