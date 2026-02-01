#!/usr/bin/env python3
"""
Windowsタスクスケジューラによる自動起動設定
"""

import os
import sys
import subprocess
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoStartSetup:
    def __init__(self):
        self.batch_file = os.path.join(os.getcwd(), 'docker_startup.bat')
        self.task_name = "AI Agent System Auto Start"
        self.description = "AI Agent SystemをPC起動時に自動で起動します"
    
    def check_admin_privileges(self):
        """管理者権限を確認"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def create_task_scheduler(self):
        """タスクスケジューラに登録"""
        logger.info("📅 タスクスケジューラに登録します...")
        
        # タスク作成コマンド
        cmd = [
            'schtasks',
            '/create',
            f'/tn "{self.task_name}"',
            f'/tr "{self.batch_file}"',
            '/sc', 'onlogon',
            '/rl', 'highest',
            '/f',
            f'/d', self.description
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                logger.info("✅ タスクスケジューラへの登録完了")
                return True
            else:
                logger.error(f"❌ タスク登録失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ タスク登録エラー: {e}")
            return False
    
    def check_task_exists(self):
        """タスクが存在するか確認"""
        try:
            result = subprocess.run(
                ['schtasks', '/query', f'/tn "{self.task_name}"'],
                capture_output=True, text=True, shell=True
            )
            
            return result.returncode == 0
        except:
            return False
    
    def delete_task(self):
        """タスクを削除"""
        logger.info("🗑️ 既存のタスクを削除します...")
        
        try:
            result = subprocess.run(
                ['schtasks', '/delete', f'/tn "{self.task_name}"', '/f'],
                capture_output=True, text=True, shell=True
            )
            
            if result.returncode == 0:
                logger.info("✅ タスク削除完了")
                return True
            else:
                logger.warning(f"⚠️ タスク削除失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ タスク削除エラー: {e}")
            return False
    
    def setup_docker_autostart(self):
        """Docker Desktopの自動起動設定"""
        logger.info("🐳 Docker Desktopの自動起動を設定します...")
        
        try:
            # Docker Desktopの自動起動レジストリ設定
            import winreg
            
            # Docker Desktopのレジストリパス
            docker_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, docker_path, 0, winreg.KEY_WRITE) as key:
                    # Docker Desktopの実行パス
                    docker_exe = r'"C:\Program Files\Docker\Docker\Docker Desktop.exe"'
                    winreg.SetValueEx(key, "Docker Desktop", 0, winreg.REG_SZ, docker_exe)
                    logger.info("✅ Docker Desktop自動起動設定完了")
                    return True
            except FileNotFoundError:
                # レジストリキーを作成
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, docker_path) as key:
                    docker_exe = r'"C:\Program Files\Docker\Docker\Docker Desktop.exe"'
                    winreg.SetValueEx(key, "Docker Desktop", 0, winreg.REG_SZ, docker_exe)
                    logger.info("✅ Docker Desktop自動起動設定完了（新規作成）")
                    return True
                    
        except ImportError:
            logger.warning("⚠️ winregモジュールが利用できません")
            logger.info("💡 手動でDocker Desktopの自動起動を設定してください")
            return False
        except Exception as e:
            logger.error(f"❌ Docker Desktop設定エラー: {e}")
            return False
    
    def create_startup_shortcut(self):
        """スタートアップフォルダにショートカットを作成"""
        logger.info("🔗 スタートアップショートカットを作成します...")
        
        try:
            import winshell
            from win32com.client import Dispatch
            
            # スタートアップフォルダのパス
            startup_folder = winshell.startup()
            
            # ショートカットの作成
            shortcut_path = os.path.join(startup_folder, "AI Agent System.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = self.batch_file
            shortcut.WorkingDirectory = os.getcwd()
            shortcut.IconLocation = "shell32.dll, 167"  # コンピューターアイコン
            shortcut.save()
            
            logger.info("✅ スタートアップショートカット作成完了")
            return True
            
        except ImportError:
            logger.warning("⚠️ winshellモジュールが利用できません")
            logger.info("💡 pip install winshell でインストールしてください")
            return False
        except Exception as e:
            logger.error(f"❌ ショートカット作成エラー: {e}")
            return False
    
    def setup(self):
        """自動起動設定全体"""
        logger.info("🚀 AI Agent System 自動起動設定")
        logger.info("=" * 50)
        
        # 管理者権限の確認
        if not self.check_admin_privileges():
            logger.error("❌ 管理者権限で実行してください")
            logger.info("💡 右クリックして「管理者として実行」を選択してください")
            return False
        
        # 既存タスクの確認と削除
        if self.check_task_exists():
            logger.info("📋 既存のタスクが見つかりました")
            if not self.delete_task():
                return False
        
        # タスクスケジューラへの登録
        if not self.create_task_scheduler():
            return False
        
        # Docker Desktopの自動起動設定
        self.setup_docker_autostart()
        
        # スタートアップショートカットの作成
        self.create_startup_shortcut()
        
        logger.info("✅ 自動起動設定完了")
        logger.info("")
        logger.info("🎯 設定内容:")
        logger.info(f"   タスク名: {self.task_name}")
        logger.info(f"   実行ファイル: {self.batch_file}")
        logger.info("")
        logger.info("🔄 次回PC起動時に自動で起動します")
        logger.info("💡 設定を削除するには: schtasks /delete \"%s\"" % self.task_name)
        
        return True

def main():
    """メイン処理"""
    print("🚀 AI Agent System 自動起動設定ツール")
    print("=" * 50)
    
    setup = AutoStartSetup()
    
    try:
        success = setup.setup()
        if success:
            print("\n🎉 自動起動設定が完了しました！")
            print("\n💡 次回PC起動時にAI Agent Systemが自動で起動します")
            print("\n🔧 設定確認:")
            print("   タスクスケジューラ: タスクスケジューラで 'AI Agent System Auto Start' を確認")
            print("   スタートアップ: スタートアップフォルダにショートカットを確認")
            print("\n⚠️ 設定を削除する場合:")
            print("   schtasks /delete \"AI Agent System Auto Start\"")
        else:
            print("\n❌ 自動起動設定に失敗しました")
            print("💡 管理者権限で実行してください")
            
        input("\nEnterキーを押して終了...")
        
    except KeyboardInterrupt:
        print("\n👋 設定を中断しました")
    except Exception as e:
        print(f"\n❌ 設定エラー: {e}")

if __name__ == "__main__":
    main()
