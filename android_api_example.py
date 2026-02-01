#!/usr/bin/env python3
"""
AndroidアプリからのAPI利用例
デジタルヒューマンAPIの使い方デモ
"""

import requests
import json
import time
from typing import Optional

class DigitalHumanAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "digital_human_2026_api_key"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def send_message(self, message: str, user_id: str = "android_user", voice_enabled: bool = False) -> dict:
        """チャットメッセージを送信"""
        try:
            url = f"{self.base_url}/chat"
            data = {
                "message": message,
                "user_id": user_id,
                "voice_enabled": voice_enabled
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"APIリクエストエラー: {str(e)}"}
    
    def get_status(self) -> dict:
        """AIのステータスを取得"""
        try:
            url = f"{self.base_url}/status"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"ステータス取得エラー: {str(e)}"}
    
    def get_screenshot(self) -> dict:
        """最新のスクリーンショットを取得"""
        try:
            url = f"{self.base_url}/screenshot"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"スクリーンショット取得エラー: {str(e)}"}
    
    def get_tasks(self) -> dict:
        """タスク履歴を取得"""
        try:
            url = f"{self.base_url}/tasks"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"タスク取得エラー: {str(e)}"}
    
    def health_check(self) -> dict:
        """ヘルスチェック"""
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"ヘルスチェックエラー: {str(e)}"}

def demonstrate_api_usage():
    """API使用例のデモ"""
    print("🤖 デジタルヒューマンAPI デモ")
    print("=" * 50)
    
    # APIクライアントの初期化
    client = DigitalHumanAPIClient()
    
    # 1. ヘルスチェック
    print("\n1. 🏥 ヘルスチェック")
    health = client.health_check()
    if "error" not in health:
        print(f"✅ APIステータス: {health['status']}")
        print(f"📅 バージョン: {health['api_version']}")
    else:
        print(f"❌ ヘルスチェック失敗: {health['error']}")
        return
    
    # 2. ステータス確認
    print("\n2. 📊 AIステータス確認")
    status = client.get_status()
    if "error" not in status:
        print(f"🤖 AI稼働中: {status['ai_active']}")
        print(f"📋 現在タスク: {status['current_tasks']}")
        print(f"⏰ タイムスタンプ: {status['timestamp']}")
    else:
        print(f"❌ ステータス取得失敗: {status['error']}")
    
    # 3. チャットメッセージ送信
    print("\n3. 💬 チャットメッセージ送信")
    messages = [
        "こんにちは！Androidアプリからテスト中です",
        "今のPCの画面状況を教えて",
        "新しいWebアプリを作ってくれませんか？",
        "ありがとう、すごいよ！"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n📱 メッセージ {i}: {message}")
        
        # メッセージを送信
        response = client.send_message(
            message=message,
            user_id=f"android_demo_{i}",
            voice_enabled=True  # 音声合成を有効化
        )
        
        if "error" not in response:
            print(f"✅ タスクID: {response['task_id']}")
            print(f"📝 ステータス: {response['status']}")
            
            # 数秒待ってからタスク状況を確認
            time.sleep(3)
            
            # タスク履歴を確認
            tasks = client.get_tasks()
            if "error" not in tasks:
                completed_tasks = [t for t in tasks['task_history'] if t.get('status') == 'completed']
                if completed_tasks:
                    latest = completed_tasks[-1]
                    print(f"🤖 AI応答: {latest.get('response', '応答待ち中...')}")
        else:
            print(f"❌ メッセージ送信失敗: {response['error']}")
        
        time.sleep(2)  # 次のメッセージまで少し待つ
    
    # 4. スクリーンショット取得
    print("\n4. 📸 スクリーンショット取得")
    screenshot = client.get_screenshot()
    if "error" not in screenshot:
        if "screenshot" in screenshot:
            print("✅ スクリーンショット取得成功")
            print(f"📅 タイムスタンプ: {screenshot['timestamp']}")
            print(f"🔍 分析結果: {screenshot.get('analysis', '分析なし')}")
            print(f"📱 画像サイズ: {len(screenshot['screenshot'])} バイト")
        else:
            print("📷 利用可能なスクリーンショットがありません")
    else:
        print(f"❌ スクリーンショット取得失敗: {screenshot['error']}")
    
    # 5. 最終タスク確認
    print("\n5. 📋 最終タスク確認")
    final_tasks = client.get_tasks()
    if "error" not in final_tasks:
        print(f"📊 総完了タスク: {final_tasks['total_completed']}")
        print(f"📝 最新タスク履歴:")
        for task in final_tasks['task_history'][-3:]:
            print(f"  - {task['id']}: {task['status']} ({task.get('completed_at', 'N/A')})")
    else:
        print(f"❌ タスク取得失敗: {final_tasks['error']}")
    
    print("\n" + "=" * 50)
    print("🎉 APIデモ完了！")
    print("\n📖 Androidアプリ実装例:")
    print("```python")
    print("import requests")
    print("")
    print("# APIクライアント初期化")
    print("client = DigitalHumanAPIClient()")
    print("")
    print("# メッセージ送信")
    print("response = client.send_message('こんにちは', voice_enabled=True)")
    print("print(response)")
    print("")
    print("# ステータス確認")
    print("status = client.get_status()")
    print("print(status)")
    print("```")

# Androidアプリ用の簡単なHTTPリクエスト例
def android_http_examples():
    """Androidアプリ用HTTPリクエスト例"""
    examples = {
        "chat": {
            "url": "http://localhost:8000/chat",
            "method": "POST",
            "headers": {
                "X-API-Key": "digital_human_2026_api_key",
                "Content-Type": "application/json"
            },
            "body": {
                "message": "こんにちは",
                "user_id": "android_user",
                "voice_enabled": True
            }
        },
        "status": {
            "url": "http://localhost:8000/status",
            "method": "GET",
            "headers": {
                "X-API-Key": "digital_human_2026_api_key"
            }
        },
        "screenshot": {
            "url": "http://localhost:8000/screenshot",
            "method": "GET",
            "headers": {
                "X-API-Key": "digital_human_2026_api_key"
            }
        }
    }
    
    print("📱 Androidアプリ用HTTPリクエスト例:")
    print(json.dumps(examples, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # デモを実行
    demonstrate_api_usage()
    
    print("\n" + "=" * 50)
    android_http_examples()
