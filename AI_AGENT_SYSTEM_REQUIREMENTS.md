# AI Agent System - 詳細構成・機能要件仕様書

## 📋 概要

本書類は、高度AIエージェントシステムをゼロから構築するための詳細な技術仕様、構成要件、機能要件を定義する。

### 🎯 システム目的
- **究極のAIアシスタント**: ユーザーの画面監視、音声対話、コード自動生成・検証
- **マルチ人格システム**: 親友エンジニア、分身、エキスパートの3人格切り替え
- **専門知識統合**: Excel/PDF解析、RAG検索、Web情報収集
- **自己修復能力**: 起動時診断、コード自動デバッグ、依存関係自動解決

---

## 🏗️ システムアーキテクチャ

### 📐 全体構成図
```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Agent System                      │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer                                       │
│  ├─ Streamlit Web UI (メインインターフェース)          │
│  ├─ Web Canvas Preview (HTML/CSS/JSリアルタイム)      │
│  └─ VRM Avatar Display (3Dアバター表示)            │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer                                     │
│  ├─ Main Application (app.py)                          │
│  ├─ Agent System (ReAct + Multi-Agent)                │
│  ├─ Personality Manager (人格切り替え)                  │
│  └─ Verification Protocols (検証・自己修復)           │
├─────────────────────────────────────────────────────────────────┤
│  AI/ML Layer                                          │
│  ├─ Ollama Integration (llama3.1:8b)               │
│  ├─ Voice Processing (faster-whisper + pyttsx3)         │
│  ├─ Knowledge System (RAG + Excel/PDF解析)            │
│  └─ Code Verification (静的解析・実行・修正)           │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                           │
│  ├─ Knowledge Base (XiフォルダExcel/PDF)             │
│  ├─ User Profile (パーソナライズDB)                   │
│  ├─ Session Memory (会話履歴)                        │
│  └─ Cache System (一時データ・モデルキャッシュ)           │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                   │
│  ├─ FastAPI Server (静的ファイル配信)                 │
│  ├─ PHP Runtime (サーバーサイド実行)                 │
│  ├─ File System (プロジェクト管理)                       │
│  └─ System Monitoring (リソース監視)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 技術スタック要件

### 🔧 コア技術
| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|--------|------|
| **言語** | Python | 3.10+ | メインアプリケーション |
| **Web UI** | Streamlit | 1.28.1+ | フロントエンドインターフェース |
| **Web API** | FastAPI | 0.104+ | 静的ファイル配信 |
| **Web Server** | Uvicorn | 0.24+ | APIサーバー |
| **AIモデル** | Ollama | 0.13.5+ | LLM推論 |
| **AIモデル** | llama3.1:8b | 4.9GB | メインLLM |

### 📦 必須ライブラリ
```python
# データ処理・解析
pandas==2.1.0              # データ分析
openpyxl==3.1.2            # Excelファイル処理
PyMuPDF==1.23.8           # PDFファイル処理
numpy==1.24.3              # 数値計算
requests==2.32.5            # HTTPリクエスト

# AI/機械学習
torch==2.1.0                # 機械学習フレームワーク
transformers==4.36.0         # トランスフォーマーモデル
sentence-transformers==2.2.2   # 文章埋め込み
faiss-cpu==1.7.4            # ベクトル検索
langchain==0.1.0             # LLMオーケストレーション
langchain-community==0.0.4    # コミュニティツール
langchain-ollama==0.1.1     # Ollama連携
langchain-experimental==0.4.1  # 実験的機能

# 音声処理
faster-whisper==0.9.0         # 音声認識
librosa==0.10.1             # 音声分析
sounddevice==0.4.6           # 音声入力
pyttsx3==2.99               # 音声合成

# Web開発
fastapi==0.128.0             # Web API
uvicorn==0.40.0             # Webサーバー
streamlit==1.28.1            # Web UI
jinja2==3.1.6                # テンプレートエンジン

# 画像処理・GUI
Pillow==10.4.0              # 画像処理
pyautogui==0.9.54           # GUI自動化
opencv-python==4.8.1.78      # コンピュータービジョン

