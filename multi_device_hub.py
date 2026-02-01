#!/usr/bin/env python3
"""
マルチデバイス・ハブ
FastAPIによる外部APIインターフェース
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import asyncio
import threading
import time
from datetime import datetime
import uvicorn
from pathlib import Path

# APIリクエストモデル
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    voice_enabled: Optional[bool] = True

class EmotionRequest(BaseModel):
    emotion: str
    intensity: Optional[float] = 1.0

class AvatarRequest(BaseModel):
    emotion: Optional[str] = None
    gesture: Optional[str] = None
    gaze_direction: Optional[List[float]] = None

class EvolutionRequest(BaseModel):
    target_files: Optional[List[str]] = None
    auto_apply: Optional[bool] = False

class CommandRequest(BaseModel):
    command: str
    parameters: Optional[Dict] = {}

# マルチデバイス・ハブ
class MultiDeviceHub:
    def __init__(self):
        self.name = "multi_device_hub"
        self.description = "FastAPIによるマルチデバイス制御システム"
        
        # FastAPIアプリ
        self.app = FastAPI(
            title="デジタルヒューマン API",
            description="AIエージェントを外部から制御するAPI",
            version="1.0.0"
        )
        
        # CORS設定
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # AIエージェントへの参照（後で設定）
        self.agent = None
        self.emotional_state = None
        self.vrm_avatar = None
        self.text_to_speech = None
        
        # セッション管理
        self.active_sessions = {}
        self.message_history = []
        
        # WebSocket接続管理
        self.websocket_connections = []
        
        # APIルートを設定
        self.setup_routes()
    
    def setup_ai_references(self, agent, emotional_state, vrm_avatar, text_to_speech):
        """AIコンポーネントへの参照を設定"""
        self.agent = agent
        self.emotional_state = emotional_state
        self.vrm_avatar = vrm_avatar
        self.text_to_speech = text_to_speech
    
    def setup_routes(self):
        """APIルートを設定"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "デジタルヒューマン API",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/status")
        async def get_status():
            """システム全体のステータスを取得"""
            status = {
                "ai_agent": "connected" if self.agent else "disconnected",
                "emotional_state": "connected" if self.emotional_state else "disconnected",
                "vrm_avatar": "connected" if self.vrm_avatar else "disconnected",
                "text_to_speech": "connected" if self.text_to_speech else "disconnected",
                "active_sessions": len(self.active_sessions),
                "uptime": time.time()
            }
            
            # 感情状態を取得
            if self.emotional_state:
                status["emotions"] = self.emotional_state.get_emotional_state()
            
            # アバター状態を取得
            if self.vrm_avatar:
                status["avatar"] = self.vrm_avatar.get_current_state()
            
            return status
        
        @self.app.post("/chat")
        async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
            """チャットメッセージを送信"""
            try:
                if not self.agent:
                    raise HTTPException(status_code=503, detail="AIエージェントが利用できません")
                
                # セッション管理
                session_id = f"{request.user_id}_{int(time.time())}"
                self.active_sessions[session_id] = {
                    "user_id": request.user_id,
                    "start_time": datetime.now().isoformat(),
                    "message_count": 0
                }
                
                # メッセージ履歴に追加
                self.message_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user_id": request.user_id,
                    "message": request.message,
                    "session_id": session_id
                })
                
                # AI応答を生成（バックグラウンドで）
                def generate_response():
                    try:
                        response = self.agent.invoke({"input": request.message})
                        ai_response = response.get('output', '応答生成エラー')
                        
                        # 感情状態を更新
                        if self.emotional_state:
                            self.emotional_state.update_emotion_from_interaction(
                                request.message, ai_response
                            )
                        
                        # 音声合成
                        if request.voice_enabled and self.text_to_speech:
                            self.text_to_speech.speak_ai_response(ai_response)
                        
                        # アバターを更新
                        if self.vrm_avatar:
                            self.vrm_avatar.sync_with_ai_state({
                                "is_speaking": True,
                                "emotion": self.emotional_state.get_dominant_emotion() if self.emotional_state else "neutral"
                            })
                        
                        # レスポンスを保存
                        self.message_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "user_id": "ai",
                            "message": ai_response,
                            "session_id": session_id
                        })
                        
                    except Exception as e:
                        print(f"AI応答生成エラー: {str(e)}")
                
                background_tasks.add_task(generate_response)
                
                return {
                    "session_id": session_id,
                    "message": "メッセージを受信しました",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/emotion")
        async def set_emotion(request: EmotionRequest):
            """感情を設定"""
            try:
                if not self.emotional_state:
                    raise HTTPException(status_code=503, detail="感情システムが利用できません")
                
                # 感情を更新
                if hasattr(self.emotional_state, request.emotion):
                    setattr(self.emotional_state, request.emotion, 
                           max(0, min(100, request.intensity * 100)))
                    self.emotional_state.save_state()
                else:
                    raise HTTPException(status_code=400, detail=f"不明な感情: {request.emotion}")
                
                # アバターを更新
                if self.vrm_avatar:
                    self.vrm_avatar.update_emotion(request.emotion, request.intensity)
                
                return {
                    "message": f"感情を{request.emotion}に設定しました",
                    "intensity": request.intensity,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/avatar")
        async def control_avatar(request: AvatarRequest):
            """アバターを制御"""
            try:
                if not self.vrm_avatar:
                    raise HTTPException(status_code=503, detail="アバターが利用できません")
                
                if request.emotion:
                    self.vrm_avatar.update_emotion(request.emotion)
                
                if request.gesture:
                    self.vrm_avatar.play_gesture(request.gesture)
                
                if request.gaze_direction:
                    self.vrm_avatar.update_gaze(request.gaze_direction)
                
                return {
                    "message": "アバターを更新しました",
                    "state": self.vrm_avatar.get_current_state(),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/evolution")
        async def trigger_evolution(request: EvolutionRequest):
            """自己進化をトリガー"""
            try:
                if not hasattr(self.agent, 'self_evolution'):
                    raise HTTPException(status_code=503, detail="自己進化システムが利用できません")
                
                # 進化を実行
                evolution_result = self.agent.self_evolution.evolve_myself(request.target_files)
                
                return {
                    "message": "自己進化を実行しました",
                    "result": evolution_result,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/command")
        async def execute_command(request: CommandRequest):
            """コマンドを実行"""
            try:
                if not self.agent:
                    raise HTTPException(status_code=503, detail="AIエージェントが利用できません")
                
                # コマンドを解析して実行
                if request.command.startswith("text_to_speech"):
                    result = self.text_to_speech.run(request.command.replace("text_to_speech ", ""))
                elif request.command.startswith("emotional_state"):
                    result = self.emotional_state.run(request.command.replace("emotional_state ", ""))
                elif request.command.startswith("vrm_avatar"):
                    result = self.vrm_avatar.run(request.command.replace("vrm_avatar ", ""))
                elif request.command.startswith("self_evolution"):
                    result = self.agent.self_evolution.run(request.command.replace("self_evolution ", ""))
                else:
                    result = "不明なコマンドです"
                
                return {
                    "command": request.command,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/history")
        async def get_history(limit: int = 50):
            """メッセージ履歴を取得"""
            return {
                "history": self.message_history[-limit:],
                "total": len(self.message_history),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/sessions")
        async def get_sessions():
            """アクティブセッションを取得"""
            return {
                "sessions": self.active_sessions,
                "count": len(self.active_sessions),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.delete("/sessions/{session_id}")
        async def close_session(session_id: str):
            """セッションを終了"""
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                return {"message": "セッションを終了しました"}
            else:
                raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        @self.app.get("/stream")
        async def stream_events():
            """イベントストリーム"""
            async def event_generator():
                while True:
                    yield f"data: {json.dumps({'timestamp': datetime.now().isoformat(), 'type': 'heartbeat'})}\n\n"
                    await asyncio.sleep(1)
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """サーバーを起動"""
        uvicorn.run(self.app, host=host, port=port, log_level="info")
    
    def run(self, command: str) -> str:
        """コマンドを実行"""
        if command == "start":
            # 別スレッドでサーバーを起動
            server_thread = threading.Thread(
                target=self.run_server,
                kwargs={"host": "0.0.0.0", "port": 8000},
                daemon=True
            )
            server_thread.start()
            return "マルチデバイス・ハブを起動しました: http://localhost:8000"
        
        elif command == "status":
            connections = len(self.active_sessions)
            return f"ハブ稼働中: {connections}件のアクティブセッション"
        
        elif command == "docs":
            return "APIドキュメント: http://localhost:8000/docs"
        
        else:
            return "コマンド形式: start, status, docs"

# グローバルハブインスタンス
hub = MultiDeviceHub()

def create_app_with_ai(agent, emotional_state, vrm_avatar, text_to_speech):
    """AIコンポーネントと連携したFastAPIアプリを作成"""
    hub.setup_ai_references(agent, emotional_state, vrm_avatar, text_to_speech)
    return hub.app

if __name__ == "__main__":
    # スタンドアロン実行
    hub.run("start")
