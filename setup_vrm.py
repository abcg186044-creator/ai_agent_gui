import os
import shutil
from pathlib import Path

def setup_vrm_directories():
    """VRMファイル用のディレクトリ構造を作成"""
    
    # ターゲットディレクトリ
    target_dir = Path(r"C:\Users\GALLE\Desktop\EzoMomonga_Free")
    static_dir = Path(__file__).parent / "static"
    
    # ディレクトリ作成
    target_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(exist_ok=True)
    
    print("📁 VRMディレクトリを作成しました:")
    print(f"   📂 デスクトップ: {target_dir}")
    print(f"   📂 アプリ用: {static_dir}")
    
    return target_dir, static_dir

def create_vrm_info():
    """VRMファイル情報を作成"""
    vrm_info = """# VRMファイルセットアップ情報

## 🤖 VRMアバターの設定

### 📁 ディレクトリ構造
```
C:\\Users\\GALLE\\Desktop\\EzoMomonga_Free\\
├── [VRMファイル名].vrm
└── README.txt

C:\\Users\\GALLE\\CascadeProjects\\ai_agent_gui\\static\\
├── avatar.vrm
└── [その他の静的ファイル]
```

### 🔧 VRMファイルの入手方法

#### 1. VRMポータルサイト
- **VRM Hub**: https://hub.vrm.dev/
- **BOOTH**: https://booth.pm/ja/
- **Sketchfab**: https://sketchfab.com/

#### 2. 無料VRMモデル
- **Alicia**: VRMサンプルモデル
- **Unityちゃん**: 人気のVRMモデル
- **各種クリエイター作品**: 多数の無料モデル

#### 3. 検索キーワード
- "VRM free"
- "3D avatar free"
- "VRM model"
- "アバター 無料"

### 📋 セットアップ手順

1. **VRMファイルをダウンロード**
   - 上記サイトからVRMファイルをダウンロード
   - .vrm形式のファイルを選択

2. **デスクトップに保存**
   - `C:\\Users\\GALLE\\Desktop\\EzoMomonga_Free\\` に保存
   - ファイル名は `avatar.vrm` にリネーム推奨

3. **アプリ用にコピー**
   - `C:\\Users\\GALLE\\CascadeProjects\\ai_agent_gui\\static\\` にもコピー
   - アプリ起動時に自動的に読み込まれる

4. **確認**
   - Dockerコンテナを再起動
   - ブラウザでVRMアバターが表示されるか確認

### ⚠️ 注意事項

- VRMファイルは通常10MB〜100MB程度
- 著作権を確認の上で使用
- 商用利用の場合はライセンスを確認
- モデルによっては表示にGPUが必要

### 🎯 推奨VRMモデル

#### 初心者向け
- **Alicia_Solid.vrm**: 公式サンプル、軽量
- **Unity-chan.vrm**: 人気、高品質

#### 中級者向け
- **各種クリエイター作品**: 多様な表現
- **カスタマイズ可能モデル**: 表情豊富

#### 上級者向け
- **高ポリゴンモデル**: 写実的表現
- **物理演算対応モデル**: 動き自然
"""
    
    return vrm_info

def main():
    print("🤖 VRMアバターセットアップツール")
    print("=" * 50)
    
    # ディレクトリ作成
    target_dir, static_dir = setup_vrm_directories()
    
    # VRM情報ファイルを作成
    vrm_info = create_vrm_info()
    
    # 情報ファイルを保存
    info_file = target_dir / "README.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(vrm_info)
    
    print(f"\n📝 VRMセットアップ情報を保存: {info_file}")
    
    # プレースホルダーVRMファイルを作成
    placeholder_vrm = static_dir / "avatar.vrm"
    if not placeholder_vrm.exists():
        with open(placeholder_vrm, 'w', encoding='utf-8') as f:
            f.write("# VRM Placeholder File\n")
            f.write("# Please replace this with a real VRM file\n")
        print(f"📝 プレースホルダーVRMファイルを作成: {placeholder_vrm}")
    
    print(f"\n🎉 VRMセットアップ準備が完了しました！")
    print(f"\n📋 次のステップ:")
    print(f"1. VRMファイルをダウンロード（上記README.txt参照）")
    print(f"2. {target_dir} にVRMファイルを保存")
    print(f"3. {static_dir} にもコピー（avatar.vrmとして）")
    print(f"4. Dockerコンテナを再起動して確認")
    
    print(f"\n🌐 参考サイト:")
    print(f"- VRM Hub: https://hub.vrm.dev/")
    print(f"- BOOTH: https://booth.pm/ja/")
    print(f"- Sketchfab: https://sketchfab.com/")

if __name__ == "__main__":
    main()