# ユーティリティ
qrcode[pil]==7.4.2           # QRコード生成
beautifulsoup4==4.12.2        # Webスクレイピング
selenium==4.15.2             # ブラウザ自動化
psutil==5.9.6                # システム監視
python-dotenv==1.0.0          # 環境変数管理
```

### 🐘 PHP環境
```php
# PHPバージョン要件
PHP 8.5+ (CLI)

# 拡張モジュール
- mbstring (マルチバイト文字列)
- curl (HTTPクライアント)
- json (JSON処理)
- fileinfo (ファイル情報)
```

---

## 🗂️ ディレクトリ構成

### 📁 プロジェクトフォルダ構成
```
ai_agent_gui/
├── 📄 app.py                           # メインアプリケーション
├── 📄 requirements.txt                 # Python依存関係
├── 📁 static/                          # 静的ファイル
│   ├── avatar.vrm                     # VRMアバターモデル
│   ├── css/                           # スタイルシート
│   ├── js/                            # JavaScriptファイル
│   └── images/                        # 画像リソース
├── 📁 knowledge_base/                  # 知識ベース
│   ├── documents/                     # ドキュメント
│   └── embeddings/                    # 埋め込みデータ
├── 📁 specialist_personality.py         # スペシャリスト人格システム
├── 📄 verification_protocols.py        # 検証プロトコル
├── 📄 web_canvas_preview.py           # Web Canvasプレビュー
├── 📁 memory_db.json                  # パーソナライズDB
├── 📁 logs/                          # ログファイル
├── 📁 temp/                          # 一時ファイル
└── 📁 backups/                       # バックアップ
```

### 📄 必須ファイル一覧
| ファイル名 | 種別 | 説明 |
|---------|------|------|
| `app.py` | メイン | アプリケーション本体 |
| `requirements.txt` | 設定 | Python依存関係リスト |
| `avatar.vrm` | リソース | 3Dアバターモデル |
| `memory_db.json` | データ | ユーザーパーソナライズDB |
| `.env` | 設定 | 環境変数設定 |

---

## 🎭 人格システム仕様

### 👥 人格定義
| 人格名 | VRM表情 | 音声キャラ | テーマ色 | システムプロンプト |
|--------|----------|------------|----------|----------------|
| **親友エンジニア** | happy | normal | 緑 (#4CAF50) | フレンドリーな親友として会話 |
| **分身** | joy | similar | 青 (#2196F3) | ユーザーと同じ視点で応答 |
| **エキスパート** | neutral | professional | 紫 (#9C27B0) | 専門家として正確な回答を提供 |

### 🔄 人格切り替え機能
```python
class PersonalityState:
    name: str           # 人格名
    vrm_expression: str  # VRM表情
    voice_character: str  # 音声キャラクター
    theme_colors: dict   # UIテーマ色
    system_prompt: str   # システムプロンプト

# 切り替えトリガー
- UIボタンクリック
- 音声コマンド
- 自動コンテキスト判定
- 時刻ベースの自動切り替え
```

---

## 🧠 AI機能要件

### 🤖 LLM連携
```python
# Ollama統合要件
class OllamaIntegration:
    model: "llama3.1:8b"           # メインモデル
    temperature: 0.7                # 創造性バランス
    max_tokens: 4096               # 最大トークン数
    context_window: 8192            # コンテキストウィンドウ
    
# 推論パイプライン
1. ユーザー入力受付
2. 人格に応じたプロンプト適用
3. Ollama APIで推論実行
4. レスポンス処理・整形
5. 音声合成・出力
```

### 🔍 知識検索システム
```python
# RAG検索要件
class KnowledgeSystem:
    # データソース
    sources: [
        "Excelファイル (openpyxl)",
        "PDFファイル (PyMuPDF)", 
        "Webコンテンツ (requests)",
        "ローカルドキュメント"
    ]
    
    # 処理フロー
    1. ドキュメント読み込み → チャンク分割
    2. SentenceTransformerで埋め込み生成
    3. FAISSでベクトルインデックス作成
    4. 類似度検索 → Top-K結果取得
    5. LLMに知識を注入して回答生成
    
    # 検索性能要件
    - 応答時間: < 2秒
    - 検索精度: Top-5 > 80%
    - 更新頻度: リアルタイム
```

### 🎵 音声処理システム
```python
# 音声認識要件
class VoiceRecognition:
    engine: "faster-whisper"        # 高速音声認識
    model: "base"                 # バランスモデル
    language: "ja"                 # 日本語対応
    real_time: True                # リアルタイム処理
    
