#!/usr/bin/env python3
"""
ネットワーク設定モジュール
IPアドレス自動取得と外部アクセス設定
"""

import socket
import subprocess
import platform
import re
from typing import Optional, List, Tuple
import qrcode
from io import BytesIO
import base64
import streamlit as st
from pathlib import Path

class NetworkConfig:
    """ネットワーク設定管理"""
    
    def __init__(self):
        self.local_ip = None
        self.public_ip = None
        self.port = 8000
        self.hostname = socket.gethostname()
        
        # IPアドレスを自動取得
        self.local_ip = self.get_local_ip()
        
        # ネットワークインターフェース情報
        self.interfaces = self.get_network_interfaces()
    
    def get_local_ip(self) -> Optional[str]:
        """ローカルIPアドレスを取得（Tailscale IPを優先）"""
        # Tailscale IPを優先的に取得
        tailscale_ip = self._get_tailscale_ip()
        if tailscale_ip:
            return tailscale_ip
        
        try:
            # 方法1: socketを使用して接続先IPを取得
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # GoogleのDNSサーバーに接続（実際には接続しない）
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                return local_ip
        except Exception:
            pass
        
        try:
            # 方法2: hostnameからIPを取得
            local_ip = socket.gethostbyname(self.hostname)
            # 127.0.0.1でないことを確認
            if local_ip.startswith("127.") or local_ip.startswith("localhost"):
                raise Exception("Localhost address detected")
            return local_ip
        except Exception:
            pass
        
        try:
            # 方法3: ipconfig/ifconfigを解析
            if platform.system().lower() == "windows":
                return self._parse_ipconfig()
            else:
                return self._parse_ifconfig()
        except Exception:
            pass
        
        # フォールバック
        return "127.0.0.1"
    
    def _get_tailscale_ip(self) -> Optional[str]:
        """Tailscale IPアドレスを取得"""
        try:
            # 方法1: Tailscaleコマンドを使用
            if platform.system().lower() == "windows":
                result = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    ip = result.stdout.strip()
                    if ip.startswith("100.") and self._is_valid_ip(ip):
                        return ip
            else:
                # Linux/Mac
                result = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    ip = result.stdout.strip()
                    if ip.startswith("100.") and self._is_valid_ip(ip):
                        return ip
        except Exception:
            pass
        
        # 方法2: ネットワークインターフェースからTailscale IPを検索
        try:
            interfaces = self.get_network_interfaces()
            for interface in interfaces:
                if interface.get("ipv4", "").startswith("100.") and self._is_valid_ip(interface["ipv4"]):
                    return interface["ipv4"]
        except Exception:
            pass
        
        # 方法3: ipconfig/ifconfigからTailscale IPを検索
        try:
            if platform.system().lower() == "windows":
                return self._parse_tailscale_ipconfig()
            else:
                return self._parse_tailscale_ifconfig()
        except Exception:
            pass
        
        return None
    
    def _is_valid_ip(self, ip: str) -> bool:
        """IPアドレスの形式を検証"""
        try:
            socket.inet_aton(ip)
            parts = ip.split(".")
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False
    
    def _parse_tailscale_ipconfig(self) -> Optional[str]:
        """Windows ipconfigからTailscale IPを解析"""
        try:
            result = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # Tailscaleアダプターを検索
            tailscale_blocks = re.findall(r"Tailscale[^\n]*\n(?:[ \t][^\n]*\n)*", output, re.IGNORECASE)
            
            for block in tailscale_blocks:
                # IPv4アドレスを検索
                ipv4_match = re.search(r"IPv4 Address[\. ]*: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", block)
                if ipv4_match:
                    ip = ipv4_match.group(1)
                    if ip.startswith("100.") and self._is_valid_ip(ip):
                        return ip
        
        except Exception as e:
            print(f"Tailscale ipconfig解析エラー: {str(e)}")
        
        return None
    
    def _parse_tailscale_ifconfig(self) -> Optional[str]:
        """Linux/Mac ifconfigからTailscale IPを解析"""
        try:
            result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # Tailscaleインターフェースを検索
            tailscale_blocks = re.findall(r"tailscale[0-9]*[^\n]*\n(?:[ \t][^\n]*\n)*", output, re.IGNORECASE)
            
            for block in tailscale_blocks:
                # inetアドレスを検索
                inet_match = re.search(r"inet ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", block)
                if inet_match:
                    ip = inet_match.group(1)
                    if ip.startswith("100.") and self._is_valid_ip(ip):
                        return ip
        
        except Exception as e:
            print(f"Tailscale ifconfig解析エラー: {str(e)}")
        
        return None
    
    def _parse_ipconfig(self) -> Optional[str]:
        """Windows ipconfigを解析"""
        try:
            result = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # IPv4アドレスを検索
            ipv4_pattern = r"IPv4 Address[\. ]*: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
            matches = re.findall(ipv4_pattern, output)
            
            # 192.168.x.x, 10.x.x.x, 172.16-31.x.x の優先順位で返す
            priority_patterns = [
                r"192\.168\.[0-9]{1,3}\.[0-9]{1,3}",
                r"10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                r"172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3}"
            ]
            
            for pattern in priority_patterns:
                for match in matches:
                    if re.match(pattern, match):
                        return match
            
            # 見つからなければ最初のプライベートIPを返す
            for match in matches:
                if not match.startswith("127.") and not match.startswith("169.254."):
                    return match
        
        except Exception as e:
            print(f"ipconfig解析エラー: {str(e)}")
        
        return None
    
    def _parse_ifconfig(self) -> Optional[str]:
        """Linux/Mac ifconfigを解析"""
        try:
            result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # inetアドレスを検索
            inet_pattern = r"inet ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
            matches = re.findall(inet_pattern, output)
            
            # 127.0.0.1を除外して最初のIPを返す
            for match in matches:
                if not match.startswith("127.") and not match.startswith("169.254."):
                    return match
        
        except Exception as e:
            print(f"ifconfig解析エラー: {str(e)}")
        
        return None
    
    def get_network_interfaces(self) -> List[Dict]:
        """ネットワークインターフェース情報を取得"""
        interfaces = []
        
        try:
            if platform.system().lower() == "windows":
                interfaces = self._get_windows_interfaces()
            else:
                interfaces = self._get_unix_interfaces()
        except Exception as e:
            print(f"インターフェース取得エラー: {str(e)}")
        
        return interfaces
    
    def _get_windows_interfaces(self) -> List[Dict]:
        """Windowsのネットワークインターフェースを取得"""
        interfaces = []
        
        try:
            result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # アダプター情報を解析
            adapter_blocks = re.split(r"\n\n", output)
            
            for block in adapter_blocks:
                if "adapter" in block.lower():
                    # アダプター名
                    name_match = re.search(r"adapter ([^:]+):", block, re.IGNORECASE)
                    if name_match:
                        name = name_match.group(1).strip()
                        
                        # IPv4アドレス
                        ipv4_match = re.search(r"IPv4 Address[\. ]*: ([0-9\.]+)", block)
                        ipv4 = ipv4_match.group(1) if ipv4_match else None
                        
                        # MACアドレス
                        mac_match = re.search(r"Physical Address[\. ]*: ([0-9A-Fa-f\-]+)", block)
                        mac = mac_match.group(1) if mac_match else None
                        
                        if ipv4 and not ipv4.startswith("127."):
                            interfaces.append({
                                "name": name,
                                "ipv4": ipv4,
                                "mac": mac,
                                "type": "Ethernet" if "Ethernet" in block else "Wireless" if "Wireless" in block else "Other"
                            })
        
        except Exception as e:
            print(f"Windowsインターフェース取得エラー: {str(e)}")
        
        return interfaces
    
    def _get_unix_interfaces(self) -> List[Dict]:
        """Unix系のネットワークインターフェースを取得"""
        interfaces = []
        
        try:
            result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # インターフェースブロックを解析
            interface_blocks = re.split(r"\n(?=[a-zA-Z0-9])", output)
            
            for block in interface_blocks:
                if ":" in block:
                    lines = block.split("\n")
                    if len(lines) > 0:
                        name = lines[0].split(":")[0].strip()
                        
                        # IPv4アドレス
                        ipv4_match = re.search(r"inet ([0-9\.]+)", block)
                        ipv4 = ipv4_match.group(1) if ipv4_match else None
                        
                        # MACアドレス
                        mac_match = re.search(r"ether ([0-9A-Fa-f:]+)", block)
                        mac = mac_match.group(1) if mac_match else None
                        
                        if ipv4 and not ipv4.startswith("127."):
                            interfaces.append({
                                "name": name,
                                "ipv4": ipv4,
                                "mac": mac,
                                "type": "Ethernet" if "eth" in name.lower() else "Wireless" if "wlan" in name.lower() or "wifi" in name.lower() else "Other"
                            })
        
        except Exception as e:
            print(f"Unixインターフェース取得エラー: {str(e)}")
        
        return interfaces
    
    def get_external_url(self) -> str:
        """外部アクセスURLを取得"""
        if self.local_ip:
            return f"http://{self.local_ip}:{self.port}"
        return f"http://127.0.0.1:{self.port}"
    
    def generate_qr_code(self, url: str) -> str:
        """QRコードを生成（base64エンコード）"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # 画像をバイトデータに変換
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            
            # base64エンコード
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_base64}"
        
        except Exception as e:
            print(f"QRコード生成エラー: {str(e)}")
            return ""
    
    def check_port_availability(self, port: int) -> bool:
        """ポートが利用可能かチェック"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                s.close()
                return True
        except OSError:
            return False
    
    def find_available_port(self, start_port: int = 8000, max_port: int = 8010) -> int:
        """利用可能なポートを探す"""
        for port in range(start_port, max_port + 1):
            if self.check_port_availability(port):
                return port
        return start_port  # フォールバック
    
    def get_connection_info(self) -> Dict:
        """接続情報を取得"""
        return {
            "local_ip": self.local_ip,
            "hostname": self.hostname,
            "port": self.port,
            "external_url": self.get_external_url(),
            "interfaces": self.interfaces,
            "is_localhost": self.local_ip == "127.0.0.1",
            "platform": platform.system(),
            "is_tailscale": self.local_ip.startswith("100.") if self.local_ip else False,
            "tailscale_status": self._check_tailscale_status()
        }
    
    def _check_tailscale_status(self) -> Dict:
        """Tailscaleの状態をチェック"""
        status = {
            "installed": False,
            "running": False,
            "ip_found": False,
            "version": None
        }
        
        try:
            # Tailscaleがインストールされているかチェック
            result = subprocess.run(["tailscale", "version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                status["installed"] = True
                version_match = re.search(r"tailscale v?([0-9.]+)", result.stdout)
                if version_match:
                    status["version"] = version_match.group(1)
            
            # Tailscaleが実行中かチェック
            result = subprocess.run(["tailscale", "status"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                status["running"] = True
                # IPが見つかったかチェック
                if self.local_ip and self.local_ip.startswith("100."):
                    status["ip_found"] = True
        
        except Exception:
            pass
        
        return status
    
    def test_connectivity(self) -> Dict:
        """接続テスト"""
        results = {
            "local_connectivity": False,
            "internet_connectivity": False,
            "dns_resolution": False,
            "port_status": {}
        }
        
        # ローカル接続テスト
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((self.local_ip or "127.0.0.1", self.port))
                results["local_connectivity"] = True
        except:
            pass
        
        # インターネット接続テスト
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(("8.8.8.8", 53))
                results["internet_connectivity"] = True
        except:
            pass
        
        # DNS解決テスト
        try:
            socket.gethostbyname("google.com")
            results["dns_resolution"] = True
        except:
            pass
        
        # ポートステータス
        test_ports = [8000, 8080, 3000, 5000]
        for port in test_ports:
            results["port_status"][port] = self.check_port_availability(port)
        
        return results

class NetworkConfigGUI:
    """ネットワーク設定GUI"""
    
    def __init__(self, network_config: NetworkConfig):
        self.network_config = network_config
    
    def render(self):
        """GUIを描画"""
        st.subheader("🌐 ネットワーク設定")
        
        # 接続情報
        info = self.network_config.get_connection_info()
        
        # Tailscaleステータス表示
        tailscale_status = info["tailscale_status"]
        
        if info["is_tailscale"]:
            st.success("🐉 Tailscale接続を検出しました！iPhoneからのアクセス準備完了です！")
        elif tailscale_status["installed"] and not tailscale_status["running"]:
            st.warning("⚠️ Tailscaleはインストールされていますが、実行されていません。")
        elif tailscale_status["installed"]:
            st.info("ℹ️ Tailscaleはインストールされていますが、IPアドレスが見つかりません。")
        else:
            st.info("ℹ️ Tailscaleが検出されません。通常のローカルネットワークを使用します。")
        
        # 外部アクセスURLの表示
        st.write("**🔗 外部アクセスURL**")
        
        if info["is_localhost"]:
            st.warning("⚠️ ローカルホストのみ検出されました。外部アクセスは制限されます。")
        
        # URL表示
        external_url = info["external_url"]
        st.code(external_url, language="text")
        
        # Tailscaleの場合の特別表示
        if info["is_tailscale"]:
            st.success("📱 このURLをiPhoneのブラウザまたはTailscaleアプリから直接アクセスできます！")
        
        # コピーボタン
        if st.button("📋 URLをコピー"):
            st.write("URLをクリップボードにコピーしました！（ブラウザの機能を使用）")
        
        # QRコード表示
        qr_code = self.network_config.generate_qr_code(external_url)
        if qr_code:
            st.write("**📱 QRコード（iPhone用）**")
            if info["is_tailscale"]:
                st.image(qr_code, width=200, caption="iPhoneでスキャンしてTailscale経由でアクセス")
            else:
                st.image(qr_code, width=200, caption="スマートフォンでスキャンしてアクセス")
        
        # 詳細情報
        with st.expander("📊 詳細ネットワーク情報", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**基本情報**")
                st.write(f"- ホスト名: {info['hostname']}")
                st.write(f"- ローカルIP: {info['local_ip']}")
                st.write(f"- ポート: {info['port']}")
                st.write(f"- プラットフォーム: {info['platform']}")
                st.write(f"- Tailscale: {'✅ 使用中' if info['is_tailscale'] else '❌ 未使用'}")
            
            with col2:
                st.write("**インターフェース**")
                for interface in info['interfaces']:
                    st.write(f"- {interface['name']}: {interface['ipv4']}")
                    st.write(f"  タイプ: {interface['type']}")
                    if interface['ipv4'].startswith("100."):
                        st.write(f"  🐉 Tailscaleインターフェース")
        
        # Tailscaleステータス詳細
        if tailscale_status["installed"]:
            with st.expander("🐉 Tailscale詳細", expanded=False):
                st.write("**Tailscaleステータス**")
                st.write(f"- インストール: {'✅' if tailscale_status['installed'] else '❌'}")
                st.write(f"- 実行中: {'✅' if tailscale_status['running'] else '❌'}")
                st.write(f"- IP検出: {'✅' if tailscale_status['ip_found'] else '❌'}")
                if tailscale_status["version"]:
                    st.write(f"- バージョン: {tailscale_status['version']}")
        
        # 接続テスト
        if st.button("🔍 接続テスト"):
            with st.spinner("接続テスト中..."):
                results = self.network_config.test_connectivity()
                
                st.write("**接続テスト結果**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("🟢" if results["local_connectivity"] else "🔴" + 
                           f" ローカル接続: {'OK' if results['local_connectivity'] else 'NG'}")
                    st.write("🟢" if results["internet_connectivity"] else "🔴" + 
                           f" インターネット接続: {'OK' if results['internet_connectivity'] else 'NG'}")
                
                with col2:
                    st.write("🟢" if results["dns_resolution"] else "🔴" + 
                           f" DNS解決: {'OK' if results['dns_resolution'] else 'NG'}")
                
                st.write("**ポート状態**")
                for port, available in results["port_status"].items():
                    status = "🟢 利用可能" if available else "🔴 使用中"
                    st.write(f"- ポート {port}: {status}")
        
        # ポート変更
        with st.expander("⚙️ ポート設定", expanded=False):
            new_port = st.number_input(
                "ポート番号",
                min_value=1024,
                max_value=65535,
                value=info["port"],
                step=1
            )
            
            if st.button("🔄 ポートを変更") and new_port != info["port"]:
                if self.network_config.check_port_availability(new_port):
                    self.network_config.port = new_port
                    st.success(f"✅ ポートを {new_port} に変更しました")
                    st.rerun()
                else:
                    st.error(f"❌ ポート {new_port} は使用中です")
        
        # iPhoneアクセスガイド
        st.write("**📱 iPhoneアクセスガイド**")
        
        if info["is_tailscale"]:
            guide_steps = [
                "1. 🐉 iPhoneでTailscaleアプリが起動していることを確認",
                "2. 📱 上記のQRコードをiPhoneでスキャン",
                "3. 🌐 またはURLを直接入力: " + external_url,
                "4. 🤖 AIアプリを起動",
                "5. 🔑 APIキーを入力: digital_human_2026_api_key",
                "6. ✅ 接続完了！iPhoneからAIと対話開始"
            ]
        else:
            guide_steps = [
                "1. 📱 上記のQRコードをスマートフォンでスキャン",
                "2. 🌐 またはURLを直接入力: " + external_url,
                "3. 🤖 AIアプリを起動",
                "4. 🔑 APIキーを入力: digital_human_2026_api_key",
                "5. ✅ 接続完了！AIと対話開始"
            ]
        
        for step in guide_steps:
            st.write(step)
        
        # Tailscaleセットアップガイド（未インストールの場合）
        if not tailscale_status["installed"]:
            st.write("**🐉 Tailscaleセットアップガイド（推奨）**")
            st.write("Tailscaleを使用すると、iPhoneから安全かつ高速にAIにアクセスできます！")
            
            setup_steps = [
                "1. 📱 iPhoneでTailscaleアプリをインストール",
                "2. 💻 PCでTailscaleをインストール: https://tailscale.com/download/",
                "3. 🔐 両方のデバイスで同じTailscaleアカウントにログイン",
                "4. 🔄 アプリを再起動すると、自動的にTailscale IPが検出されます",
                "5. 🎉 iPhoneから直接AIにアクセスできるようになります！"
            ]
            
            for step in setup_steps:
                st.write(step)
        
        # 音声案内
        if st.button("🔊 接続情報を音声で案内"):
            if info["is_tailscale"]:
                connection_text = f"iPhoneでTailscaleアプリが起動していることを確認してね！接続先アドレスは {external_url} です。QRコードをスキャンするか、このURLを直接入力してください。"
            else:
                connection_text = f"外部アクセスURLは {external_url} です。QRコードをスキャンするか、このURLを直接入力してください。"
            
            if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'text_to_speech'):
                st.session_state.agent.text_to_speech.speak_ai_response(connection_text)
                st.success("🔊 接続情報を音声で案内しました")
            else:
                st.warning("⚠️ 音声合成が利用できません")

# メイン関数
def create_network_config_gui():
    """ネットワーク設定GUIを作成"""
    network_config = NetworkConfig()
    gui = NetworkConfigGUI(network_config)
    gui.render()
    return network_config
