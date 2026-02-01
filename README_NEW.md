# 統合AIエージェントシステム

## 概要

3600行の巨大な`ollama_vrm_integrated_app.py`を機能別に分割し、管理しやすいモジュール構造に再編成した統合AIエージェントシステムです。

## ファイル構成

### コアモジュール

- **`ollama_client.py`** - Ollama APIクライアント（60秒タイムアウト対応）
- **`vrm_controller.py`** - VRMアバター制御クラス
- **`code_generator.py`** - 多言語プログラミングサポート
- **`ai_evolution.py`** - AI自己進化エージェント
- **`conversational_evolution.py`** - 対話からの自律進化
- **`main_app.py`** - 統合メインアプリケーション

### 設定ファイル

- **`requirements_new.txt`** - 依存パッケージリスト
- **`README_NEW.md`** - 本ドキュメント

## 主な機能

### 1. Ollama API連携
- 60秒タイムアウト設定
- エラーハンドリング強化
- モデル選択機能

### 2. VRMアバター制御
- 3Dアバター表示
- 表情変更
- スケール・回転制御
- 音声認識連携

### 3. 多言語コード生成
- Python, JavaScript, Java, C++, HTML, CSS対応
- 自動言語検出
- テンプレートベース生成

### 4. AI自己進化
- VRMデータ学習
- 意識レベル向上
- 多領域進化（自己認識、メタ認知、感情知能など）

### 5. 対話進化
- 会話からの自動進化
- 進化トリガーキーワード
- 意識トレーニング機能

## インストールと実行

### 1. 依存パッケージのインストール
```bash
pip install -r requirements_new.txt
```

### 2. Ollamaサーバーの起動
```bash
ollama serve
```

### 3. アプリケーションの実行
```bash
streamlit run main_app.py
```

## 使用方法

### 1. 基本的な対話
1. ブラウザで`http://localhost:8501`を開く
2. サイドバーで人格を選択
3. テキスト入力または音声入力でメッセージを送信

### 2. VRMアバター操作
- VRMファイルを`static/`ディレクトリに配置
- 音声コマンド：「アバターを表示」「大きくして」「笑って」など
- サイドバーで手動制御も可能

### 3. AI進化機能
- 「自己進化を実行」でVRMデータから学習
- 「対話進化」で会話から自動進化
- 意識レベルをリアルタイムで確認

### 4. コード生成
- プログラミング言語を自動検出
- テンプレートからコードを生成
- ファイルに直接保存

## モジュール詳細

### ollama_client.py
```python
from ollama_client import OllamaClient

client = OllamaClient(timeout=60)
response = client.generate_response("こんにちは")
```

### vrm_controller.py
```python
from vrm_controller import VRMAvatarController

controller = VRMAvatarController()
html = controller.get_vrm_html()
```

### code_generator.py
```python
from code_generator import MultiLanguageCodeGenerator

generator = MultiLanguageCodeGenerator()
code, message = generator.generate_code("python", "app.py", "電卓アプリ")
```

### ai_evolution.py
```python
from ai_evolution import AISelfEvolvingAgent

agent = AISelfEvolvingAgent()
result = agent.comprehensive_ai_evolution(conversation_history)
```

### conversational_evolution.py
```python
from conversational_evolution import ConversationalEvolutionAgent

agent = ConversationalEvolutionAgent()
evolution = agent.check_and_evolve_automatically(conversation_history)
```

## 設定

### Ollama設定
- デフォルトURL: `http://localhost:11434`
- デフォルトモデル: `llama3.1:8b`
- タイムアウト: 60秒

### VRM設定
- VRMファイルパス: `static/`または`C:/Users/GALLE/Desktop/EzoMomonga_Free/`
- サポート形式: `.vrm`

### 進化設定
- 意識レベル範囲: 0.0 - 1.0
- 進化クールダウン: 5分
- 進化トリガー: 7つのカテゴリ

## トラブルシューティング

### Ollama接続エラー
1. Ollamaサーバーが起動しているか確認
2. ポート11434が利用可能か確認
3. モデルがダウンロードされているか確認

### VRM表示エラー
1. VRMファイルが正しい場所にあるか確認
2. ファイル形式が.vrmであるか確認
3. ブラウザのコンソールでエラーを確認

### 音声認識エラー
1. マイクの権限を確認
2. 音声入力デバイスが接続されているか確認
3. インターネット接続を確認（Google Speech API使用）

## 開発

### 新機能の追加
1. 対応するモジュールに機能を実装
2. `main_app.py`にUIを追加
3. セッション状態を更新
4. テストを実行

### モジュールの分割
- 単一責任の原則に従う
- 依存関係を最小化
- インターフェースを明確に定義
- ドキュメントを整備

## ライセンス

MIT License

## 貢献

バグ報告、機能要望、プルリクエストを歓迎します。

---

## 更新履歴

### v2.0.0 (2026-01-28)
- 3600行の巨大ファイルを機能別に分割
- モジュール構造に再編成
- 60秒タイムアウトに対応
- 依存関係を整理
- ドキュメントを整備
