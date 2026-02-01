"""
バックアップ管理モジュール
ファイルのバックアップ作成と復元を管理
"""

import os
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class BackupManager:
    """バックアップ管理クラス"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """単一ファイルのバックアップを作成"""
        try:
            source_file = Path(file_path)
            
            if not source_file.exists():
                print(f"警告: バックアップ対象ファイルが存在しません: {file_path}")
                return None
            
            # タイムスタンプ付きのバックアップファイル名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{source_file.stem}_{timestamp}{source_file.suffix}"
            backup_path = self.backup_dir / backup_filename
            
            # バックアップを作成
            shutil.copy2(source_file, backup_path)
            
            print(f"✅ バックアップ作成: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ バックアップ作成エラー: {e}")
            return None
    
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """バックアップから復元"""
        try:
            backup_file = Path(backup_path)
            target_file = Path(target_path)
            
            if not backup_file.exists():
                print(f"❌ バックアップファイルが存在しません: {backup_path}")
                return False
            
            # ターゲットディレクトリを作成
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 復元
            shutil.copy2(backup_file, target_file)
            
            print(f"✅ バックアップ復元: {backup_path} → {target_path}")
            return True
            
        except Exception as e:
            print(f"❌ バックアップ復元エラー: {e}")
            return False
    
    def list_backups(self, file_pattern: str = None) -> List[Dict]:
        """バックアップ一覧を取得"""
        backups = []
        
        try:
            for backup_file in self.backup_dir.glob("*.py"):
                # 元ファイル名を推定
                original_name = backup_file.stem.split('_')[0]
                
                if file_pattern and file_pattern not in original_name:
                    continue
                
                # ファイル情報を取得
                stat = backup_file.stat()
                
                backups.append({
                    "backup_path": str(backup_file),
                    "original_name": original_name,
                    "created_time": datetime.datetime.fromtimestamp(stat.st_mtime),
                    "size": stat.st_size
                })
            
            # 作成時間でソート
            backups.sort(key=lambda x: x["created_time"], reverse=True)
            
        except Exception as e:
            print(f"❌ バックアップ一覧取得エラー: {e}")
        
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """古いバックアップをクリーンアップ"""
        try:
            all_backups = self.list_backups()
            
            if len(all_backups) <= keep_count:
                return 0
            
            # 削除対象を特定
            to_delete = all_backups[keep_count:]
            deleted_count = 0
            
            for backup in to_delete:
                try:
                    Path(backup["backup_path"]).unlink()
                    deleted_count += 1
                    print(f"🗑️ 古いバックアップを削除: {backup['backup_path']}")
                except Exception as e:
                    print(f"❌ バックアップ削除エラー: {e}")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ バックアップクリーンアップエラー: {e}")
            return 0
    
    def get_latest_backup(self, original_file: str) -> Optional[str]:
        """最新のバックアップを取得"""
        try:
            original_name = Path(original_file).stem
            backups = self.list_backups(original_name)
            
            if backups:
                return backups[0]["backup_path"]
            
            return None
            
        except Exception as e:
            print(f"❌ 最新バックアップ取得エラー: {e}")
            return None

# グローバルインスタンス
backup_manager = BackupManager()
