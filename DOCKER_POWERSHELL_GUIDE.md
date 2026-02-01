# 🔧 PowerShell実行ガイド

## 🎯 問題の解決

### エラーメッセージ
```
docker_final_start.bat : 用語 'docker_final_start.bat' は、コマンドレット、関数、スクリプト ファイル、または操作可能なプログラムの名前として認識されません。
```

### 原因
PowerShellではカレントディレクトリのスクリプトを `.\` を付けて実行する必要があります。

---

## 🚀 解決策

### 1. PowerShellスクリプトの使用（推奨）

#### 完全版PowerShellスクリプト
```powershell
# 実行方法
.\docker_final_start.ps1

# または
powershell -ExecutionPolicy Bypass -File .\docker_final_start.ps1
```

#### 簡易版PowerShellスクリプト
```powershell
# 実行方法
.\start_docker.ps1

# または
powershell -ExecutionPolicy Bypass -File .\start_docker.ps1
```

### 2. バッチファイルの実行方法

#### コマンドプロンプトから実行
```cmd
# コマンドプロンプトを開いて実行
docker_final_start.bat

# または
.\docker_final_start.bat
```

#### PowerShellから実行
```powershell
# PowerShellからバッチファイルを実行
.\docker_final_start.bat

# または
cmd /c docker_final_start.bat
```

---

## 📁 新しいファイル

### 1. docker_final_start.ps1
- **機能**: 完全なPowerShell版起動スクリプト
- **特徴**: 詳細なログ、エラーハンドリング、GPU判定
- **実行**: `.\docker_final_start.ps1`

### 2. start_docker.ps1
- **機能**: 簡易版PowerShell起動スクリプト
- **特徴**: シンプルで確実な起動
- **実行**: `.\start_docker.ps1`

---

## 🔧 実行手順

### 方法1: PowerShellスクリプト（推奨）
```powershell
# 1. PowerShellを開く
# 2. プロジェクトディレクトリに移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# 3. 実行ポリシーを設定（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. スクリプトを実行
.\docker_final_start.ps1
```

### 方法2: 簡易版PowerShell
```powershell
# 1. PowerShellを開く
# 2. プロジェクトディレクトリに移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# 3. スクリプトを実行
.\start_docker.ps1
```

### 方法3: コマンドプロンプト
```cmd
# 1. コマンドプロンプトを開く
# 2. プロジェクトディレクトリに移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# 3. バッチファイルを実行
docker_final_start.bat
```

---

## 🛠️ トラブルシューティング

### 1. 実行ポリシーの問題
```powershell
# 現在の実行ポリシーを確認
Get-ExecutionPolicy

# 実行ポリシーを変更
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 一時的に実行ポリシーを変更して実行
powershell -ExecutionPolicy Bypass -File .\docker_final_start.ps1
```

### 2. ファイルが見つからない
```powershell
# カレントディレクトリを確認
Get-Location

# ファイルの存在を確認
Test-Path .\docker_final_start.ps1
Test-Path .\start_docker.ps1
Test-Path .\docker_final_start.bat
```

### 3. Pythonスクリプトが実行できない
```powershell
# Pythonのパスを確認
Get-Command python

# Pythonスクリプトを直接実行
python scripts\fix_line_endings.py
```

---

## 📋 比較表

| 方法 | 特徴 | 推奨度 |
|------|------|--------|
| `.\docker_final_start.ps1` | 完全な機能、詳細なログ | ⭐⭐⭐⭐⭐ |
| `.\start_docker.ps1` | シンプル、確実 | ⭐⭐⭐⭐ |
| `cmd /c docker_final_start.bat` | 従来の方法 | ⭐⭐⭐ |
| `.\docker_final_start.bat` | PowerShellから実行 | ⭐⭐ |

---

## 🎯 推奨手順

### 1. 初回セットアップ
```powershell
# PowerShellを管理者として開く
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 通常実行
```powershell
# プロジェクトディレクトリに移動
cd C:\Users\GALLE\CascadeProjects\ai_agent_gui

# PowerShellスクリプトを実行
.\docker_final_start.ps1
```

### 3. 代替手段
```powershell
# 簡易版を実行
.\start_docker.ps1

# またはコマンドプロンプトから
cmd /c docker_final_start.bat
```

---

## 🎉 成功確認

### ✅ 正常に実行された場合
```
========================================
🚀 AI Agent System Final Start
========================================
📁 プロジェクトディレクトリ: C:\Users\GALLE\CascadeProjects\ai_agent_gui
🔄 Docker Desktopの状態を確認中...
✅ Docker Desktopが起動しています
🔧 改行コードを修正中...
✅ 改行コードの修正完了
💾 データディレクトリを作成中...
🛑 既存のコンテナを停止中...
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

## 🔧 PowerShellの基本

### 実行ポリシーの種類
- `Restricted`: スクリプト実行不可
- `AllSigned`: 全てのスクリプトに署名が必要
- `RemoteSigned`: ローカルスクリプトは実行可能、リモートは署名が必要
- `Unrestricted`: 全てのスクリプトを実行可能

### よく使うコマンド
```powershell
# 現在のポリシー確認
Get-ExecutionPolicy

# ポリシー変更
Set-ExecutionPolicy RemoteSigned

# スクリプト実行
.\script.ps1

# 一時的にポリシーを変更して実行
powershell -ExecutionPolicy Bypass -File .\script.ps1
```

---

**🎯 これでPowerShellでの実行エラーが完全に解消されます！**
