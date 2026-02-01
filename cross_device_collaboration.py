#!/usr/bin/env python3
"""
クロスデバイス連携システム
外部端末とのファイル移動・リモート操作・エージェント間通信
"""

import os
import subprocess
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import shutil
import base64
import hashlib
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import aiofiles
import qrcode
from io import BytesIO
import streamlit as st
from dataclasses import dataclass, field
from enum import Enum

class DeviceType(Enum):
    """デバイスタイプ"""
    ANDROID = "android"
    IPHONE = "iphone"
    PC = "pc"
    UNKNOWN = "unknown"

class CommandType(Enum):
    """コマンドタイプ"""
    FILE_TRANSFER = "file_transfer"
    REMOTE_OPERATION = "remote_operation"
    AGENT_MESSAGE = "agent_message"
    STATUS_UPDATE = "status_update"

@dataclass
class DeviceInfo:
    """デバイス情報"""
    device_id: str
    device_type: DeviceType
    ip_address: str
    last_seen: datetime
    capabilities: List[str] = field(default_factory=list)
    status: str = "online"

@dataclass
class FileTransfer:
    """ファイル転送情報"""
    file_id: str
    filename: str
    file_path: str
    file_size: int
    checksum: str
    created_at: datetime
    expires_at: datetime
    download_count: int = 0
    max_downloads: int = 10

@dataclass
class AgentCommand:
    """エージェントコマンド"""
    command_id: str
    command_type: CommandType
    source_device: str
    target_device: str
    payload: Dict
    created_at: datetime
    status: str = "pending"
    response: Optional[Dict] = None

