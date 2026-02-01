"""
ネットワーク公開設定付き起動スクリプト
外部アクセスを許可してStreamlitアプリを起動
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

def get_local_ip():
    """ローカルIPアドレスを取得"""
    try:
        # ホスト名からIPアドレスを取得
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "127.0.0.1"

def check_permissions():
    """ファイルパーミッションを確認"""
    try:
        # データディレクトリのパーミッションを確認
        data_dir = Path("data")
        if data_dir.exists():
            # 書き込み権限を確認
            test_file = data_dir / "permission_test.tmp"
            try:
                test_file.write_text("test")
                test_file.unlink()
                return True
            except:
                return False
        else:
            # ディレクトリを作成して権限を設定
            data_dir.mkdir(exist_ok=True)
            return True
    except Exception as e:
        print(f"❌ パーミッション確認エラー: {e}")
        return False

def start_streamlit_public():
    """外部アクセス可能なStreamlitアプリを起動"""
    print("🚀 AI Agent VRM System - ネットワーク公開モード")
    print("=" * 50)
    
    # パーミッション確認
    if not check_permissions():
        print("❌ ファイルパーミッションエラー")
        print("管理者権限で実行するか、ファイルの書き込み権限を確認してください")
        return False
    
    # ローカルIPを取得
    local_ip = get_local_ip()
    
    # 起動コマンド
    cmd = [
        sys.executable, "-m", "streamlit", "run", "main_app_new.py",
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false"
    ]
    
    print(f"🌐 ネットワークアクセスURL:")
    print(f"   Local:   http://localhost:8501")
    print(f"   Network: http://{local_ip}:8501")
    print()
    print("📱 同じネットワーク内の他のデバイスからアクセス可能:")
    print(f"   スマートフォン: http://{local_ip}:8501")
    print(f"   タブレット:     http://{local_ip}:8501")
    print()
    print("🔧 起動中...")
    
    try:
        # Streamlitを起動
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 起動エラー: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 アプリケーションを停止しました")
        return True

if __name__ == "__main__":
    start_streamlit_public()
