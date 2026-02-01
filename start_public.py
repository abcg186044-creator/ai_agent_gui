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
    
    # カレントディレクトリを確認
    current_dir = Path.cwd()
    main_app_path = current_dir / "main_app_new.py"
    
    if not main_app_path.exists():
        print(f"❌ メインアプリが見つかりません: {main_app_path}")
        print("カレントディレクトリ:", current_dir)
        print("ファイル一覧:")
        for file in current_dir.glob("*.py"):
            print(f"  - {file.name}")
        return False
    
    print(f"✅ メインアプリを確認: {main_app_path}")
    
    # 起動コマンド
    cmd = [
        sys.executable, "-m", "streamlit", "run", "main_app_new.py",
        "--server.address", "0.0.0.0",
        "--server.port", "8502",
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    
    print(f"🌐 ネットワークアクセスURL:")
    print(f"   Local:   http://localhost:8502")
    print(f"   Network: http://{local_ip}:8502")
    print()
    print("📱 同じネットワーク内の他のデバイスからアクセス可能:")
    print(f"   スマートフォン: http://{local_ip}:8502")
    print(f"   タブレット:     http://{local_ip}:8502")
    print()
    print("🔧 最新のモジュール版AI Agent VRM Systemを起動中...")
    print(f"📁 作業ディレクトリ: {current_dir}")
    print(f"🔧 コマンド: {' '.join(cmd)}")
    print()
    
    try:
        # 環境変数を設定
        env = os.environ.copy()
        env["STREAMLIT_SERVER_HEADLESS"] = "false"
        env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        
        # Streamlitを起動
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("✅ Streamlitプロセスを開始しました")
        print("🌐 ブラウザでアクセスしてください...")
        
        # 出力を監視
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # エラー出力を確認
        stderr_output = process.stderr.read()
        if stderr_output:
            print("❌ エラー出力:")
            print(stderr_output)
        
        return_code = process.poll()
        if return_code == 0:
            print("✅ 正常終了")
        else:
            print(f"❌ 終了コード: {return_code}")
            
        return return_code == 0
        
    except FileNotFoundError:
        print("❌ Streamlitが見つかりません")
        print("インストールコマンド: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        return False

if __name__ == "__main__":
    start_streamlit_public()
