import requests
import os
import shutil
from pathlib import Path

def download_sample_vrm():
    """サンプルVRMファイルをダウンロード"""
    
    # ターゲットディレクトリ
    target_dir = Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print("🤖 サンプルVRMファイルをダウンロードします...")
    print(f"📁 保存先: {target_dir}")
    
    # サンプルVRMファイルのダウンロードURLリスト
    vrm_samples = [
        {
            "name": "Alicia_Solid",
            "url": "https://raw.githubusercontent.com/vrm-c/vrm-specification/master/samples/Alicia_Solid.vrm",
            "filename": "Alicia_Solid.vrm",
            "description": "VRM公式サンプルモデル"
        },
        {
            "name": "VRM_Sample_Basic",
            "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/VC/glTF-Binary/VC.glb",
            "filename": "VRM_Sample_Basic.glb",
            "description": "glTFサンプルモデル（VRM変換可能）"
        }
    ]
    
    downloaded_files = []
    
    for sample in vrm_samples:
        print(f"\n🔄 {sample['name']} ({sample['description']}) をダウンロード中...")
        
        try:
            # ファイルダウンロード
            response = requests.get(sample['url'], stream=True, timeout=60)
            response.raise_for_status()
            
            # 保存先パス
            file_path = target_dir / sample['filename']
            
            # ファイル保存
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ {sample['filename']} を {file_path} に保存しました")
            downloaded_files.append(file_path)
            
        except Exception as e:
            print(f"❌ {sample['name']} のダウンロードに失敗: {str(e)}")
    
    if downloaded_files:
        # staticディレクトリにもコピー
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        print(f"\n📁 VRMファイルを {static_dir} にもコピーします...")
        
        # avatar.vrmとしてコピー（最初のファイル）
        if downloaded_files:
            source_file = downloaded_files[0]
            dest_file = static_dir / "avatar.vrm"
            
            try:
                shutil.copy2(source_file, dest_file)
                print(f"✅ {source_file.name} を {dest_file} にコピーしました")
            except Exception as e:
                print(f"❌ コピーに失敗: {str(e)}")
        
        print(f"\n🎉 VRMファイルのダウンロードが完了しました！")
        print(f"\n📋 ダウンロードされたファイル:")
        for file_path in downloaded_files:
            print(f"  - {file_path.name}")
            
        print(f"\n📋 次のステップ:")
        print(f"1. Dockerコンテナを再起動")
        print(f"2. ブラウザで http://localhost:8501 にアクセス")
        print(f"3. VRMアバターが表示されるか確認")
        
    else:
        print("\n❌ VRMファイルのダウンロードに失敗しました。")
        print("💡 手動でVRMファイルをダウンロードしてください。")
        print(f"📁 配置先: {target_dir}")

def create_vrm_download_guide():
    """VRMダウンロードガイドを作成"""
    guide_content = """# VRMファイルダウンロードガイド

## 🤖 おすすめのVRMファイル

### 1. 無料VRMモデル

#### VRM Hub (公式)
- URL: https://hub.vrm.dev/
- 特徴: 多数の無料VRMモデル
- おすすめ: Alicia_Solid, Unity-chan

#### BOOTH
- URL: https://booth.pm/ja/
- 特徴: 日本のクリエイター作品
- 検索: "VRM 無料"

#### Sketchfab
- URL: https://sketchfab.com/
- 特徴: 3Dモデル多数
- 検索: "VRM free download"

### 2. 直接ダウンロードリンク

#### Alicia (VRM公式サンプル)
- URL: https://raw.githubusercontent.com/vrm-c/vrm-specification/master/samples/Alicia_Solid.vrm
- ファイル名: Alicia_Solid.vrm
- 特徴: 軽量、確実に動作

#### Unity-chan
- URL: https://github.com/dwango/unity-chan-vrm/releases
- ファイル名: unity-chan-vrm.vrm
- 特徴: 人気、高品質

### 3. ダウンロード手順

1. 上記URLからVRMファイルをダウンロード
2. `C:\\Users\\GALLE\\Desktop\\EzoMomonga_Free\\` に保存
3. ファイル名を `avatar.vrm` に変更（推奨）
4. Dockerコンテナを再起動

### 4. 確認方法

1. ブラウザで http://localhost:8501 にアクセス
2. VRMアバターが表示されるか確認
3. 人格切り替えで表情が変わるか確認

### 5. 注意事項

- VRMファイルは通常10MB〜100MB
- 著作権を確認の上で使用
- 商用利用の場合はライセンスを確認
"""
    
    guide_path = Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free\VRM_Download_Guide.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📝 VRMダウンロードガイドを作成: {guide_path}")

if __name__ == "__main__":
    print("🤖 VRMサンプルファイルダウンローダー")
    print("=" * 50)
    
    # サンプルVRMをダウンロード
    download_sample_vrm()
    
    # ダウンロードガイドを作成
    create_vrm_download_guide()
    
    print("\n" + "=" * 50)
    print("🎉 VRMファイルの準備が完了しました！")
    print("\n💡 追加のVRMファイルはガイドを参照してください。")
