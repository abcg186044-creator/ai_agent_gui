import json
import os
import shutil
import ast
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import time
import threading

class CoderAgent:
    """
    自己進化型マルチエージェントシステムのCoderエージェント
    evolution_task.jsonを監視し、コード編集を実行する
    """
    
    def __init__(self):
        self.system_prompt = """
あなたはシステムのコードを安全に編集するCoderエージェントです。

役割：
1. evolution_task.jsonを監視し、タスクを自動で実行する
2. コード編集前に必ずバックアップを作成する
3. 編集後は構文エラーがないか自己診断する
4. 変更を安全かつ確実に実装する

安全性ルール：
- 編集前に必ずbackups/フォルダに現在のファイルをコピーする
- 構文チェックをパスしない変更は適用しない
- 重要なシステムファイルは慎重に扱う
"""
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def monitor_evolution_tasks(self):
        """
        evolution_task.jsonを監視し、タスクがあれば実行する
        """
        print("🤖 Coderエージェント: evolution_task.jsonの監視を開始...")
        
        while True:
            task_file = Path("evolution_task.json")
            
            if task_file.exists():
                try:
                    with open(task_file, "r", encoding="utf-8") as f:
                        evolution_data = json.load(f)
                    
                    # タスクがpending状態の場合のみ実行
                    if evolution_data.get("status") == "pending":
                        print(f"🔧 Coderエージェント: 進化タスクを検出 - {evolution_data['requirements']['feature_description']}")
                        
                        # タスクを実行
                        success = self.execute_evolution_task(evolution_data)
                        
                        # ステータスを更新
                        evolution_data["status"] = "completed" if success else "failed"
                        evolution_data["completed_at"] = datetime.now().isoformat()
                        
                        with open(task_file, "w", encoding="utf-8") as f:
                            json.dump(evolution_data, f, ensure_ascii=False, indent=2)
                            
                        if success:
                            print("✅ Coderエージェント: 進化タスクを完了しました")
                        else:
                            print("❌ Coderエージェント: 進化タスクの実行に失敗しました")
                            
                except Exception as e:
                    print(f"❌ Coderエージェント: エラーが発生しました - {e}")
                    
            time.sleep(2)  # 2秒ごとにチェック
    
    def execute_evolution_task(self, evolution_data: Dict) -> bool:
        """
        進化タスクを実行する
        
        Args:
            evolution_data: 進化要件データ
            
        Returns:
            実行成功フラグ
        """
        try:
            requirements = evolution_data["requirements"]
            
            # 1. バックアップを作成
            self.create_backup(requirements.get("target_files", []))
            
            # 2. コード編集を実行
            success = self.edit_code(requirements)
            
            if success:
                # 3. 構文チェックを実行
                syntax_ok = self.verify_syntax(requirements.get("target_files", []))
                
                if syntax_ok:
                    # 4. 人格定義を更新（必要な場合）
                    if requirements.get("new_personalities"):
                        self.update_personalities(requirements["new_personalities"])
                    
                    return True
                else:
                    print("❌ 構文エラーが検出されたため、変更をロールバックします")
                    self.rollback_changes(requirements.get("target_files", []))
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"❌ 進化タスク実行中にエラーが発生しました: {e}")
            return False
    
    def create_backup(self, target_files: List[str]):
        """
        対象ファイルのバックアップを作成する
        
        Args:
            target_files: バックアップ対象ファイルリスト
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / timestamp
        backup_subdir.mkdir(exist_ok=True)
        
        for file_path in target_files:
            source = Path(file_path)
            if source.exists():
                backup_path = backup_subdir / source.name
                shutil.copy2(source, backup_path)
                print(f"📁 バックアップ作成: {file_path} -> {backup_path}")
    
    def edit_code(self, requirements: Dict) -> bool:
        """
        コード編集を実行する
        
        Args:
            requirements: 進化要件
            
        Returns:
            編集成功フラグ
        """
        feature_desc = requirements["feature_description"]
        target_files = requirements.get("target_files", [])
        
        # 簡単な実装例 - 実際はより高度なコード生成が必要
        if "新しい人格" in feature_desc:
            return self.add_new_personality(requirements)
        elif "機能" in feature_desc:
            return self.add_new_feature(requirements)
        else:
            print(f"⚠️ 未対応の機能タイプ: {feature_desc}")
            return False
    
    def add_new_personality(self, requirements: Dict) -> bool:
        """新規人格を追加する"""
        personalities = requirements.get("new_personalities", [])
        
        if not personalities:
            return False
            
        # memory_db.jsonに新規人格を追加
        memory_file = Path("memory_db.json")
        
        try:
            if memory_file.exists():
                with open(memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)
            else:
                memory_data = {"personalities": {}}
            
            for personality in personalities:
                memory_data["personalities"][personality] = {
                    "name": personality,
                    "description": f"{personality}の人格",
                    "traits": ["friendly", "helpful"],
                    "created_at": datetime.now().isoformat()
                }
            
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
                
            print(f"✅ 新規人格を追加: {', '.join(personalities)}")
            return True
            
        except Exception as e:
            print(f"❌ 人格追加エラー: {e}")
            return False
    
    def add_new_feature(self, requirements: Dict) -> bool:
        """新規機能を追加する"""
        # 簡単な機能追加の例
        target_files = requirements.get("target_files", [])
        
        if not target_files:
            # デフォルトでメインファイルを対象
            target_files = ["ollama_vrm_integrated_app.py"]
        
        for file_path in target_files:
            success = self.add_feature_to_file(file_path, requirements)
            if not success:
                return False
                
        return True
    
    def add_feature_to_file(self, file_path: str, requirements: Dict) -> bool:
        """特定ファイルに機能を追加する"""
        try:
            file_obj = Path(file_path)
            
            if not file_obj.exists():
                print(f"⚠️ ファイルが存在しません: {file_path}")
                return False
            
            # ファイルを読み込み
            with open(file_obj, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 簡単な機能追加コードを生成（実際はより高度な生成が必要）
            feature_desc = requirements["feature_description"]
            new_code = f"""
    # 新規機能: {feature_desc}
    def new_feature_{datetime.now().strftime('%Y%m%d_%H%M%S')}():
        \"\"\"
        {feature_desc}
        \"\"\"
        print("新機能が実行されました: {feature_desc}")
        return True
