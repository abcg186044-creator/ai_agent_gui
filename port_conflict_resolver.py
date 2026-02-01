#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポート競合解決システム
"""

import socket
import subprocess
import time
import asyncio
from typing import List, Dict, Optional, Any
import requests

class PortManager:
    """ポート管理システム"""
    
    def __init__(self, base_port: int = 11434, max_ports: int = 5):
        self.base_port = base_port
        self.max_ports = max_ports
        self.used_ports = set()
        self.ollama_processes = {}
    
    def check_port_available(self, port: int) -> bool:
        """ポートが利用可能かチェック"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0
        except:
            return False
    
    def find_available_port(self) -> Optional[int]:
        """利用可能なポートを探す"""
        for i in range(self.max_ports):
            port = self.base_port + i
            if self.check_port_available(port):
                return port
        return None
    
    def start_ollama_on_port(self, port: int) -> bool:
        """指定ポートでOllamaを起動"""
        if port in self.ollama_processes:
            return True
        
        try:
            # Ollamaを指定ポートで起動
            cmd = ["ollama", "serve", "--port", str(port)]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 起動を待機
            time.sleep(2)
            
            if self.check_port_available(port):
                process.terminate()
                return False
            
            self.ollama_processes[port] = process
            return True
            
        except Exception as e:
            print(f"❌ Ollama起動エラー (ポート: {port}): {e}")
            return False
    
    def stop_ollama_on_port(self, port: int):
        """指定ポートのOllamaを停止"""
        if port in self.ollama_processes:
            try:
                self.ollama_processes[port].terminate()
                del self.ollama_processes[port]
            except:
                pass
    
    def get_port_status(self) -> Dict[str, Any]:
        """ポートステータスを取得"""
        status = {}
        for i in range(self.max_ports):
            port = self.base_port + i
            status[f"port_{port}"] = {
                "port": port,
                "available": self.check_port_available(port),
                "process_running": port in self.ollama_processes
            }
        return status
    
    def cleanup(self):
        """クリーンアップ"""
        for port in list(self.ollama_processes.keys()):
            self.stop_ollama_on_port(port)

class PortConflictResolver:
    """ポート競合解決システム"""
    
    def __init__(self, base_port: int = 11434, max_ports: int = 5):
        self.port_manager = PortManager(base_port, max_ports)
        self.request_queue = asyncio.Queue()
        self.processing = False
    
    async def resolve_port_conflict(self, max_retries: int = 3) -> Optional[int]:
        """ポート競合を解決"""
        for attempt in range(max_retries):
            # 利用可能なポートを探す
            available_port = self.port_manager.find_available_port()
            
            if available_port:
                # ポートが利用可能な場合
                if available_port == self.port_manager.base_port:
                    # メインポートが利用可能
                    return available_port
                else:
                    # 別ポートでOllamaを起動
                    if self.port_manager.start_ollama_on_port(available_port):
                        return available_port
            
            # 少し待って再試行
            await asyncio.sleep(1)
        
        return None
    
    async def get_ollama_port(self) -> int:
        """Ollamaポートを取得"""
        port = await self.resolve_port_conflict()
        if port:
            return port
        else:
            raise Exception("利用可能なOllamaポートが見つかりません")
    
    async def test_ollama_connection(self, port: int) -> bool:
        """Ollama接続をテスト"""
        try:
            response = requests.get(f"http://localhost:{port}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        return {
            "port_status": self.port_manager.get_port_status(),
            "active_processes": len(self.port_manager.ollama_processes),
            "base_port": self.port_manager.base_port,
            "max_ports": self.port_manager.max_ports
        }

# テスト用
if __name__ == "__main__":
    resolver = PortConflictResolver(base_port=11434, max_ports=3)
    
    async def test_port_resolution():
        """ポート解決テスト"""
        print("🚀 ポート競合解決テスト開始")
        print("=" * 60)
        
        # 初期ステータス
        print("📊 初期ポートステータス:")
        status = resolver.get_system_status()
        for port_name, port_info in status["port_status"].items():
            available_text = "🟢 利用可能" if port_info["available"] else "🔴 使用中"
            print(f"   {port_name}: {available_text}")
        
        print("\n🔍 ポート解決テスト:")
        
        # 複数回ポート要求をテスト
        for i in range(5):
            print(f"\n📋 テスト {i+1}: Ollamaポートを要求")
            
            try:
                port = await resolver.get_ollama_port()
                print(f"✅ ポート {port} を取得")
                
                # 接続テスト
                connection_ok = await resolver.test_ollama_connection(port)
                if connection_ok:
                    print(f"   🌐 接続テスト成功")
                else:
                    print(f"   ⚠️ 接続テスト失敗（Ollama未起動）")
                
            except Exception as e:
                print(f"❌ エラー: {e}")
        
        print(f"\n📊 最終ポートステータス:")
        status = resolver.get_system_status()
        for port_name, port_info in status["port_status"].items():
            available_text = "🟢 利用可能" if port_info["available"] else "🔴 使用中"
            process_text = "🟢 起動中" if port_info["process_running"] else "🔴 停止中"
            print(f"   {port_name}: {available_text}, {process_text}")
        
        print(f"\n🔄 アクティブプロセス: {status['active_processes']}")
        
        # クリーンアップ
        print(f"\n🧹 クリーンアップ中...")
        resolver.port_manager.cleanup()
        
        print(f"🎉 ポート競合解決テスト完了！")
    
    # テスト実行
    asyncio.run(test_port_resolution())
