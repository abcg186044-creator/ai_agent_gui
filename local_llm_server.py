#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自作ローカルLLM推論サーバー
"""

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False

class LocalLLMServer:
    def __init__(self, port: int = 11435):
        self.port = port
        self.app = FastAPI(title="Local LLM Server")
        self.setup_app()
    
    def setup_app(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"]
        )
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/")
        async def root():
            return {"message": "Local LLM Server is running"}
        
        @self.app.get("/api/tags")
        async def get_tags():
            return {
                "models": [
                    {
                        "name": "local-llm",
                        "model": "local-llm",
                        "modified_at": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                ]
            }
        
        @self.app.post("/api/generate")
        async def generate(request: GenerateRequest):
            return {
                "model": request.model,
                "response": f"Local LLM response for: {request.prompt}",
                "done": True,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
    
    def run(self):
        uvicorn.run(self.app, host="localhost", port=self.port)

if __name__ == "__main__":
    server = LocalLLMServer(port=11435)
    server.run()
