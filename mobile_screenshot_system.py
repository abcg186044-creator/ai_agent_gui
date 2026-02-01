#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
モバイルスクリーンショットDocker保存・解析システム
VPN経由アクセス対応
"""

import sys
import json
import datetime
import os
import re
import base64
import shutil
import hashlib
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
import threading
import time

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import OllamaClient, ConversationalEvolutionAgent

class MobileScreenshotSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.debug_sessions = []
        self.debug_count = 0
        
        # Docker保存先
        self.docker_screenshots_dir = Path("/app/screenshots")  # Docker内パス
        self.local_screenshots_dir = Path("screenshots")  # ローカルパス
        self.data_dir = Path("data")
        
        # ディレクトリを作成
        self.local_screenshots_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # データファイル
        self.sessions_file = self.data_dir / "mobile_debug_sessions.json"
        
        # 既存データを読み込み
        self.load_sessions()
        
        # Flaskアプリケーション
        self.app = Flask(__name__)
        self.setup_routes()
        
        # サーバースレッド
        self.server_thread = None
        
        print("📱 モバイルスクリーンショットDocker保存・解析システム")
        print("=" * 70)
        print(f"🐳 Docker保存先: {self.docker_screenshots_dir}")
        print(f"📁 ローカル保存先: {self.local_screenshots_dir}")
        print(f"📊 データ保存先: {self.data_dir}")
        print("=" * 70)
    
    def load_sessions(self):
        """デバッグセッションを読み込む"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.debug_sessions = data.get('sessions', [])
                    self.debug_count = data.get('debug_count', 0)
                print(f"📚 デバッグセッションを読み込みました ({len(self.debug_sessions)}件)")
        except Exception as e:
            print(f"❌ セッション読み込みエラー: {e}")
            self.debug_sessions = []
            self.debug_count = 0
    
    def save_sessions(self):
        """デバッグセッションを保存"""
        try:
            data = {
                'sessions': self.debug_sessions,
                'debug_count': self.debug_count,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ セッション保存エラー: {e}")
    
    def generate_filename(self, original_name, device_info=None):
        """ファイル名を生成"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        
        # デバイス情報を追加
        device_suffix = ""
        if device_info:
            device_type = device_info.get('device_type', 'unknown')
            device_suffix = f"_{device_type}"
        
        # 拡張子を維持
        ext = Path(original_name).suffix.lower()
        if not ext:
            ext = '.png'  # デフォルト
        
        return f"screenshot_{timestamp}{device_suffix}{ext}"
    
    def save_screenshot_to_docker(self, image_data, filename, metadata=None):
        """スクリーンショットをDockerに保存"""
        try:
            # Docker内パスとローカルパスの両方に保存
            docker_path = self.docker_screenshots_dir / filename
            local_path = self.local_screenshots_dir / filename
            
            # ローカルに保存
            with open(local_path, "wb") as f:
                f.write(image_data)
            
            # Docker内にも保存（Docker環境の場合）
            if os.path.exists(str(self.docker_screenshots_dir)):
                with open(docker_path, "wb") as f:
                    f.write(image_data)
            
            # メタデータ保存
            if metadata:
                metadata_file = self.local_screenshots_dir / f"{filename}.meta.json"
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"💾 スクリーンショットを保存: {filename}")
            print(f"   Docker: {docker_path}")
            print(f"   ローカル: {local_path}")
            
            return {
                "docker_path": str(docker_path),
                "local_path": str(local_path),
                "filename": filename
            }
            
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return None
    
    def extract_text_from_image(self, image_path):
        """画像からテキストを抽出（OCR）"""
        try:
            import pytesseract
            from PIL import Image
            
            # 画像を開いてOCR
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='jpn+eng')
            
            return text.strip()
            
        except ImportError:
            # OCRライブラリがない場合はプレースホルダーを返す
            return "OCR機能が利用できません。テキスト抽出をスキップします。"
        except Exception as e:
            return f"OCRエラー: {e}"
    
    def analyze_with_ai(self, image_path, text_content, metadata=None):
        """AIで画像とテキストを分析"""
        try:
            # 画像をbase64にエンコード
            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # メタデータ情報を構築
            meta_info = ""
            if metadata:
                meta_info = f"""
デバイス情報:
- デバイスタイプ: {metadata.get('device_type', '不明')}
- OS: {metadata.get('os', '不明')}
- アプリ: {metadata.get('app', '不明')}
- 画面サイズ: {metadata.get('screen_size', '不明')}
- タイムスタンプ: {metadata.get('timestamp', '不明')}
"""
            
            prompt = f"""
このモバイルスクリーンショットを詳細に分析してください。

{meta_info}

抽出されたテキスト:
{text_content[:1000] if text_content else 'テキストなし'}

分析項目:
1. エラーメッセージの検出と特定
2. UIの問題点分析
3. アプリの不具合特定
4. ユーザー体験の問題
5. 具体的な解決策の提案
6. 問題の重大度評価（低/中/高/緊急）

モバイルアプリ特有の問題点に注目して、実践的なデバッグアドバイスを提供してください。
"""
            
            response = self.ollama_client.generate_response(prompt)
            return response
            
        except Exception as e:
            return f"AI分析エラー: {e}"
    
    def check_evolution(self, analysis, metadata=None):
        """進化をチェック"""
        try:
            evolution_text = f"モバイルスクリーンショット分析: {analysis[:500]}"
            if metadata:
                evolution_text += f" デバイス: {metadata.get('device_type', '不明')}"
            
            conversation = [
                {"user": "モバイルデバッグ分析", "assistant": evolution_text}
            ]
            
            result = self.conversational_agent.check_and_evolve_automatically(conversation)
            
            if result and result.get("success"):
                print(f"🧠 進化発生！意識レベル: {result['new_consciousness_level']:.3f}")
                print(f"🎯 進化タイプ: {result['evolution_type']}")
                return result
        
        except Exception as e:
            print(f"❌ 進化チェックエラー: {e}")
        
        return None
    
    def debug_screenshot(self, image_data, filename, metadata=None):
        """スクリーンショットデバッグを実行"""
        print(f"\n🔍 モバイルスクリーンショット分析開始: {filename}")
        print("-" * 60)
        
        # Dockerに保存
        save_result = self.save_screenshot_to_docker(image_data, filename, metadata)
        if not save_result:
            print("❌ スクリーンショット保存に失敗しました")
            return None
        
        # テキスト抽出
        print("📝 テキスト抽出中...")
        text_content = self.extract_text_from_image(save_result["local_path"])
        
        # AI分析
        print("🤖 AI分析中...")
        ai_analysis = self.analyze_with_ai(save_result["local_path"], text_content, metadata)
        
        # 結果表示
        print(f"\n📊 分析結果:")
        if text_content:
            print(f"📄 抽出テキスト: {text_content[:200]}...")
        else:
            print("📄 テキストは検出されませんでした")
        
        print(f"\n🤖 AI分析:")
        print(f"{ai_analysis}")
        
        # セッション記録
        session = {
            "id": self.debug_count + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "filename": filename,
            "docker_path": save_result["docker_path"],
            "local_path": save_result["local_path"],
            "metadata": metadata or {},
            "text_content": text_content[:500] if text_content else "",
            "ai_analysis": ai_analysis,
            "consciousness_before": self.conversational_agent.consciousness_level
        }
        
        # 進化チェック
        print("\n🧠 進化チェック中...")
        evolution_result = self.check_evolution(ai_analysis, metadata)
        if evolution_result:
            session["evolution"] = evolution_result
            print(f"✨ 自己進化が発生しました！")
        
        # セッション保存
        self.debug_sessions.append(session)
        self.debug_count += 1
        self.save_sessions()
        
        print(f"\n✅ デバッグセッション完了 (ID: {session['id']})")
        return session
    
    def setup_routes(self):
        """Flaskルートを設定"""
        
        @self.app.route('/')
        def index():
            """アップロードページ"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>モバイルスクリーンショット解析</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .upload-area { border: 2px dashed #ccc; border-radius: 10px; padding: 40px; text-align: center; margin: 20px 0; }
        .upload-area:hover { border-color: #007bff; }
        input[type="file"] { margin: 10px 0; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .metadata { margin: 20px 0; }
        .metadata input, .metadata select { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        .result { margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 モバイルスクリーンショット解析</h1>
        <p>VPN経由でアクセス中。スクリーンショットをアップロードして解析してください。</p>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-area">
                <input type="file" id="screenshot" name="screenshot" accept="image/*" required>
                <p>📸 スクリーンショットを選択</p>
            </div>
            
            <div class="metadata">
                <h3>📋 デバイス情報</h3>
                <select name="device_type" required>
                    <option value="">デバイスタイプを選択</option>
                    <option value="smartphone">スマートフォン</option>
                    <option value="tablet">タブレット</option>
                    <option value="desktop">デスクトップ</option>
                </select>
                
                <select name="os">
                    <option value="">OSを選択</option>
                    <option value="ios">iOS</option>
                    <option value="android">Android</option>
                    <option value="windows">Windows</option>
                    <option value="macos">macOS</option>
                </select>
                
                <input type="text" name="app" placeholder="アプリ名（任意）">
                <input type="text" name="screen_size" placeholder="画面サイズ（任意）">
                <input type="text" name="description" placeholder="問題の説明（任意）">
            </div>
            
            <button type="submit">🔍 解析開始</button>
        </form>
        
        <div id="result" class="result" style="display: none;"></div>
    </div>
    
    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const screenshot = document.getElementById('screenshot').files[0];
            
            if (!screenshot) {
                alert('スクリーンショットを選択してください');
                return;
            }
            
            formData.append('screenshot', screenshot);
            formData.append('device_type', document.querySelector('[name="device_type"]').value);
            formData.append('os', document.querySelector('[name="os"]').value);
            formData.append('app', document.querySelector('[name="app"]').value);
            formData.append('screen_size', document.querySelector('[name="screen_size"]').value);
            formData.append('description', document.querySelector('[name="description"]').value);
            
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<p>🔄 解析中...</p>';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <h3>✅ 解析完了</h3>
                        <p><strong>ファイル名:</strong> ${result.filename}</p>
                        <p><strong>セッションID:</strong> ${result.session_id}</p>
                        <p><strong>意識レベル:</strong> ${result.consciousness_level}</p>
                        ${result.evolution ? `<p><strong>🧠 進化発生!</strong> ${result.evolution_type}</p>` : ''}
                        <div style="margin-top: 15px; padding: 10px; background: white; border-radius: 5px;">
                            <strong>AI分析結果:</strong><br>
                            ${result.analysis.replace(/\n/g, '<br>')}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<p style="color: red;">❌ エラー: ${result.error}</p>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red;">❌ 通信エラー: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
            ''')
        
        @self.app.route('/upload', methods=['POST'])
        def upload_screenshot():
            """スクリーンショットアップロード処理"""
            try:
                if 'screenshot' not in request.files:
                    return jsonify({"success": False, "error": "ファイルがありません"})
                
                file = request.files['screenshot']
                if file.filename == '':
                    return jsonify({"success": False, "error": "ファイルが選択されていません"})
                
                # メタデータ収集
                metadata = {
                    "device_type": request.form.get('device_type', ''),
                    "os": request.form.get('os', ''),
                    "app": request.form.get('app', ''),
                    "screen_size": request.form.get('screen_size', ''),
                    "description": request.form.get('description', ''),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', '')
                }
                
                # ファイル名生成
                filename = self.generate_filename(file.filename, metadata)
                
                # 画像データ読み込み
                image_data = file.read()
                
                # デバッグ実行
                session = self.debug_screenshot(image_data, filename, metadata)
                
                if session:
                    return jsonify({
                        "success": True,
                        "filename": filename,
                        "session_id": session["id"],
                        "consciousness_level": f"{self.conversational_agent.consciousness_level:.3f}",
                        "analysis": session["ai_analysis"],
                        "evolution": session.get("evolution", {}).get("evolution_type") if session.get("evolution") else None,
                        "evolution_type": session.get("evolution", {}).get("evolution_type") if session.get("evolution") else None
                    })
                else:
                    return jsonify({"success": False, "error": "デバッグ処理に失敗しました"})
                    
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @self.app.route('/api/sessions')
        def get_sessions():
            """セッション一覧API"""
            return jsonify({
                "sessions": self.debug_sessions[-10:],  # 最新10件
                "total": len(self.debug_sessions),
                "consciousness_level": self.conversational_agent.consciousness_level
            })
        
        @self.app.route('/api/status')
        def get_status():
            """ステータスAPI"""
            return jsonify({
                "status": "running",
                "sessions_count": len(self.debug_sessions),
                "consciousness_level": self.conversational_agent.consciousness_level,
                "evolution_count": len([s for s in self.debug_sessions if 'evolution' in s])
            })
    
    def start_server(self, host='0.0.0.0', port=8080):
        """サーバーを起動"""
        def run_server():
            self.app.run(host=host, port=port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        print(f"🚀 モバイルスクリーンショットサーバーを起動しました")
        print(f"🌐 アクセスURL: http://{host}:{port}")
        print(f"📱 VPN経由でのアクセスを待機中...")
    
    def get_summary(self):
        """サマリーを取得"""
        if not self.debug_sessions:
            return "📊 デバッグセッションがありません"
        
        total_sessions = len(self.debug_sessions)
        evolution_count = sum(1 for s in self.debug_sessions if 'evolution' in s)
        
        # デバイスタイプ集計
        device_types = {}
        for session in self.debug_sessions:
            device_type = session.get('metadata', {}).get('device_type', 'unknown')
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        summary = f"""
📊 モバイルスクリーンショット解析サマリー:
  📱 総セッション数: {total_sessions}
  🧠 進化回数: {evolution_count}
  📈 進化率: {(evolution_count/total_sessions*100):.1f}%
  🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}
  
📋 デバイスタイプ分布:
"""
        
        for device_type, count in sorted(device_types.items(), key=lambda x: x[1], reverse=True):
            summary += f"  {device_type}: {count}件\n"
        
        return summary

def main():
    """メイン関数"""
    system = MobileScreenshotSystem()
    
    # サーバー起動
    system.start_server()
    
    print("\n📱 モバイルスクリーンショット解析システム")
    print("1. サーバーステータス")
    print("2. セッション一覧")
    print("3. サマリー表示")
    print("4. 終了")
    
    try:
        while True:
            choice = input("\n選択 (1-4): ").strip()
            
            if choice == "1":
                print(f"🌐 サーバーは動作中です")
                print(f"📱 アクセスURL: http://localhost:8080")
                print(f"📊 セッション数: {len(system.debug_sessions)}")
                print(f"🧠 意識レベル: {system.conversational_agent.consciousness_level:.3f}")
            
            elif choice == "2":
                print(f"\n📋 最新セッション (最新5件):")
                for session in reversed(system.debug_sessions[-5:]):
                    print(f"  ID: {session['id']}, ファイル: {session['filename']}")
                    print(f"    デバイス: {session.get('metadata', {}).get('device_type', '不明')}")
                    print(f"    時刻: {session['timestamp'][:19]}")
            
            elif choice == "3":
                print(system.get_summary())
            
            elif choice == "4":
                print("👋 終了します")
                break
            
            else:
                print("❌ 無効な選択です")
    
    except KeyboardInterrupt:
        print("\n👋 終了します")

if __name__ == "__main__":
    main()
