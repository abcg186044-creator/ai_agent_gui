from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

app = FastAPI(title="AI Agent System API")

# 静的ファイル配信
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "AI Agent System API"}

@app.get("/avatar.vrm")
async def serve_vrm():
    """VRMファイル配信"""
    vrm_path = Path("static/avatar.vrm")
    if vrm_path.exists():
        return FileResponse(vrm_path, media_type="application/octet-stream")
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "VRM file not found"}
        )

@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": "2026-01-17T12:00:00Z",
        "services": {
            "fastapi": "running",
            "static_files": "available"
        }
    }

@app.post("/api/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """音声認識API"""
    try:
        # 音声ファイル処理
        content = await audio.read()
        
        # ここに音声認識処理を追加
        # 現在はダミー応答
        return {
            "text": "音声認識結果（ダミー）",
            "confidence": 0.95
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """AIチャットAPI"""
    try:
        user_message = request.get("message", "")
        personality = request.get("personality", "friend")
        
        # ここにOllama連携処理を追加
        # 現在はダミー応答
        responses = {
            "friend": "こんにちは！親友エンジニアです。何かお手伝いできることはありますか？",
            "copy": "そうですね、私も同じように感じます。もっと詳しく教えてください。",
            "expert": "専門家として分析します。まずは問題の詳細を把握する必要があります。"
        }
        
        return {
            "response": responses.get(personality, responses["friend"]),
            "personality": personality,
            "timestamp": "2026-01-17T12:00:00Z"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
