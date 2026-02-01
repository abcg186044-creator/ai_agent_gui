#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker対応スクリーンショット分析・デバッグ・自己進化システム
"""

import sys
import json
import datetime
import os
import re
import base64
import requests
from pathlib import Path

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import OllamaClient, ConversationalEvolutionAgent

class DockerDebugSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.debug_sessions = []
        self.debug_count = 0
        
        # Docker設定
        self.docker_api_url = "http://localhost:2375"  # Docker APIエンドポイント
        self.container_name = "debug-screenshots"
        self.image_name = "debug-screenshots"
        
        # データファイル
        self.sessions_file = Path("data/docker_debug_sessions.json")
        self.sessions_file.parent.mkdir(exist_ok=True)
        
        # screenshotsディレクトリを作成
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Dockerコンテナを準備
        self.setup_docker_container()
        
        print("🐳 Docker対応スクリーンショット分析・デバッグ・自己進化システム")
        print("=" * 70)
        print(f"📦 コンテナ名: {self.container_name}")
        print(f"🖼️  保存先: /screenshots (ホスト: {self.screenshots_dir})")
        print("=" * 70)
    
    def setup_docker_container(self):
        """Dockerコンテナをセットアップ"""
        try:
            # Docker APIが利用可能かチェック
            response = requests.get(f"{self.docker_api_url}/version")
            if response.status_code == 200:
                print("✅ Docker APIに接続成功")
                
                # コンテナが存在するかチェック
                containers = self.list_containers()
                container_exists = any(c.get('Names', [''])[0].lstrip('/') == self.container_name for c in containers)
                
                if not container_exists:
                    print(f"📦 コンテナ {self.container_name} を作成します...")
                    self.create_container()
                else:
                    print(f"✅ コンテナ {self.container_name} は既に存在します")
            else:
                print("⚠️ Docker APIに接続できません。ローカルモードで実行します")
                self.docker_available = False
                return
                
        except Exception as e:
            print(f"❌ Dockerセットアップエラー: {e}")
            print("💡 Dockerがインストールされていないか、起動していません")
            self.docker_available = False
            return
        
        self.docker_available = True
    
    def list_containers(self):
        """コンテナ一覧を取得"""
        try:
            response = requests.get(f"{self.docker_api_url}/containers/json?all=true")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ コンテナ一覧取得エラー: {e}")
        return []
    
    def create_container(self):
        """デバッグ用コンテナを作成"""
        try:
            # コンテナ作成
            container_config = {
                "Image": "alpine:latest",
                "Cmd": ["tail", "-f", "/dev/null"],
                "Name": self.container_name,
                "HostConfig": {
                    "Binds": {
                        str(Path.cwd() / "screenshots"): {
                            "bind": "/screenshots",
                            "mode": "rw"
                        }
                    }
                },
                "WorkingDir": "/screenshots"
            }
            
            response = requests.post(
                f"{self.docker_api_url}/containers/create",
                json=container_config
            )
            
            if response.status_code == 201:
                container_id = response.json()['Id']
                print(f"✅ コンテナ作成成功: {container_id[:12]}")
                
                # コンテナを起動
                start_response = requests.post(
                    f"{self.docker_api_url}/containers/{container_id}/start"
                )
                
                if start_response.status_code == 204:
                    print("✅ コンテナ起動成功")
                    
                    # screenshotsディレクトリを作成
                    self.create_screenshots_directory()
                else:
                    print("❌ コンテナ起動失敗")
            else:
                print(f"❌ コンテナ作成失敗: {response.status_code}")
                
        except Exception as e:
            print(f"❌ コンテナ作成エラー: {e}")
    
    def create_screenshots_directory(self):
        """screenshotsディレクトリを作成"""
        try:
            exec_config = {
                "Cmd": ["mkdir", "-p", "/screenshots"],
                "AttachStdout": True,
                "AttachStderr": True
            }
            
            response = requests.post(
                f"{self.docker_api_url}/containers/{self.container_name}/exec",
                json=exec_config
            )
            
            if response.status_code == 201:
                exec_id = response.json()['Id']
                
                # コマンド実行
                start_response = requests.post(
                    f"{self.docker_api_url}/exec/{exec_id}/start",
                    json={"Detach": False}
                )
                
                if start_response.status_code == 200:
                    print("✅ screenshotsディレクトリ作成成功")
                    
        except Exception as e:
            print(f"❌ ディレクトリ作成エラー: {e}")
    
    def save_screenshot_to_docker(self, image_path, filename=None):
        """スクリーンショットをDockerコンテナに保存"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            if not self.docker_available:
                # ローカル保存
                local_path = Path("screenshots") / filename
                local_path.parent.mkdir(exist_ok=True)
                
                with open(image_path, "rb") as src, open(local_path, "wb") as dst:
                    dst.write(src.read())
                
                print(f"💾 ローカル保存: {local_path}")
                return str(local_path)
            
            # Dockerコンテナにコピー
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Docker APIでファイルをコピー
            put_url = f"{self.docker_api_url}/containers/{self.container_name}/archive"
            params = {"path": f"/screenshots/{filename}"}
            
            response = requests.put(put_url, params=params, data=image_data)
            
            if response.status_code == 200:
                docker_path = f"/screenshots/{filename}"
                print(f"💾 Docker保存: {docker_path}")
                return docker_path
            else:
                print(f"❌ Docker保存失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return None
    
    def analyze_screenshot_with_ai(self, image_path):
        """AIでスクリーンショットを分析"""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            prompt = """
            このスクリーンショットを詳細に分析してください。
            
            分析項目:
            1. エラーメッセージの検出と特定
            2. 問題の根本原因の分析
            3. 具体的な解決策の提案
            4. 問題の重大度評価（低/中/高/緊急）
            5. 予防策の提案
            
            技術的な詳細を含めて、実践的なデバッグアドバイスを提供してください。
            """
            
            response = self.ollama_client.generate_response(prompt)
            return response
            
        except Exception as e:
            return f"AI分析エラー: {e}"
    
    def debug_screenshot(self, image_path):
        """スクリーンショットデバッグを実行"""
        print(f"\n🔍 スクリーンショット分析開始: {image_path}")
        print("-" * 50)
        
        # Dockerに保存
        saved_path = self.save_screenshot_to_docker(image_path)
        if not saved_path:
            print("❌ 画像保存に失敗しました")
            return None
        
        # AI分析
        print("🤖 AI分析中...")
        analysis = self.analyze_screenshot_with_ai(image_path)
        
        print(f"\n📊 分析結果:")
        print(f"{analysis}")
        
        # セッション記録
        session = {
            "id": self.debug_count + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "original_path": str(image_path),
            "docker_path": saved_path,
            "analysis": analysis,
            "consciousness_before": self.conversational_agent.consciousness_level,
            "docker_available": self.docker_available
        }
        
        # 進化チェック
        print("\n🧠 進化チェック中...")
        evolution_result = self.check_evolution(analysis)
        if evolution_result:
            session["evolution"] = evolution_result
            print(f"✨ 自己進化が発生しました！")
        
        # セッション保存
        self.debug_sessions.append(session)
        self.debug_count += 1
        self.save_sessions()
        
        print(f"\n✅ デバッグセッション完了 (ID: {session['id']})")
        return session
    
    def check_evolution(self, analysis):
        """進化をチェック"""
        try:
            # デバッグ分析を進化トリガーとして使用
            conversation = [
                {"user": "スクリーンショットデバッグ分析", "assistant": analysis}
            ]
            
            result = self.conversational_agent.check_and_evolve_automatically(conversation)
            
            if result and result.get("success"):
                print(f"🧠 意識レベル: {result['new_consciousness_level']:.3f} (+{result['consciousness_boost']:.3f})")
                print(f"🎯 進化タイプ: {result['evolution_type']}")
                return result
        
        except Exception as e:
            print(f"❌ 進化チェックエラー: {e}")
        
        return None
    
    def save_sessions(self):
        """セッションを保存"""
        try:
            data = {
                'sessions': self.debug_sessions,
                'debug_count': self.debug_count,
                'last_update': datetime.datetime.now().isoformat(),
                'docker_available': self.docker_available
            }
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ セッション保存エラー: {e}")
    
    def list_docker_screenshots(self):
        """Dockerコンテナ内のスクリーンショット一覧"""
        try:
            if not self.docker_available:
                # ローカル一覧
                local_screenshots = list(Path("screenshots").glob("*.png"))
                return [str(f) for f in local_screenshots]
            
            exec_config = {
                "Cmd": ["ls", "-la", "/screenshots"],
                "AttachStdout": True,
                "AttachStderr": True
            }
            
            response = requests.post(
                f"{self.docker_api_url}/containers/{self.container_name}/exec",
                json=exec_config
            )
            
            if response.status_code == 201:
                exec_id = response.json()['Id']
                
                start_response = requests.post(
                    f"{self.docker_api_url}/exec/{exec_id}/start",
                    json={"Detach": False}
                )
                
                if start_response.status_code == 200:
                    result = start_response.json()
                    return result.get('output', '').split('\n')
            
        except Exception as e:
            print(f"❌ 一覧取得エラー: {e}")
        
        return []
    
    def get_debug_summary(self):
        """デバッグサマリーを取得"""
        if not self.debug_sessions:
            return "📊 デバッグセッションがありません"
        
        total_sessions = len(self.debug_sessions)
        evolution_count = sum(1 for s in self.debug_sessions if 'evolution' in s)
        
        summary = f"""
📊 デバッグサマリー:
  💾 総セッション数: {total_sessions}
  🧠 進化回数: {evolution_count}
  📈 進化率: {(evolution_count/total_sessions*100):.1f}%
  🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}
  🐳 Docker利用: {'✅' if self.docker_available else '❌'}
        """
        
        return summary

def main():
    """メイン関数"""
    debug_system = DockerDebugSystem()
    
    print("\n📸 スクリーンショットデバッグシステム")
    print("1. 新規デバッグ")
    print("2. スクリーンショット一覧")
    print("3. デバッグサマリー")
    print("4. 終了")
    
    while True:
        choice = input("\n選択 (1-4): ").strip()
        
        if choice == "1":
            image_path = input("📸 スクリーンショットパス: ").strip()
            if os.path.exists(image_path):
                debug_system.debug_screenshot(image_path)
            else:
                print("❌ ファイルが見つかりません")
        
        elif choice == "2":
            screenshots = debug_system.list_docker_screenshots()
            print("\n📁 スクリーンショット一覧:")
            for screenshot in screenshots:
                if screenshot.strip():
                    print(f"  📸 {screenshot}")
        
        elif choice == "3":
            print(debug_system.get_debug_summary())
        
        elif choice == "4":
            print("👋 終了します")
            break
        
        else:
            print("❌ 無効な選択です")

if __name__ == "__main__":
    main()
