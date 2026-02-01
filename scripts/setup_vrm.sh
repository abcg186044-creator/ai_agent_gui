#!/bin/bash

# VRMモデルセットアップスクリプト

echo "🎭 VRMモデルセットアップを開始します..."

# VRMディレクトリの確認
VRM_DIR="/app/assets/vrm"
mkdir -p "$VRM_DIR"

# デスクトップのVRMモデルをコピー
DESKTOP_VRM="/mnt/c/Users/GALLE/Desktop/EzoMomonga_Free"

if [ -d "$DESKTOP_VRM" ]; then
    echo "✅ デスクトップのVRMモデルが見つかりました"
    cp -r "$DESKTOP_VRM"/* "$VRM_DIR/"
    echo "✅ VRMモデルをコンテナにコピーしました"
else
    echo "⚠️ デスクトップのVRMモデルが見つかりません"
    echo "🔄 デフォルトVRMモデルをダウンロードします..."
    
    # デフォルトVRMモデルのダウンロード
    DEFAULT_VRM_URL="https://github.com/MochiMochi3D/VRM-Samples/raw/main/VRM/AliciaSolid.vrm"
    curl -L -o "$VRM_DIR/AliciaSolid.vrm" "$DEFAULT_VRM_URL"
    echo "✅ デフォルトVRMモデルをダウンロードしました"
fi

# VRMモデルの確認
echo "📋 利用可能なVRMモデル:"
ls -la "$VRM_DIR/"

# パーミッションの設定
chmod 644 "$VRM_DIR"/*.vrm 2>/dev/null

echo "✅ VRMモデルセットアップ完了"