"""
            
            # ファイルの末尾に追加
            updated_content = content + new_code
            
            # ファイルに書き込み
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
                
            print(f"✅ 機能を追加: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 機能追加エラー ({file_path}): {e}")
            return False
    
    def verify_syntax(self, target_files: List[str]) -> bool:
        """
        構文チェックを実行する
        
        Args:
            target_files: チェック対象ファイルリスト
            
        Returns:
            構文チェック結果
        """
        print("🔍 構文チェックを実行中...")
        
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                
                # Python構文チェック
                ast.parse(code)
                print(f"✅ 構文チェックOK: {file_path}")
                
            except SyntaxError as e:
                print(f"❌ 構文エラー ({file_path}): {e}")
                return False
            except Exception as e:
                print(f"❌ チェックエラー ({file_path}): {e}")
                return False
        
        return True
    
    def rollback_changes(self, target_files: List[str]):
        """
        変更をロールバックする
        
        Args:
            target_files: ロールバック対象ファイルリスト
        """
        print("🔄 変更をロールバック中...")
        
        # 最新のバックアップを取得
        latest_backup = self.get_latest_backup()
        
        if not latest_backup:
            print("❌ バックアップが見つかりません")
            return
        
        for file_path in target_files:
            source = Path(file_path)
            backup_file = latest_backup / source.name
            
            if backup_file.exists():
                shutil.copy2(backup_file, source)
                print(f"🔄 ロールバック: {file_path}")
    
    def get_latest_backup(self) -> Optional[Path]:
        """最新のバックアップディレクトリを取得"""
        if not self.backup_dir.exists():
            return None
        
        backup_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir()]
        if not backup_dirs:
            return None
        
        # タイムスタンプでソートして最新を取得
        backup_dirs.sort(key=lambda x: x.name, reverse=True)
        return backup_dirs[0]
    
    def update_personalities(self, new_personalities: List[str]):
        """
        人格定義を更新する
        
        Args:
            new_personalities: 新規人格リスト
        """
        # add_new_personalityで実装済み
        pass
    
    def start_monitoring(self):
        """監視を別スレッドで開始"""
        monitor_thread = threading.Thread(target=self.monitor_evolution_tasks, daemon=True)
        monitor_thread.start()
        print("🚀 Coderエージェントの監視を開始しました")