class CrossDeviceCollaboration:
    """クロスデバイス連携システム"""
    
    def __init__(self):
        self.name = "cross_device_collaboration"
        self.description = "外部端末とのファイル移動・リモート操作・エージェント間通信"
        
        # デバイス管理
        self.connected_devices = {}
        self.device_info_file = "connected_devices.json"
        
        # ファイル転送管理
        self.file_transfers = {}
        self.transfer_dir = Path("file_transfers")
        self.transfer_dir.mkdir(exist_ok=True)
        
        # エージェント通信
        self.agent_commands = {}
        self.command_history = []
        
        # ADB設定
        self.adb_available = self._check_adb_availability()
        self.connected_android_devices = []
        
        # 初期化
        self._load_device_info()
        self._scan_android_devices()
    
    def _check_adb_availability(self) -> bool:
        """ADBの利用可能性をチェック"""
        try:
            result = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _load_device_info(self):
        """デバイス情報を読み込み"""
        try:
            if Path(self.device_info_file).exists():
                with open(self.device_info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for device_id, info in data.items():
                        device = DeviceInfo(
                            device_id=device_id,
                            device_type=DeviceType(info.get("device_type", "unknown")),
                            ip_address=info.get("ip_address", ""),
                            last_seen=datetime.fromisoformat(info.get("last_seen", datetime.now().isoformat())),
                            capabilities=info.get("capabilities", []),
                            status=info.get("status", "offline")
                        )
                        self.connected_devices[device_id] = device
        except Exception as e:
            print(f"デバイス情報読み込みエラー: {str(e)}")
    
    def _save_device_info(self):
        """デバイス情報を保存"""
        try:
            data = {}
            for device_id, device in self.connected_devices.items():
                data[device_id] = {
                    "device_type": device.device_type.value,
                    "ip_address": device.ip_address,
                    "last_seen": device.last_seen.isoformat(),
                    "capabilities": device.capabilities,
                    "status": device.status
                }
            
            with open(self.device_info_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"デバイス情報保存エラー: {str(e)}")
    
    def _scan_android_devices(self):
        """Androidデバイスをスキャン"""
        if not self.adb_available:
            return
        
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # ヘッダーを除外
                self.connected_android_devices = []
                
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            device_id = parts[0].strip()
                            status = parts[1].strip()
                            
                            if status == "device":
                                self.connected_android_devices.append(device_id)
                                
                                # デバイス情報を取得
                                device_info = self._get_android_device_info(device_id)
                                if device_info:
                                    self.connected_devices[device_id] = device_info
        except Exception as e:
            print(f"Androidデバイススキャンエラー: {str(e)}")
    
    def _get_android_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Androidデバイス情報を取得"""
        try:
            # デバイスモデルを取得
            result = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.product.model"], 
                                  capture_output=True, text=True, timeout=5)
            model = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            # IPアドレスを取得（WiFi接続の場合）
            ip_result = subprocess.run(["adb", "-s", device_id, "shell", "ip", "addr", "show", "wlan0"], 
                                      capture_output=True, text=True, timeout=5)
            ip_address = "Unknown"
            if ip_result.returncode == 0:
                import re
                ip_match = re.search(r"inet ([0-9\.]+)", ip_result.stdout)
                if ip_match:
                    ip_address = ip_match.group(1)
            
            return DeviceInfo(
                device_id=device_id,
                device_type=DeviceType.ANDROID,
                ip_address=ip_address,
                last_seen=datetime.now(),
                capabilities=["file_transfer", "remote_operation", "app_install"],
                status="online"
            )
        except Exception as e:
            print(f"Androidデバイス情報取得エラー: {str(e)}")
            return None
    
    def register_device(self, device_id: str, device_type: DeviceType, ip_address: str, 
                       capabilities: List[str] = None) -> bool:
        """デバイスを登録"""
        try:
            device = DeviceInfo(
                device_id=device_id,
                device_type=device_type,
                ip_address=ip_address,
                last_seen=datetime.now(),
                capabilities=capabilities or [],
                status="online"
            )
            
            self.connected_devices[device_id] = device
            self._save_device_info()
            return True
        except Exception as e:
            print(f"デバイス登録エラー: {str(e)}")
            return False
    
    def create_file_transfer(self, file_path: str, max_downloads: int = 10, 
                           expires_hours: int = 24) -> Optional[FileTransfer]:
        """ファイル転送を作成"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            # ファイル情報を取得
            file_size = path.stat().st_size
            
            # チェックサムを計算
            with open(path, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()
            
            # 転送用ファイルをコピー
            transfer_id = hashlib.md5(f"{file_path}{datetime.now()}".encode()).hexdigest()[:8]
            transfer_path = self.transfer_dir / f"{transfer_id}_{path.name}"
            shutil.copy2(path, transfer_path)
            
            # ファイル転送情報を作成
            file_transfer = FileTransfer(
                file_id=transfer_id,
                filename=path.name,
                file_path=str(transfer_path),
                file_size=file_size,
                checksum=checksum,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=expires_hours),
                max_downloads=max_downloads
            )
            
            self.file_transfers[transfer_id] = file_transfer
            return file_transfer
        except Exception as e:
            print(f"ファイル転送作成エラー: {str(e)}")
            return None
    
    def get_file_transfer(self, transfer_id: str) -> Optional[FileTransfer]:
        """ファイル転送情報を取得"""
        transfer = self.file_transfers.get(transfer_id)
        
        if transfer:
            # 有効期限チェック
            if datetime.now() > transfer.expires_at:
                self.cleanup_file_transfer(transfer_id)
                return None
            
            # ダウンロード回数チェック
            if transfer.download_count >= transfer.max_downloads:
                return None
        
        return transfer
    
    def increment_download_count(self, transfer_id: str) -> bool:
        """ダウンロード回数を増加"""
        transfer = self.file_transfers.get(transfer_id)
        if transfer:
            transfer.download_count += 1
            return True
        return False
    
    def cleanup_file_transfer(self, transfer_id: str):
        """ファイル転送をクリーンアップ"""
        transfer = self.file_transfers.get(transfer_id)
        if transfer:
            try:
                Path(transfer.file_path).unlink(missing_ok=True)
                del self.file_transfers[transfer_id]
            except Exception as e:
                print(f"ファイル転送クリーンアップエラー: {str(e)}")
    
    def create_agent_command(self, command_type: CommandType, source_device: str, 
                           target_device: str, payload: Dict) -> Optional[str]:
        """エージェントコマンドを作成"""
        try:
            command_id = hashlib.md5(f"{command_type.value}{source_device}{target_device}{datetime.now()}".encode()).hexdigest()[:8]
            
            command = AgentCommand(
                command_id=command_id,
                command_type=command_type,
                source_device=source_device,
                target_device=target_device,
                payload=payload,
                created_at=datetime.now()
            )
            
            self.agent_commands[command_id] = command
            self.command_history.append(command)
            return command_id
        except Exception as e:
            print(f"エージェントコマンド作成エラー: {str(e)}")
            return None
    
    def execute_adb_command(self, device_id: str, command: str) -> Dict:
        """ADBコマンドを実行"""
        if not self.adb_available:
            return {"success": False, "error": "ADBが利用できません"}
        
        if device_id not in self.connected_android_devices:
            return {"success": False, "error": "デバイスが接続されていません"}
        
        try:
            # コマンドを実行
            result = subprocess.run(["adb", "-s", device_id, "shell", command], 
                                  capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "コマンドタイムアウト"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remote_adb_operation(self, device_id: str, operation: str, **kwargs) -> Dict:
        """リモートADB操作"""
        operations = {
            "send_file": self._adb_send_file,
            "pull_file": self._adb_pull_file,
            "install_apk": self._adb_install_apk,
            "delete_file": self._adb_delete_file,
            "list_files": self._adb_list_files,
            "get_info": self._adb_get_device_info
        }
        
        if operation not in operations:
            return {"success": False, "error": "不明な操作: " + operation}
        
        return operations[operation](device_id, **kwargs)
    
    def _adb_send_file(self, device_id: str, local_path: str, remote_path: str) -> Dict:
        """ファイルをAndroidデバイスに送信"""
        try:
            result = subprocess.run(["adb", "-s", device_id, "push", local_path, remote_path], 
                                  capture_output=True, text=True, timeout=60)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _adb_pull_file(self, device_id: str, remote_path: str, local_path: str) -> Dict:
        """Androidデバイスからファイルを取得"""
        try:
            result = subprocess.run(["adb", "-s", device_id, "pull", remote_path, local_path], 
                                  capture_output=True, text=True, timeout=60)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _adb_install_apk(self, device_id: str, apk_path: str) -> Dict:
        """APKをインストール"""
        try:
            result = subprocess.run(["adb", "-s", device_id, "install", apk_path], 
                                  capture_output=True, text=True, timeout=120)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _adb_delete_file(self, device_id: str, remote_path: str) -> Dict:
        """ファイルを削除"""
        try:
            result = self.execute_adb_command(device_id, f"rm {remote_path}")
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _adb_list_files(self, device_id: str, remote_path: str = "/sdcard/") -> Dict:
        """ファイル一覧を取得"""
        try:
            result = self.execute_adb_command(device_id, f"ls -la {remote_path}")
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _adb_get_device_info(self, device_id: str) -> Dict:
        """デバイス情報を取得"""
        try:
            info = {}
            
            # モデル情報
            model_result = self.execute_adb_command(device_id, "getprop ro.product.model")
            if model_result["success"]:
                info["model"] = model_result["output"].strip()
            
            # Androidバージョン
            version_result = self.execute_adb_command(device_id, "getprop ro.build.version.release")
            if version_result["success"]:
                info["android_version"] = version_result["output"].strip()
            
            # バッテリー情報
            battery_result = self.execute_adb_command(device_id, "dumpsys battery | grep level")
            if battery_result["success"]:
                info["battery_level"] = battery_result["output"].strip()
            
            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_universal_link(self, transfer_id: str, base_url: str) -> str:
        """ユニバーサルリンクを生成"""
        return f"{base_url}/download/{transfer_id}"
    
    def generate_qr_code_for_link(self, link: str) -> str:
        """リンク用のQRコードを生成"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            print(f"QRコード生成エラー: {str(e)}")
            return ""
    
    def get_connected_devices(self) -> List[DeviceInfo]:
        """接続中デバイス一覧を取得"""
        return list(self.connected_devices.values())
    
    def get_device_by_id(self, device_id: str) -> Optional[DeviceInfo]:
        """デバイスIDでデバイス情報を取得"""
        return self.connected_devices.get(device_id)
    
    def cleanup_expired_transfers(self):
        """期限切れのファイル転送をクリーンアップ"""
        current_time = datetime.now()
        expired_transfers = []
        
        for transfer_id, transfer in self.file_transfers.items():
            if current_time > transfer.expires_at:
                expired_transfers.append(transfer_id)
        
        for transfer_id in expired_transfers:
            self.cleanup_file_transfer(transfer_id)
    
    def get_system_status(self) -> Dict:
        """システムステータスを取得"""
        return {
            "adb_available": self.adb_available,
            "connected_android_devices": len(self.connected_android_devices),
            "total_connected_devices": len(self.connected_devices),
            "active_file_transfers": len(self.file_transfers),
            "pending_commands": len([cmd for cmd in self.agent_commands.values() if cmd.status == "pending"]),
            "device_types": {
                device_type.value: len([d for d in self.connected_devices.values() if d.device_type == device_type])
                for device_type in DeviceType
            }
        }

class CrossDeviceGUI:
    """クロスデバイス連携GUI"""
    
    def __init__(self, collaboration: CrossDeviceCollaboration):
        self.collaboration = collaboration
    
    def render(self):
        """GUIを描画"""
        st.subheader("🔄 クロスデバイス連携")
        
        # システムステータス
        status = self.collaboration.get_system_status()
        
        # ステータス表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "ADB利用可能",
                "✅" if status["adb_available"] else "❌",
                help="Android Debug Bridgeの利用可否"
            )
        
        with col2:
            st.metric(
                "接続デバイス",
                status["total_connected_devices"],
                help="現在接続中のデバイス数"
            )
        
        with col3:
            st.metric(
                "ファイル転送",
                status["active_file_transfers"],
                help="アクティブなファイル転送数"
            )
        
        with col4:
            st.metric(
                "待機コマンド",
                status["pending_commands"],
                help="実行待ちのコマンド数"
            )
        
        # デバイス管理
        st.write("**📱 接続デバイス管理**")
        
        devices = self.collaboration.get_connected_devices()
        if devices:
            for device in devices:
                with st.expander(f"{device.device_id} ({device.device_type.value.upper()})", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"- IPアドレス: {device.ip_address}")
                        st.write(f"- ステータス: {device.status}")
                        st.write(f"- 最終接続: {device.last_seen.strftime('%H:%M:%S')}")
                    
                    with col2:
                        st.write(f"- ケイパビリティ: {', '.join(device.capabilities)}")
                        
                        if device.device_type == DeviceType.ANDROID:
                            if st.button(f"📱 {device.device_id} にファイル送信", key=f"send_{device.device_id}"):
                                self._show_file_transfer_dialog(device.device_id)
                            
                            if st.button(f"ℹ️ {device.device_id} 情報取得", key=f"info_{device.device_id}"):
                                info = self.collaboration._adb_get_device_info(device.device_id)
                                if info["success"]:
                                    st.json(info["info"])
                                else:
                                    st.error(f"情報取得失敗: {info['error']}")
        else:
            st.info("接続中のデバイスがありません")
        
        # Androidデバイススキャン
        if st.button("🔍 Androidデバイスをスキャン"):
            with st.spinner("スキャン中..."):
                self.collaboration._scan_android_devices()
                self.collaboration._save_device_info()
                st.success("スキャン完了！")
                st.rerun()
        
        # ファイル転送管理
        st.write("**📁 ファイル転送管理**")
        
        # ファイルアップロード
        uploaded_file = st.file_uploader(
            "ファイルをアップロードして転送を作成",
            type=None,
            help="アップロードしたファイルを外部デバイスからダウンロードできるようにします"
        )
        
        if uploaded_file:
            # 一時ファイルに保存
            temp_path = Path(f"temp_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # ファイル転送を作成
            transfer = self.collaboration.create_file_transfer(str(temp_path))
            
            if transfer:
                # ユニバーサルリンクとQRコードを生成
                if hasattr(st.session_state, 'network_config'):
                    base_url = st.session_state.network_config.get_external_url()
                else:
                    base_url = "http://localhost:8000"
                
                download_link = self.collaboration.generate_universal_link(transfer.file_id, base_url)
                qr_code = self.collaboration.generate_qr_code_for_link(download_link)
                
                st.success(f"✅ ファイル転送を作成しました: {transfer.filename}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📱 ダウンロードリンク**")
                    st.code(download_link)
                
                with col2:
                    if qr_code:
                        st.write("**📱 QRコード**")
                        st.image(qr_code, width=200, caption="スキャンしてダウンロード")
                
                # 転送情報
                with st.expander("転送詳細", expanded=False):
                    st.write(f"- ファイルID: {transfer.file_id}")
                    st.write(f"- ファイルサイズ: {transfer.file_size:,} バイト")
                    st.write(f"- 有効期限: {transfer.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"- 最大ダウンロード回数: {transfer.max_downloads}")
                    st.write(f"- 現在ダウンロード回数: {transfer.download_count}")
                
                # 一時ファイルを削除
                temp_path.unlink(missing_ok=True)
            else:
                st.error("❌ ファイル転送の作成に失敗しました")
        
        # アクティブな転送一覧
        if self.collaboration.file_transfers:
            st.write("**🔄 アクティブな転送**")
            
            for transfer_id, transfer in self.collaboration.file_transfers.items():
                with st.expander(f"{transfer.filename} ({transfer.download_count}/{transfer.max_downloads})", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"- 作成時刻: {transfer.created_at.strftime('%H:%M:%S')}")
                        st.write(f"- 有効期限: {transfer.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    with col2:
                        st.write(f"- ファイルサイズ: {transfer.file_size:,} バイト")
                        st.write(f"- ダウンロード回数: {transfer.download_count}/{transfer.max_downloads}")
                    
                    if st.button(f"🗑️ 削除", key=f"delete_{transfer_id}"):
                        self.collaboration.cleanup_file_transfer(transfer_id)
                        st.success("転送を削除しました")
                        st.rerun()
        
        # エージェント通信
        st.write("**🤖 エージェント間通信**")
        
        with st.expander("コマンド送信テスト", expanded=False):
            target_device = st.selectbox(
                "ターゲットデバイス",
                [device.device_id for device in devices],
                key="target_device"
            )
            
            command_type = st.selectbox(
                "コマンドタイプ",
                [cmd_type.value for cmd_type in CommandType],
                key="command_type"
            )
            
            payload = st.text_area(
                "ペイロード (JSON)",
                value='{"message": "テストメッセージ"}',
                key="payload"
            )
            
            if st.button("📤 コマンド送信"):
                try:
                    payload_dict = json.loads(payload)
                    command_id = self.collaboration.create_agent_command(
                        CommandType(command_type),
                        "pc",
                        target_device,
                        payload_dict
                    )
                    
                    if command_id:
                        st.success(f"✅ コマンドを送信しました: {command_id}")
                    else:
                        st.error("❌ コマンド送信に失敗しました")
                except json.JSONDecodeError:
                    st.error("❌ ペイロードが有効なJSONではありません")
        
        # システム情報
        if st.button("📊 システムステータス詳細"):
            st.json(status)

# FastAPIエンドポイント
def setup_cross_device_endpoints(app: FastAPI, collaboration: CrossDeviceCollaboration):
    """クロスデバイス連携用のFastAPIエンドポイントを設定"""
    
    @app.get("/download/{transfer_id}")
    async def download_file(transfer_id: str):
        """ファイルダウンロードエンドポイント"""
        transfer = collaboration.get_file_transfer(transfer_id)
        
        if not transfer:
            raise HTTPException(status_code=404, detail="ファイル転送が見つかりません")
        
        # ダウンロード回数を増加
        collaboration.increment_download_count(transfer_id)
        
        # ファイルを返す
        return FileResponse(
            transfer.file_path,
            media_type='application/octet-stream',
            filename=transfer.filename
        )
    
    @app.post("/upload")
    async def upload_file(file: UploadFile = File(...), device_id: str = Form(...)):
        """ファイルアップロードエンドポイント"""
        try:
            # アップロードディレクトリを作成
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            # ファイルを保存
            file_path = upload_dir / f"{device_id}_{file.filename}"
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # デバイスを登録（まだの場合）
            if device_id not in collaboration.connected_devices:
                collaboration.register_device(
                    device_id=device_id,
                    device_type=DeviceType.UNKNOWN,
                    ip_address="unknown",
                    capabilities=["file_upload"]
                )
            
            return {
                "success": True,
                "filename": file.filename,
                "file_path": str(file_path),
                "size": len(content)
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"アップロードエラー: {str(e)}")
    
    @app.post("/agent/command")
    async def agent_command(command: Dict):
        """エージェントコマンド受信エンドポイント"""
        try:
            command_id = command.get("command_id")
            if not command_id:
                raise HTTPException(status_code=400, detail="command_idが必要です")
            
            # コマンドを処理
            agent_command = collaboration.agent_commands.get(command_id)
            if not agent_command:
                raise HTTPException(status_code=404, detail="コマンドが見つかりません")
            
            # レスポンスを更新
            agent_command.response = command.get("response")
            agent_command.status = command.get("status", "completed")
            
            return {"success": True, "message": "コマンドを受信しました"}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"コマンド処理エラー: {str(e)}")
    
    @app.get("/devices")
    async def get_devices():
        """接続デバイス一覧エンドポイント"""
        devices = collaboration.get_connected_devices()
        return {
            "devices": [
                {
                    "device_id": device.device_id,
                    "device_type": device.device_type.value,
                    "ip_address": device.ip_address,
                    "status": device.status,
                    "capabilities": device.capabilities,
                    "last_seen": device.last_seen.isoformat()
                }
                for device in devices
            ]
        }
    
    @app.post("/device/register")
    async def register_device(device_info: Dict):
        """デバイス登録エンドポイント"""
        try:
            device_id = device_info.get("device_id")
            device_type = DeviceType(device_info.get("device_type", "unknown"))
            ip_address = device_info.get("ip_address", "")
            capabilities = device_info.get("capabilities", [])
            
            success = collaboration.register_device(device_id, device_type, ip_address, capabilities)
            
            if success:
                return {"success": True, "message": "デバイスを登録しました"}
            else:
                return {"success": False, "message": "デバイス登録に失敗しました"}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"デバイス登録エラー: {str(e)}")

# メイン関数
def create_cross_device_collaboration():
    """クロスデバイス連携システムを作成"""
    collaboration = CrossDeviceCollaboration()
    return collaboration

def create_cross_device_gui(collaboration: CrossDeviceCollaboration):
    """クロスデバイス連携GUIを作成"""
    gui = CrossDeviceGUI(collaboration)
    gui.render()
    return collaboration
