#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker環境セットアップスクリプト
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_docker_installation():
    """Dockerのインストールを確認"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Dockerがインストールされています: {result.stdout.strip()}")
            return True
        else:
            print("❌ Dockerがインストールされていません")
            return False
    except FileNotFoundError:
        print("❌ Dockerが見つかりません")
        return False

def check_docker_daemon():
    """Dockerデーモンの動作を確認"""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dockerデーモンが動作しています")
            return True
        else:
            print("❌ Dockerデーモンが動作していません")
            print("💡 Docker Desktopを起動してください")
            return False
    except Exception as e:
        print(f"❌ Dockerデーモンチェックエラー: {e}")
        return False

def setup_docker_api():
    """Docker APIを有効化"""
    try:
        # Windowsの場合、Docker Desktopの設定を確認
        if os.name == 'nt':
            print("🪟 Windows環境を検出しました")
            print("💡 Docker Desktopで「Expose daemon on tcp://localhost:2375 without TLS」を有効にしてください")
            print("   設定場所: Docker Desktop → Settings → Docker Engine")
            return True
        
        # Linux/Macの場合
        print("🐧 Linux/Mac環境を検出しました")
        
        # Docker APIソケットを確認
        api_socket = "/var/run/docker.sock"
        if os.path.exists(api_socket):
            print(f"✅ Docker APIソケットが存在します: {api_socket}")
            return True
        else:
            print(f"❌ Docker APIソケットが存在しません: {api_socket}")
            return False
            
    except Exception as e:
        print(f"❌ Docker APIセットアップエラー: {e}")
        return False

def test_docker_api():
    """Docker APIの接続テスト"""
    try:
        # ローカルDocker APIテスト
        response = requests.get("http://localhost:2375/version", timeout=5)
        if response.status_code == 200:
            print("✅ Docker APIに接続成功")
            print(f"📋 Dockerバージョン: {response.json().get('Version', 'Unknown')}")
            return True
        else:
            print(f"❌ Docker API接続失敗: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Docker APIに接続できません")
        print("💡 以下を確認してください:")
        print("   1. Docker Desktopが起動しているか")
        print("   2. Docker APIが有効になっているか")
        print("   3. ファイアウォールの設定")
        return False
    except Exception as e:
        print(f"❌ Docker APIテストエラー: {e}")
        return False

def create_debug_container():
    """デバッグ用コンテナを作成"""
    try:
        # コンテナが存在するか確認
        result = subprocess.run([
            'docker', 'ps', '-a', '--filter', 'name=debug-screenshots', '--format', '{{.Names}}'
        ], capture_output=True, text=True)
        
        if 'debug-screenshots' in result.stdout:
            print("✅ debug-screenshotsコンテナは既に存在します")
            
            # コンテナが停止している場合は起動
            result = subprocess.run([
                'docker', 'ps', '--filter', 'name=debug-screenshots', '--format', '{{.Status}}'
            ], capture_output=True, text=True)
            
            if 'Up' not in result.stdout:
                print("🚀 debug-screenshotsコンテナを起動します...")
                subprocess.run(['docker', 'start', 'debug-screenshots'], check=True)
                print("✅ コンテナ起動成功")
        else:
            print("📦 debug-screenshotsコンテナを作成します...")
            
            # screenshotsディレクトリを作成
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            # コンテナを作成
            subprocess.run([
                'docker', 'run', '-d',
                '--name', 'debug-screenshots',
                '-v', f'{os.getcwd()}/screenshots:/screenshots',
                'alpine:latest',
                'tail', '-f', '/dev/null'
            ], check=True)
            
            print("✅ debug-screenshotsコンテナ作成成功")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ コンテナ作成エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ コンテナセットアップエラー: {e}")
        return False

def setup_screenshots_directory():
    """screenshotsディレクトリをセットアップ"""
    try:
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        # テストファイルを作成
        test_file = screenshots_dir / "test.txt"
        with open(test_file, "w") as f:
            f.write("Docker screenshots directory test\n")
        
        print(f"✅ screenshotsディレクトリをセットアップしました: {screenshots_dir}")
        return True
        
    except Exception as e:
        print(f"❌ ディレクトリセットアップエラー: {e}")
        return False

def main():
    """メインセットアップ処理"""
    print("🐳 Docker環境セットアップを開始します")
    print("=" * 50)
    
    # 1. Dockerインストール確認
    if not check_docker_installation():
        print("\n❌ Dockerがインストールされていません")
        print("💡 以下からDocker Desktopをインストールしてください:")
        print("   https://www.docker.com/products/docker-desktop")
        return False
    
    # 2. Dockerデーモン確認
    if not check_docker_daemon():
        print("\n❌ Dockerデーモンが動作していません")
        print("💡 Docker Desktopを起動してください")
        return False
    
    # 3. Docker APIセットアップ
    if not setup_docker_api():
        print("\n❌ Docker APIのセットアップに失敗しました")
        return False
    
    # 4. Docker APIテスト
    if not test_docker_api():
        print("\n❌ Docker APIの接続テストに失敗しました")
        print("💡 手動でDocker APIを有効にしてください")
        return False
    
    # 5. デバッグコンテナ作成
    if not create_debug_container():
        print("\n❌ デバッグコンテナの作成に失敗しました")
        return False
    
    # 6. screenshotsディレクトリセットアップ
    if not setup_screenshots_directory():
        print("\n❌ screenshotsディレクトリのセットアップに失敗しました")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Docker環境セットアップ完了！")
    print("=" * 50)
    print("✅ Dockerインストール: 完了")
    print("✅ Dockerデーモン: 動作中")
    print("✅ Docker API: 接続可能")
    print("✅ debug-screenshotsコンテナ: 作成済み")
    print("✅ screenshotsディレクトリ: 準備完了")
    print("\n🚀 スクリーンショットデバッグシステムを利用できます！")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