# 音声合成要件  
class VoiceSynthesis:
    engine: "pyttsx3"             # オフラインTTS
    voice: "female"                 # 女性音声
    rate: 200                      # 話速
    volume: 0.9                    # 音量
```

---

## 🔧 検証・自己修復システム

### 🚀 起動時自己診断
```python
class StartupSelfCheck:
    # 診断項目
    checks = [
        "Ollama接続確認",
        "faster-whisper動作確認", 
        "Pythonライブラリ依存確認",
        "PHP実行環境確認",
        "VRMファイル存在確認",
        "ディスク容量確認",
        "メモリ使用量確認"
    ]
    
    # 自動修復機能
    auto_fixes = [
        "pip install [不足ライブラリ]",
        "winget install PHP",
        "ollama pull [モデル]",
        "PATH環境変数設定"
    ]
    
    # 診断結果レポート
    - 成功/警告/エラー分類
    - 詳細なエラーメッセージ
    - 修復履歴の記録
```

### 🔍 コード自動検証
```python
class AutoVerificationLoop:
    # 検証ステップ
    verification_steps = [
        "1. 静的解析 (AST構文チェック)",
        "2. サンドボックス実行",
        "3. エラー検出・分析",
        "4. 自動修正 (最大3回)",
        "5. 最終検証・実行"
    ]
    
    # 対応言語
    supported_languages = ["python", "javascript", "php"]
    
    # 修正戦略
    fix_strategies = [
        "インデントエラー修正",
        "未定義変数追加",
        "ImportError対応",
        "構文エラー修正",
        "論理エラー改善"
    ]
