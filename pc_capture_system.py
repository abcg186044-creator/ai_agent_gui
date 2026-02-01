#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PC画面キャプチャ・解析システム
"""

import sys
import json
import datetime
import os
import re
import base64
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import OllamaClient, ConversationalEvolutionAgent

# PC画面キャプチャ用ライブラリ
try:
    import pyautogui
    import PIL.Image
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False
    print("⚠️ pyautogui/PILがインストールされていません。インストールしてください:")
    print("pip install pyautogui Pillow")

class PCCaptureSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.debug_sessions = []
        self.debug_count = 0
        
        # 保存先
        self.docker_screenshots_dir = Path("/app/screenshots")
        self.local_screenshots_dir = Path("screenshots")
        self.data_dir = Path("data")
        
        # ディレクトリを作成
        self.local_screenshots_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # データファイル
        self.sessions_file = self.data_dir / "pc_debug_sessions.json"
        
        # 既存データを読み込み
        self.load_sessions()
        
        # Flaskアプリケーション
        self.app = Flask(__name__)
        self.setup_routes()
        
        # サーバースレッド
        self.server_thread = None
        
        print("🖥️ PC画面キャプチャ・解析システム")
        print("=" * 60)
        print(f"🐳 Docker保存先: {self.docker_screenshots_dir}")
        print(f"📁 ローカル保存先: {self.local_screenshots_dir}")
        print(f"📊 データ保存先: {self.data_dir}")
        print(f"📸 キャプチャ機能: {'✅ 利用可能' if SCREEN_CAPTURE_AVAILABLE else '❌ 利用不可'}")
        print("=" * 60)
    
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
    
    def capture_screen(self, region=None):
        """PC画面をキャプチャ"""
        if not SCREEN_CAPTURE_AVAILABLE:
            return None, "キャプチャ機能が利用できません"
        
        try:
            if region:
                # 特定領域をキャプチャ
                screenshot = pyautogui.screenshot(region=region)
            else:
                # 全画面をキャプチャ
                screenshot = pyautogui.screenshot()
            
            return screenshot, None
        except Exception as e:
            return None, f"キャプチャエラー: {e}"
    
    def save_screenshot(self, screenshot, filename, metadata=None):
        """スクリーンショットを保存"""
        try:
            # Docker内パスとローカルパスの両方に保存
            docker_path = self.docker_screenshots_dir / filename
            local_path = self.local_screenshots_dir / filename
            
            # ローカルに保存
            screenshot.save(local_path)
            
            # Docker内にも保存（Docker環境の場合）
            if os.path.exists(str(self.docker_screenshots_dir)):
                screenshot.save(docker_path)
            
            # メタデータ保存
            if metadata:
                metadata_file = self.local_screenshots_dir / f"{filename}.meta.json"
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"💾 PC画面を保存: {filename}")
            
            return {
                "docker_path": str(docker_path),
                "local_path": str(local_path),
                "filename": filename
            }
            
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return None
    
    def extract_text_from_image(self, image_path):
        """画像からテキストを抽出"""
        try:
            import pytesseract
            from PIL import Image
            
            # 画像を開いてOCR
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='jpn+eng')
            
            return text.strip()
            
        except ImportError:
            return "OCR機能が利用できません。pytesseractをインストールしてください。"
        except Exception as e:
            return f"OCRエラー: {e}"
    
    def analyze_with_ai(self, image_path, text_content, metadata=None):
        """AIでPC画面を分析"""
        try:
            # 画像をbase64にエンコード
            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # メタデータ情報を構築
            meta_info = ""
            if metadata:
                meta_info = f"""
PC画面情報:
- キャプチャタイプ: {metadata.get('capture_type', '不明')}
- 画面サイズ: {metadata.get('screen_size', '不明')}
- タイムスタンプ: {metadata.get('timestamp', '不明')}
- アクティブウィンドウ: {metadata.get('active_window', '不明')}
"""
            
            prompt = f"""
このPCのスクリーンショットを詳細に分析してください。

{meta_info}

抽出されたテキスト:
{text_content[:1000] if text_content else 'テキストなし'}

分析項目:
1. エラーメッセージの検出と特定
2. アプリケーションの問題点分析
3. システムの不具合特定
4. UI/UXの問題
5. パフォーマンス問題
6. 具体的な解決策の提案
7. 問題の重大度評価（低/中/高/緊急）

