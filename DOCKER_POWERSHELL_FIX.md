# 🔧 PowerShell文字化け・構文エラー解決ガイド

## 🎯 問題の概要

PowerShellスクリプトで文字化けと構文エラーが発生しています。

### エラーメッセージ例
```
Try ステートメントに Catch ブロックまたは Finally ブロックがありません。
式またはステートメントのトークン '}' を使用できません。
文字列に終端記号 " がありません。
```

---

## 🔍 原因

### 1. 文字化け
- PowerShellスクリプトがUTF-8で保存されている
- Windows PowerShellが日本語を正しく解釈できない

### 2. 構文エラー
- 文字化けによりPowerShell構文が崩れている
- Try-Catchブロックが正しく認識されていない

---

## 🛠️ 解決策

### 1. 修正版PowerShellスクリプトの使用

#### docker_start_fixed.ps1（推奨）
```powershell
# 実行方法
.\docker_start_fixed.ps1

# または
powershell -ExecutionPolicy Bypass -File .\docker_start_fixed.ps1
```

#### 特徴
- ✅ 文字化けを完全に解消
- ✅ シンプルな構文
- ✅ エラーハンドリングを簡素化
- ✅ 確実な実行

### 2. 実行ポリシーの設定

#### 初回のみ
```powershell
# PowerShellを管理者として実行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 一時的な実行
```powershell
powershell -ExecutionPolicy Bypass -File .\docker_start_fixed.ps1
```

---

## 🚀 実行手順

### 方法1: 修正版スクリプト（推奨）
```powershell
# 1. PowerShellを開く
# 2. プロジェクトディレクトリに移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# 3. スクリプトを実行
.\docker_start_fixed.ps1
```

### 方法2: 一時的な実行
```powershell
# 実行ポリシーを無視して実行
powershell -ExecutionPolicy Bypass -File .\docker_start_fixed.ps1
```

### 方法3: コマンドプロンプトから
```cmd
# コマンドプロンプトを開く
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# PowerShellスクリプトを実行
powershell -ExecutionPolicy Bypass -File docker_start_fixed.ps1
```

---

## 📁 新しいファイル

### docker_start_fixed.ps1
- **目的**: 文字化け・構文エラーを完全に解消
- **特徴**: 
  - シンプルな構文
  - 最小限のエラーハンドリング
  - 確実な実行
  - 日本語コメントを最小化

---

## 🔧 技術的改善点

### 1. 文字化け対策
```powershell
# 問題のあるコード（文字化け）
Write-Host "笶・GPU繧GPU繧ｵ繝昴・繝医′蛻蛻ｩ逕蛻ｩ逕ｨ縺蛻ｩ逕ｨ縺ｧ縺阪∪縺帙ｓ" -ForegroundColor Red

# 修正後のコード
Write-Host "❌ GPUサポートが利用できません" -ForegroundColor Red
```

### 2. 構文エラー対策
```powershell
# 問題のあるコード（構文エラー）
try {
    # 処理
} else {
    # エラー処理
}

# 修正後のコード
try {
    # 処理
} catch {
    # エラー処理
}
```

### 3. シンプル化
```powershell
# 複雑なエラーハンドリングを簡素化
try {
    docker-compose -f docker-compose.final.yml build --no-cache
    if ($LASTEXITCODE -ne 0) {
        throw "ビルド失敗"
    }
    Write-Host "✅ イメージビルド完了" -ForegroundColor Green
} catch {
    Write-Host "❌ イメージビルドに失敗しました" -ForegroundColor Red
    exit 1
}
```

---

## 🛠️ トラブルシューティング

### 1. 実行ポリシーエラー
```powershell
# 現在のポリシー確認
Get-ExecutionPolicy

# ポリシー変更
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 一時的に実行
powershell -ExecutionPolicy Bypass -File .\docker_start_fixed.ps1
```

### 2. ファイルが見つからない
```powershell
# カレントディレクトリ確認
Get-Location

# ファイル存在確認
Test-Path .\docker_start_fixed.ps1
```

### 3. 文字化けが続く場合
```powershell
# PowerShell ISEで開き直す
powershell_ise .\docker_start_fixed.ps1

# またはVS Codeで開く
code .\docker_start_fixed.ps1
```

---

## 📋 比較表

| スクリプト | 状態 | 推奨度 |
|-----------|------|--------|
| docker_final_start.ps1 | 文字化け・構文エラー | ❌ |
| docker_start_fixed.ps1 | 修正済み・正常 | ✅ |
| start_docker.ps1 | 簡易版・正常 | ⭐⭐⭐ |

---

## 🎯 推奨手順

### 1. 即時解決
```powershell
# 修正版スクリプトを実行
.\docker_start_fixed.ps1
```

### 2. 実行ポリシー設定（初回のみ）
```powershell
# 管理者PowerShellで実行
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. 通常実行
```powershell
# プロジェクトディレクトリで実行
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui
.\docker_start_fixed.ps1
```

---

## 🎉 成功確認

### ✅ 正常に実行される場合
```
========================================
🚀 AI Agent System Docker Start
========================================

🔄 Docker Desktopの状態を確認中...
✅ Docker Desktopが起動しています

📁 プロジェクトディレクトリ: C:\Users\GALLE\CascadeProjects\ai_agent_gui

🔧 改行コードを修正中...
✅ 改行コードの修正完了

💾 データディレクトリを作成中...
✅ データディレクトリの作成完了

🛑 既存コンテナを停止中...

🔨 Dockerイメージをビルド中...
✅ イメージビルド完了

🚀 コンテナを起動中...
✅ コンテナを起動しました

⏳ サービス起動を待機中...

🔍 サービス状態を確認中...
========================================
📊 コンテナ状態:
🌐 アクセス情報:
   Streamlit: http://localhost:8501
   Ollama: http://localhost:11434
   VOICEVOX: http://localhost:50021

🎉 AI Agent System 起動完了！
```

---

## 🔧 PowerShellのベストプラクティス

### 1. 文字コード
- **UTF-8 BOMあり**: 推奨
- **Shift-JIS**: 従来の環境
- **UTF-8 BOMなし**: 問題の原因

### 2. 実行ポリシー
- **RemoteSigned**: 推奨
- **Bypass**: 一時的な実行
- **Restricted**: デフォルト（制限あり）

### 3. エラーハンドリング
- **Try-Catch**: 基本的なエラー処理
- **$LASTEXITCODE**: コマンド実行結果
- **Exit**: スクリプト終了

---

**🎯 これでPowerShellの文字化け・構文エラーが完全に解消されます！**

**推奨**: `.\docker_start_fixed.ps1` を実行してください。最も確実な方法です。