```

---

## 🎨 UI/UX要件

### 🖥️ Streamlitインターフェース
```python
# メインレイアウト
st.set_page_config(
    page_title="AI Agent System",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# サイドバー構成
sidebar_sections = [
    "🤖 AI人格切り替え",
    "🔍 起動時診断", 
    "🔧 コード検証",
    "📚 知識ベース管理",
    "🎵 音声設定",
    "🎨 VRMアバター制御",
    "🌐 ネットワーク設定"
]

# メインエリア
main_sections = [
    "💬 チャットインターフェース",
    "📊 システム状態ダッシュボード", 
    "🎨 Web Canvasプレビュー",
    "📋 プロジェクトファイル管理",
    "⚙️ 設定・設定"
]
```

### 🎨 Web Canvasプレビュー
```html
<!-- リアルタイムWeb開発環境 -->
<div id="web-canvas">
    <iframe id="preview-frame"></iframe>
    <div id="control-panel">
        <button onclick="runCode()">▶️ 実行</button>
        <button onclick="refresh()">🔄 更新</button>
        <button onclick="screenshot()">📸 スクリーンショット</button>
    </div>
</div>

<!-- 機能要件 -->
- HTML/CSS/JSリアルタイム編集
- ライブプレビュー表示
- エディタ構文ハイライト
- ファイル自動保存
- エラー検出・表示
```

### 🤖 VRMアバター表示
```javascript
// Three.js + three-vrm連携
class VRMAvatar {
    constructor() {
        this.model = "avatar.vrm";
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera();
        this.renderer = new THREE.WebGLRenderer();
    }
    
    // 表情制御
    setExpression(expression) {
        // happy, joy, neutral, sad, angry
    }
    
    // アニメーション制御
    setMotion(motion) {
        // idle, talking, thinking, greeting
    }
    
    // 人格連携
    updatePersonality(personality) {
        const expressions = {
            "friend": "happy",
            "copy": "joy", 
            "expert": "neutral"
        };
        this.setExpression(expressions[personality]);
    }
}
```

---

## 📊 データベース設計

### 🗃️ パーソナライズDB
```json
{
    "conversations": [
        {
            "timestamp": "2026-01-13T12:00:00Z",
            "user": "ユーザー入力",
            "ai": "AI応答",
            "personality": "friend",
            "context": "会話コンテキスト"
        }
    ],
    "user_profile": {
        "name": "ユーザー名",
        "os": "Windows 11",
        "tech_stack": ["Python", "JavaScript"],
        "preferences": ["Web開発", "AI"],
        "projects": ["プロジェクト履歴"],
        "last_updated": "2026-01-13T12:00:00Z"
    },
    "learning_data": {
        "common_questions": ["よくある質問"],
        "preferred_responses": ["好まれる応答スタイル"],
        "technical_level": "intermediate"
    }
}
```

### 📚 知識ベース構造
```python
class KnowledgeBase:
    def __init__(self):
        self.documents = []      # ドキュメントリスト
        self.embeddings = []     # 埋め込みベクトル
        self.index = None        # FAISSインデックス
        
    def add_document(self, doc_type, content, metadata):
        # ドキュメント追加処理
        pass
        
    def search(self, query, top_k=5):
        # 類似度検索
        pass
        
    def update_index(self):
        # インデックス再構築
        pass
```

---

## 🔌 APIエンドポイント仕様

### 🌐 FastAPIルート定義
```python
# 静的ファイル配信
@app.get("/static/{file_path:path}")
async def serve_static_file(file_path: str):
    return FileResponse(f"static/{file_path}")

# VRMファイル配信
@app.get("/avatar.vrm")
async def serve_vrm():
    return FileResponse("static/avatar.vrm")

# AIチャットAPI
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # 人格に応じた処理
    response = await process_chat(request)
    return {"response": response, "personality": current_personality}

# 音声認識API
@app.post("/api/speech-to-text")
async def speech_to_text(audio: UploadFile):
    text = await transcribe_audio(audio)
    return {"text": text}

# コード検証API
@app.post("/api/verify-code")
async def verify_code_endpoint(request: CodeRequest):
    result = await verify_code_safely(request.code, request.language)
    return {"result": result}
```

---

## 🛡️ セキュリティ要件

### 🔒 データ保護
```python
# 入力検証
class InputValidation:
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        # XSS対策
        text = html.escape(text)
        # SQLインジェクション対策
        text = re.sub(r"[;--]", "", text)
        # 長さ制限
        return text[:10000]

# ファイルアクセス制御
class FileSecurity:
    ALLOWED_EXTENSIONS = ['.py', '.js', '.html', '.css', '.md']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        # 拡張子チェック
        # パストラバーサル対策
        # サイズ制限
        return True
```

### 🚫 エラーハンドリング
```python
class ErrorHandler:
    @staticmethod
    def handle_api_error(error: Exception) -> dict:
        return {
            "error": True,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }
    
    @staticmethod
    def handle_model_error(error: Exception) -> str:
        # モデルエラーメッセージ
        return "申し訳ありません。AIモデルでエラーが発生しました。"
```

---

## 📈 パフォーマンス要件

### ⚡ 応答性能
| 機能 | 目標応答時間 | 許容遅延 |
|------|--------------|----------|
| LLM推論 | < 3秒 | 5秒 |
| 音声認識 | < 2秒 | 3秒 |
| 知識検索 | < 1秒 | 2秒 |
| UI応答 | < 500ms | 1秒 |
| ファイル保存 | < 1秒 | 2秒 |

### 💾 メモリ使用量
```python
# メモリ制限
MEMORY_LIMITS = {
    "llm_model": "4GB",           # LLMモデル
    "knowledge_base": "2GB",       # 知識ベース
    "voice_processing": "1GB",     # 音声処理
    "ui_components": "500MB"        # UIコンポーネント
}

# メモリ監視
def monitor_memory_usage():
    import psutil
    memory = psutil.virtual_memory()
    return {
        "used": f"{memory.percent}%",
        "available": f"{memory.available / (1024**3):.2f}GB"
    }
```

### 🔄 並列処理
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 非同期処理要件
async def process_user_request(request):
    tasks = [
        process_voice_input(request.audio),
        search_knowledge(request.text),
        generate_llm_response(request.text),
        update_vrm_avatar(request.personality)
    ]
    results = await asyncio.gather(*tasks)
    return combine_results(results)
```

---

## 🚀 デプロイ要件

### 📦 ビルドプロセス
```bash
# 1. 依存関係インストール
pip install -r requirements.txt

# 2. Ollamaモデルダウンロード
ollama pull llama3.1:8b

# 3. PHP環境確認
php --version

# 4. アプリケーション起動
streamlit run app.py

# 5. APIサーバー起動 (別プロセス)
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

### 🐳 実行環境
```yaml
# 開発環境
development:
  python: "3.10+"
  os: "Windows 11 / macOS / Linux"
  memory: "8GB+"
  storage: "10GB+"
  
# 本番環境
production:
  server: "FastAPI + Uvicorn"
  database: "SQLite (ファイルベース)"
  cdn: "ローカル静的ファイル配信"
  monitoring: "システムログ + パフォーマンス監視"
```

---

## 🧪 テスト要件

### 🧪 単体テスト
```python
# 機能テスト項目
test_cases = [
    "LLM推論テスト",
    "音声認識テスト", 
    "人格切り替えテスト",
    "知識検索テスト",
    "コード検証テスト",
    "VRMアバター表示テスト",
    "Web Canvasプレビューテスト",
    "APIエンドポイントテスト"
]

# テスト自動化
def run_unit_tests():
    for test in test_cases:
        result = execute_test(test)
        assert result.success, f"テスト失敗: {test.name}"
```

### 🔍 統合テスト
```python
# E2Eテストシナリオ
scenarios = [
    "ユーザー登録 → パーソナライズ → AI対話",
    "Excelアップロード → 知識検索 → 専門家回答",
    "コード生成 → 自動検証 → 実行確認",
    "人格切り替え → VRM表情変更 → 音声キャラ変更"
]
```

---

## 📋 開発手順

### 🔄 開発フロー
```
1. 📁 環境構築
   ├── Python 3.10+ インストール
   ├── Gitリポジトリクローン
   ├── 仮想環境作成 (venv)
   └── 依存関係インストール

2. 🤖 AIモデル準備
   ├── Ollamaインストール
   ├── llama3.1:8bモデルダウンロード
   └── モデル動作確認

3. 🐘 PHP環境構築
   ├── PHP 8.5+ インストール
   ├── 拡張モジュール確認
   └── CLI動作テスト

4. 📁 プロジェクトセットアップ
   ├── 必須ファイル配置
   ├── VRMアバター設置
   ├── 知識ベース準備
   └── 権限設定確認

5. 🚀 アプリケーション起動
   ├── Streamlitアプリ起動
   ├── FastAPIサーバー起動
   ├── 機能テスト実行
   └── ブラウザで動作確認

6. ✅ 動作検証
   ├── 全機能動作テスト
   ├── パフォーマンス測定
   ├── エラーハンドリング確認
   └── ユーザビリティテスト
```

---

## 📚 付録

### 🔧 環境変数設定
```bash
# .envファイル例
OLLAMA_MODEL=llama3.1:8b
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
VOICE_RATE=200
VOICE_VOLUME=0.9
VRM_MODEL_PATH=./static/avatar.vrm
KNOWLEDGE_BASE_PATH=./knowledge_base
LOG_LEVEL=INFO
```

### 📝 コーディング規約
```python
# PEP 8 準拠
# 型ヒント使用 (Type Python)
# ドキュメンテーション文字列
# エラーハンドリング統一
# 単体テスト必須
# セキュリティ考慮
```

### 🐛 トラブルシューティング
| 問題 | 原因 | 解決策 |
|------|------|--------|
| Ollama接続エラー | サービス未起動 | `ollama serve` 実行 |
| メモリ不足 | 大容量モデル | llama3.1:8b使用 |
| 音声認識精度 | マイク設定 | 音声入力デバイス確認 |
| VRM表示されない | ファイルパス | `./static/avatar.vrm` 確認 |
| Pythonライブラリエラー | 依存関係 | `pip install -r requirements.txt` |
| PHP実行エラー | PATH設定 | 環境変数確認 |

---

## 📞 サポート情報

### 📧 技術サポート
- **ドキュメント**: 各モジュールにdocstring実装
- **ログレベル**: DEBUG, INFO, WARNING, ERROR
- **エラーレポート**: 詳細なスタックトレース
- **ヘルスチェック**: `/api/health` エンドポイント

### 📈 パフォーマンス監視
- **応答時間監視**: 各APIエンドポイントの処理時間
- **リソース使用量**: CPU、メモリ、ディスク使用率
- **エラーレート**: エラー発生頻度・種類
- **ユーザー満足度**: レスポンス品質の定性的評価

---

*本仕様書は、AIエージェントシステムをゼロから構築するための完全な技術文書です。すべての要件を満たすことで、高度なAIアシスタントシステムが実現可能となります。*
