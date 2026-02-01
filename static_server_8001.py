#!/usr/bin/env python3
"""
FastAPI静的ファイルサーバー（ポート8001）
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="VRM Static Server", description="VRMアバター表示用静的ファイルサーバー")

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信の設定
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"✅ 静的ファイル配信を設定: {static_dir}")
else:
    print(f"❌ 静的ファイルディレクトリが見つかりません: {static_dir}")

@app.get("/")
async def root():
    return {"message": "VRM Static Server", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vrm-static-server"}

if __name__ == "__main__":
    print("🚀 FastAPI静的ファイルサーバー起動中...")
    print("📁 静的ファイル配信: http://localhost:8001/static/")
    print("🔧 VRMファイル: http://localhost:8001/static/avatar.vrm")
    print("📜 JavaScript: http://localhost:8001/static/js/vrm_app.js")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
