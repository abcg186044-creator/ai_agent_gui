import requests
import os
import sys
from pathlib import Path

def download_vrm():
    """VRMアバターをダウンロードして指定ディレクトリに保存"""
    
    # VRMファイルURL（例：フリーのVRMモデル）
    vrm_urls = [
        {
            "name": "EzoMomonga_Free",
            "url": "https://github.com/EzoMomonga/EzoMomonga_Free/releases/download/v1.0.0/EzoMomonga_Free.vrm",
            "filename": "EzoMomonga_Free.vrm"
        },
        {
            "name": "Alicia_Solid",
            "url": "https://github.com/vrm-c/vrm-specification/blob/master/samples/Alicia_Solid.vrm?raw=true",
            "filename": "Alicia_Solid.vrm"
        }
    ]
    
    # ターゲットディレクトリ
    target_dir = Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"VRMファイルを {target_dir} にダウンロードします...")
    
    for vrm_info in vrm_urls:
        print(f"\n{vrm_info['name']} をダウンロード中...")
        
        try:
            # ファイルダウンロード
            response = requests.get(vrm_info['url'], stream=True, timeout=30)
            response.raise_for_status()
            
            # 保存先パス
            file_path = target_dir / vrm_info['filename']
            
            # ファイル保存
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ {vrm_info['filename']} を {file_path} に保存しました")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {vrm_info['name']} のダウンロードに失敗: {str(e)}")
        except Exception as e:
            print(f"❌ {vrm_info['name']} の処理中にエラー: {str(e)}")
    
    # staticディレクトリにもコピー
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    
    print(f"\nVRMファイルを {static_dir} にもコピーします...")
    
    for vrm_info in vrm_urls:
        source_file = target_dir / vrm_info['filename']
        dest_file = static_dir / vrm_info['filename']
        
        if source_file.exists():
            try:
                import shutil
                shutil.copy2(source_file, dest_file)
                print(f"✅ {vrm_info['filename']} を {dest_file} にコピーしました")
            except Exception as e:
                print(f"❌ {vrm_info['filename']} のコピーに失敗: {str(e)}")
        else:
            print(f"⚠️ {vrm_info['filename']} が見つかりません: {source_file}")
    
    print(f"\n🎉 VRMファイルのダウンロードと設定が完了しました！")
    print(f"📁 保存先: {target_dir}")
    print(f"📁 アプリ用: {static_dir}")

if __name__ == "__main__":
    download_vrm()
