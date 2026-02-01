import requests
import os
import sys
from pathlib import Path
import urllib.parse

def search_vrm_sources():
    """VRMファイルのダウンロードソースを検索"""
    print("🔍 VRMファイルのダウンロードソースを検索中...")
    
    # 有名なVRMファイルのダウンロードURL
    vrm_sources = [
        {
            "name": "Alicia",
            "url": "https://dl.vrm.dev/vrm-c/Alicia_Solid.vrm",
            "description": "VRMサンプルモデル（Alicia）"
        },
        {
            "name": "Unity-chan",
            "url": "https://github.com/dwango/unity-chan-vrm/releases/download/v1.0.0/unity-chan-vrm.vrm",
            "description": "UnityちゃんVRMモデル"
        },
        {
            "name": "VRM_Sample",
            "url": "https://github.com/vrm-c/vrm-specification/raw/master/samples/Alicia_Solid.vrm",
            "description": "VRM仕様のサンプルモデル"
        }
    ]
    
    return vrm_sources

def download_vrm():
    """VRMアバターをダウンロードして指定ディレクトリに保存"""
    
    # ターゲットディレクトリ
    target_dir = Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 VRMファイルを {target_dir} にダウンロードします...")
    
    # VRMソースを取得
    vrm_sources = search_vrm_sources()
    
    downloaded_files = []
    
    for vrm_info in vrm_sources:
        print(f"\n🔄 {vrm_info['name']} ({vrm_info['description']}) をダウンロード中...")
        
        try:
            # ファイルダウンロード
            response = requests.get(vrm_info['url'], stream=True, timeout=60)
            response.raise_for_status()
            
            # ファイル名を取得
            filename = f"{vrm_info['name']}.vrm"
            file_path = target_dir / filename
            
            # ファイル保存
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ {filename} を {file_path} に保存しました")
            downloaded_files.append(file_path)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {vrm_info['name']} のダウンロードに失敗: {str(e)}")
        except Exception as e:
            print(f"❌ {vrm_info['name']} の処理中にエラー: {str(e)}")
    
    if downloaded_files:
        # staticディレクトリにもコピー
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        print(f"\n📁 VRMファイルを {static_dir} にもコピーします...")
        
        for file_path in downloaded_files:
            dest_file = static_dir / file_path.name
            
            try:
                import shutil
                shutil.copy2(file_path, dest_file)
                print(f"✅ {file_path.name} を {dest_file} にコピーしました")
            except Exception as e:
                print(f"❌ {file_path.name} のコピーに失敗: {str(e)}")
        
        print(f"\n🎉 VRMファイルのダウンロードと設定が完了しました！")
        print(f"📁 保存先: {target_dir}")
        print(f"📁 アプリ用: {static_dir}")
        print(f"\n📋 ダウンロードされたファイル:")
        for file_path in downloaded_files:
            print(f"  - {file_path.name}")
    else:
        print("\n❌ VRMファイルのダウンロードに失敗しました。")
        print("💡 手動でVRMファイルをダウンロードして、以下のディレクトリに配置してください:")
        print(f"   📁 {target_dir}")
        print(f"   📁 {static_dir}")

def create_placeholder_vrm():
    """プレースホルダーVRMファイルを作成"""
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    
    placeholder_vrm = static_dir / "avatar.vrm"
    
    # 簡単なプレースホルダーテキストを作成
    with open(placeholder_vrm, 'w', encoding='utf-8') as f:
        f.write("# VRM Placeholder File\n")
        f.write("# This is a placeholder file.\n")
        f.write("# Please download a real VRM file and replace this.\n")
        f.write("# Recommended VRM sources:\n")
        f.write("# - https://dl.vrm.dev/vrm-c/Alicia_Solid.vrm\n")
        f.write("# - https://github.com/dwango/unity-chan-vrm/releases\n")
    
    print(f"📝 プレースホルダーファイルを作成: {placeholder_vrm}")

if __name__ == "__main__":
    print("🤖 VRMアバターダウンローダー")
    print("=" * 50)
    
    download_vrm()
    
    # ダウンロード失敗時のフォールバック
    static_dir = Path(__file__).parent / "static"
    if not any(static_dir.glob("*.vrm")):
        print("\n⚠️ VRMファイルが見つかりません。プレースホルダーを作成します。")
        create_placeholder_vrm()
        print("\n💡 後で実際のVRMファイルをダウンロードして、avatar.vrmとして保存してください。")