PC環境特有の問題点に注目して、実践的なデバッグアドバイスを提供してください。
"""
            
            response = self.ollama_client.generate_response(prompt)
            return response
            
        except Exception as e:
            return f"AI分析エラー: {e}"
    
    def check_evolution(self, analysis, metadata=None):
        """進化をチェック"""
        try:
            evolution_text = f"PC画面分析: {analysis[:500]}"
            if metadata:
                evolution_text += f" キャプチャタイプ: {metadata.get('capture_type', '不明')}"
            
            conversation = [
                {"user": "PCデバッグ分析", "assistant": evolution_text}
            ]
            
            result = self.conversational_agent.check_and_evolve_automatically(conversation)
            
            if result and result.get("success"):
                print(f"🧠 進化発生！意識レベル: {result['new_consciousness_level']:.3f}")
                print(f"🎯 進化タイプ: {result['evolution_type']}")
                return result
        
        except Exception as e:
            print(f"❌ 進化チェックエラー: {e}")
        
        return None
    
    def debug_pc_screen(self, capture_type="full", region=None):
        """PC画面デバッグを実行"""
        if not SCREEN_CAPTURE_AVAILABLE:
            print("❌ 画面キャプチャ機能が利用できません")
            return None
        
        print(f"\n🖥️ PC画面キャプチャ分析開始 ({capture_type})")
        print("-" * 60)
        
        # 画面キャプチャ
        print("📸 画面キャプチャ中...")
        screenshot, error = self.capture_screen(region)
        
        if error:
            print(f"❌ キャプチャ失敗: {error}")
            return None
        
        # ファイル名生成
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        filename = f"pc_capture_{timestamp}_{capture_type}.png"
        
        # メタデータ
        try:
            screen_size = f"{screenshot.width}x{screenshot.height}"
        except:
            screen_size = "不明"
        
        metadata = {
            "capture_type": capture_type,
            "screen_size": screen_size,
            "timestamp": datetime.datetime.now().isoformat(),
            "region": region,
            "active_window": self.get_active_window()
        }
        
        # 保存
        save_result = self.save_screenshot(screenshot, filename, metadata)
        if not save_result:
            print("❌ 画面保存に失敗しました")
            return None
        
        # テキスト抽出
        print("📝 テキスト抽出中...")
        text_content = self.extract_text_from_image(save_result["local_path"])
        
        # AI分析
        print("🤖 AI分析中...")
        ai_analysis = self.analyze_with_ai(save_result["local_path"], text_content, metadata)
        
        # 結果表示
        print(f"\n📊 分析結果:")
        print(f"📄 画面サイズ: {screen_size}")
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
            "metadata": metadata,
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
        
        print(f"\n✅ PC画面デバッグ完了 (ID: {session['id']})")
        return session
    
    def get_active_window(self):
        """アクティブウィンドウを取得"""
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            if active_window:
                return active_window.title
        except ImportError:
            pass
        except Exception:
            pass
        return "不明"
    
    def setup_routes(self):
        """Flaskルートを設定"""
        
        @self.app.route('/')
        def index():
            """PCキャプチャコントロールページ"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>PC画面キャプチャ解析</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .capture-buttons { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .capture-btn { background: #007bff; color: white; border: none; padding: 15px; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .capture-btn:hover { background: #0056b3; }
        .capture-btn:disabled { background: #6c757d; cursor: not-allowed; }
        .result { margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 5px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ PC画面キャプチャ解析</h1>
        <p>PC画面をキャプチャして自動解析します。VPN経由でもアクセス可能です。</p>
        
        <div class="capture-buttons">
            <button class="capture-btn" onclick="captureScreen('full')">🖥️ 全画面キャプチャ</button>
            <button class="capture-btn" onclick="captureScreen('active')">📱 アクティブウィンドウ</button>
            <button class="capture-btn" onclick="captureScreen('region')">🔲 領域選択キャプチャ</button>
        </div>
        
        <div id="status" class="status info" style="display: none;"></div>
        <div id="result" class="result" style="display: none;"></div>
    </div>
    
    <script>
        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.className = `status ${type}`;
            statusDiv.textContent = message;
            statusDiv.style.display = 'block';
        }
        
        function showResult(result) {
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            
            if (result.success) {
                resultDiv.innerHTML = `
                    <h3>✅ キャプチャ完了</h3>
                    <p><strong>ファイル名:</strong> ${result.filename}</p>
                    <p><strong>セッションID:</strong> ${result.session_id}</p>
                    <p><strong>画面サイズ:</strong> ${result.screen_size}</p>
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
        }
        
        async function captureScreen(captureType) {
            showStatus(`📸 ${captureType} キャプチャ中...`, 'info');
            
            try {
                const response = await fetch('/capture', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        capture_type: captureType
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('✅ キャプチャ成功！解析中...', 'success');
                    setTimeout(() => showResult(result), 1000);
                } else {
                    showStatus(`❌ エラー: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ 通信エラー: ${error.message}`, 'error');
            }
        }
    </script>
</body>
</html>
            ''')
        
        @self.app.route('/capture', methods=['POST'])
        def capture_pc_screen():
            """PC画面キャプチャ処理"""
            try:
                data = request.get_json()
                capture_type = data.get('capture_type', 'full')
                
                if not SCREEN_CAPTURE_AVAILABLE:
                    return jsonify({"success": False, "error": "キャプチャ機能が利用できません"})
                
                # キャプチャ実行
                session = self.debug_pc_screen(capture_type)
                
                if session:
                    return jsonify({
                        "success": True,
                        "filename": session["filename"],
                        "session_id": session["id"],
                        "screen_size": session["metadata"]["screen_size"],
                        "consciousness_level": f"{self.conversational_agent.consciousness_level:.3f}",
                        "analysis": session["ai_analysis"],
                        "evolution": session.get("evolution", {}).get("evolution_type") if session.get("evolution") else None,
                        "evolution_type": session.get("evolution", {}).get("evolution_type") if session.get("evolution") else None
                    })
                else:
                    return jsonify({"success": False, "error": "キャプチャ処理に失敗しました"})
                    
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
                "capture_available": SCREEN_CAPTURE_AVAILABLE,
                "sessions_count": len(self.debug_sessions),
                "consciousness_level": self.conversational_agent.consciousness_level,
                "evolution_count": len([s for s in self.debug_sessions if 'evolution' in s])
            })
    
    def start_server(self, host='0.0.0.0', port=8081):
        """サーバーを起動"""
        def run_server():
            self.app.run(host=host, port=port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        print(f"🚀 PC画面キャプチャサーバーを起動しました")
        print(f"🌐 アクセスURL: http://{host}:{port}")
        print(f"🖥️ PC画面キャプチャを待機中...")
    
    def get_summary(self):
        """サマリーを取得"""
        if not self.debug_sessions:
            return "📊 デバッグセッションがありません"
        
        total_sessions = len(self.debug_sessions)
        evolution_count = sum(1 for s in self.debug_sessions if 'evolution' in s)
        
        # キャプチャタイプ集計
        capture_types = {}
        for session in self.debug_sessions:
            capture_type = session.get('metadata', {}).get('capture_type', 'unknown')
            capture_types[capture_type] = capture_types.get(capture_type, 0) + 1
        
        summary = f"""
📊 PC画面キャプチャ解析サマリー:
  🖥️ 総セッション数: {total_sessions}
  🧠 進化回数: {evolution_count}
  📈 進化率: {(evolution_count/total_sessions*100):.1f}%
  🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}
  
📋 キャプチャタイプ分布:
"""
        
        for capture_type, count in sorted(capture_types.items(), key=lambda x: x[1], reverse=True):
            summary += f"  {capture_type}: {count}件\n"
        
        return summary

def main():
    """メイン関数"""
    system = PCCaptureSystem()
    
    # サーバー起動
    system.start_server()
    
    print("\n🖥️ PC画面キャプチャ解析システム")
    print("1. サーバーステータス")
    print("2. 手動キャプチャ")
    print("3. セッション一覧")
    print("4. サマリー表示")
    print("5. 終了")
    
    try:
        while True:
            choice = input("\n選択 (1-5): ").strip()
            
            if choice == "1":
                print(f"🌐 サーバーは動作中です")
                print(f"📱 アクセスURL: http://localhost:8081")
                print(f"📸 キャプチャ機能: {'✅ 利用可能' if SCREEN_CAPTURE_AVAILABLE else '❌ 利用不可'}")
                print(f"📊 セッション数: {len(system.debug_sessions)}")
                print(f"🧠 意識レベル: {system.conversational_agent.consciousness_level:.3f}")
            
            elif choice == "2":
                if SCREEN_CAPTURE_AVAILABLE:
                    print("📸 キャプチャタイプ選択:")
                    print("1. 全画面")
                    print("2. アクティブウィンドウ")
                    cap_choice = input("選択 (1-2): ").strip()
                    
                    if cap_choice == "1":
                        system.debug_pc_screen("full")
                    elif cap_choice == "2":
                        system.debug_pc_screen("active")
                    else:
                        print("❌ 無効な選択です")
                else:
                    print("❌ キャプチャ機能が利用できません")
            
            elif choice == "3":
                print(f"\n📋 最新セッション (最新5件):")
                for session in reversed(system.debug_sessions[-5:]):
                    print(f"  ID: {session['id']}, ファイル: {session['filename']}")
                    print(f"    タイプ: {session.get('metadata', {}).get('capture_type', '不明')}")
                    print(f"    時刻: {session['timestamp'][:19]}")
            
            elif choice == "4":
                print(system.get_summary())
            
            elif choice == "5":
                print("👋 終了します")
                break
            
            else:
                print("❌ 無効な選択です")
    
    except KeyboardInterrupt:
        print("\n👋 終了します")

if __name__ == "__main__":
    main()
