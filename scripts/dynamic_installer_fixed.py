#!/usr/bin/env python3
"""
動的ライブラリインストーラー - バージョン競合修正版
"""

import os
import sys
import subprocess
import importlib
import json
import logging
from datetime import datetime
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicInstallerFixed:
    def __init__(self):
        self.site_packages = self.get_site_packages_path()
        self.installed_packages_file = "/app/data/installed_packages.json"
        self.install_history_file = "/app/data/install_history.json"
        
        # データディレクトリの作成
        os.makedirs("/app/data", exist_ok=True)
        
        # インストール済みパッケージの読み込み
        self.installed_packages = self.load_installed_packages()
        self.install_history = self.load_install_history()
        
        # PyTorch互換性マップ
        self.pytorch_compatibility = {
            "torch": "2.1.0",
            "torchaudio": "2.1.0",
            "torchvision": "0.16.0"
        }
    
    def get_site_packages_path(self):
        """site-packagesのパスを取得"""
        import site
        site_packages = site.getsitepackages()
        if site_packages:
            return site_packages[0]
        return "/usr/local/lib/python3.10/site-packages"
    
    def load_installed_packages(self):
        """インストール済みパッケージを読み込み"""
        try:
            if os.path.exists(self.installed_packages_file):
                with open(self.installed_packages_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load installed packages: {e}")
        return {}
    
    def save_installed_packages(self):
        """インストール済みパッケージを保存"""
        try:
            with open(self.installed_packages_file, 'w', encoding='utf-8') as f:
                json.dump(self.installed_packages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save installed packages: {e}")
    
    def load_install_history(self):
        """インストール履歴を読み込み"""
        try:
            if os.path.exists(self.install_history_file):
                with open(self.install_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load install history: {e}")
        return []
    
    def save_install_history(self):
        """インストール履歴を保存"""
        try:
            with open(self.install_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.install_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save install history: {e}")
    
    def check_package_exists(self, package_name):
        """パッケージが存在するか確認"""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False
    
    def install_package(self, package_name, version=None, force_version=False):
        """パッケージをインストール（バージョン互換性考慮）"""
        logger.info(f"📦 Installing package: {package_name}")
        
        # PyTorch関連パッケージのバージョン互換性を確保
        if package_name in self.pytorch_compatibility and not force_version:
            version = self.pytorch_compatibility[package_name]
        
        # インストールコマンドの構築
        install_cmd = ["pip", "install", package_name]
        if version:
            install_cmd.append(f"{package_name}=={version}")
        
        # PyTorch関連の特別処理
        if package_name in ["torch", "torchaudio", "torchvision"]:
            install_cmd.extend(["--no-cache-dir", "--force-reinstall"])
        
        # インストール実行
        try:
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分タイムアウト
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully installed {package_name}")
                
                # キャッシュを無効化
                importlib.invalidate_caches()
                
                # インストール記録を保存
                self.record_installation(package_name, version, True, result.stdout)
                
                return True, result.stdout
            else:
                logger.error(f"❌ Failed to install {package_name}: {result.stderr}")
                self.record_installation(package_name, version, False, result.stderr)
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            error_msg = f"Installation timeout for {package_name}"
            logger.error(error_msg)
            self.record_installation(package_name, version, False, error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Installation error for {package_name}: {str(e)}"
            logger.error(error_msg)
            self.record_installation(package_name, version, False, error_msg)
            return False, error_msg
    
    def record_installation(self, package_name, version, success, message):
        """インストール記録を保存"""
        # インストール済みパッケージに追加
        if success:
            self.installed_packages[package_name] = {
                "version": version or "latest",
                "installed_at": datetime.now().isoformat(),
                "status": "success"
            }
        else:
            self.installed_packages[package_name] = {
                "version": version or "latest",
                "installed_at": datetime.now().isoformat(),
                "status": "failed",
                "error": message
            }
        
        self.save_installed_packages()
        
        # インストール履歴に追加
        history_entry = {
            "package": package_name,
            "version": version or "latest",
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.install_history.append(history_entry)
        self.save_install_history()
    
    def try_import_after_install(self, package_name):
        """インストール後にインポートを試行（エラーハンドリング強化）"""
        try:
            importlib.invalidate_caches()
            
            # PyTorch関連の特別処理
            if package_name in ["torchaudio", "torchvision"]:
                # まずtorchをインポート
                try:
                    import torch
                    logger.info("✅ torch imported successfully")
                except ImportError as torch_error:
                    logger.error(f"❌ Failed to import torch: {torch_error}")
                    return False, None
            
            # 対象パッケージをインポート
            module = importlib.import_module(package_name)
            logger.info(f"✅ Successfully imported {package_name}")
            return True, module
            
        except ImportError as e:
            logger.error(f"❌ Failed to import {package_name} after installation: {e}")
            
            # PyTorch関連のエラーの場合、バージョン不一致を疑う
            if package_name in ["torchaudio", "torchvision"] and "undefined symbol" in str(e):
                logger.warning(f"⚠️ Version conflict detected for {package_name}")
                return self.handle_pytorch_conflict(package_name)
            
            return False, None
        except Exception as e:
            logger.error(f"❌ Unexpected error importing {package_name}: {e}")
            return False, None
    
    def handle_pytorch_conflict(self, package_name):
        """PyTorchバージョン競合を処理"""
        logger.info(f"🔧 Handling PyTorch conflict for {package_name}")
        
        # 既存のPyTorch関連パッケージをアンインストール
        pytorch_packages = ["torch", "torchaudio", "torchvision"]
        
        for pkg in pytorch_packages:
            try:
                subprocess.run(["pip", "uninstall", "-y", pkg], capture_output=True, timeout=60)
                logger.info(f"🗑️ Uninstalled {pkg}")
            except:
                pass
        
        # 互換性のあるバージョンで再インストール
        for pkg in pytorch_packages:
            version = self.pytorch_compatibility[pkg]
            success, message = self.install_package(pkg, version, force_version=True)
            
            if not success:
                logger.error(f"❌ Failed to reinstall {pkg}: {message}")
                return False, None
        
        # 再度インポートを試行
        try:
            importlib.invalidate_caches()
            module = importlib.import_module(package_name)
            logger.info(f"✅ Successfully imported {package_name} after conflict resolution")
            return True, module
        except ImportError as e:
            logger.error(f"❌ Still failed to import {package_name}: {e}")
            return False, None
    
    def get_package_info(self, package_name):
        """パッケージ情報を取得"""
        try:
            result = subprocess.run(
                ["pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Package {package_name} not found"
        except Exception as e:
            return f"Error getting package info: {str(e)}"
    
    def list_installed_packages(self):
        """インストール済みパッケージを一覧表示"""
        return list(self.installed_packages.keys())
    
    def get_install_summary(self):
        """インストールサマリーを取得"""
        success_count = sum(1 for p in self.installed_packages.values() if p.get("status") == "success")
        failed_count = sum(1 for p in self.installed_packages.values() if p.get("status") == "failed")
        
        return {
            "total_packages": len(self.installed_packages),
            "successful": success_count,
            "failed": failed_count,
            "recent_installs": self.install_history[-5:] if self.install_history else []
        }

def install_package(package_name, version=None):
    """パッケージをインストールする関数（AIが呼び出す用）"""
    installer = DynamicInstallerFixed()
    
    # 既に存在するか確認
    if installer.check_package_exists(package_name):
        logger.info(f"✅ Package {package_name} already exists")
        return True, f"Package {package_name} is already installed"
    
    # インストール実行
    success, message = installer.install_package(package_name, version)
    
    if success:
        # インポート試行
        import_success, module = installer.try_import_after_install(package_name)
        if import_success:
            return True, f"✅ Successfully installed and imported {package_name}"
        else:
            return False, f"❌ Installed but failed to import {package_name}"
    else:
        return False, f"❌ Failed to install {package_name}: {message}"

def auto_install_missing_packages(error_message):
    """エラーメッセージから不足パッケージを自動検出・インストール"""
    logger.info("🔍 Auto-detecting missing packages...")
    
    # ModuleNotFoundErrorからパッケージ名を抽出
    if "ModuleNotFoundError" in error_message:
        # "No module named 'package_name'" 形式を抽出
        import re
        match = re.search(r"No module named '([^']+)'", error_message)
        if match:
            package_name = match.group(1)
            logger.info(f"🎯 Detected missing package: {package_name}")
            
            # 自動インストール
            success, message = install_package(package_name)
            return success, message, package_name
    
    return False, "Could not detect missing package", None

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("Usage: python dynamic_installer_fixed.py <package_name> [version]")
        return 1
    
    package_name = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else None
    
    success, message = install_package(package_name, version)
    
    if success:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ {message}")
        return 1

if __name__ == "__main__":
    exit(main())
