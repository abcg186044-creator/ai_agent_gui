"""
ステートマネージャーモジュール
会話履歴、TODO、進化ルールのJSON保存・読み込みを管理
"""

import json
import os
import datetime
from pathlib import Path
from ..core.constants import *

def save_workspace_state():
    """ワークスペース状態を保存"""
    try:
        workspace_data = {
            'todo_list': st.session_state.get(SESSION_KEYS['todo_list'], []),
            'quick_memos': st.session_state.get(SESSION_KEYS['quick_memos'], []),
            'last_saved': datetime.datetime.now().isoformat()
        }
        
        # dataディレクトリを作成
        DATA_DIR.mkdir(exist_ok=True)
        
        # 保存
        with open(WORKSPACE_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(workspace_data, f, ensure_ascii=False, indent=2)
        
        print("✅ ワークスペース状態を保存しました")
        return True
        
    except Exception as e:
        print(f"❌ ワークスペース状態保存エラー: {e}")
        return False

def load_workspace_state():
    """ワークスペース状態を読み込み"""
    try:
        if WORKSPACE_STATE_FILE.exists():
            with open(WORKSPACE_STATE_FILE, "r", encoding="utf-8") as f:
                workspace_data = json.load(f)
            
            # セッション状態に復元
            st.session_state[SESSION_KEYS['todo_list']] = workspace_data.get('todo_list', [])
            st.session_state[SESSION_KEYS['quick_memos']] = workspace_data.get('quick_memos', [])
            
            print("✅ ワークスペース状態を読み込みました")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ ワークスペース状態読み込みエラー: {e}")
        return False

def save_conversation_history(conversation_history):
    """会話履歴を保存"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        
        history_file = DATA_DIR / "conversation_history.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ 会話履歴保存エラー: {e}")
        return False

def load_conversation_history():
    """会話履歴を読み込み"""
    try:
        history_file = DATA_DIR / "conversation_history.json"
        
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return []
        
    except Exception as e:
        print(f"❌ 会話履歴読み込みエラー: {e}")
        return []

def save_evolution_rules(evolution_rules):
    """進化ルールを保存"""
    try:
        custom_data = {
            "evolution_rules": evolution_rules,
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        with open(PERSONALITIES_CUSTOM_FILE, "w", encoding="utf-8") as f:
            json.dump(custom_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ 進化ルール保存エラー: {e}")
        return False

def load_evolution_rules():
    """進化ルールを読み込み"""
    try:
        if PERSONALITIES_CUSTOM_FILE.exists():
            with open(PERSONALITIES_CUSTOM_FILE, "r", encoding="utf-8") as f:
                custom_data = json.load(f)
                return custom_data.get("evolution_rules", [])
        
        return []
        
    except Exception as e:
        print(f"❌ 進化ルール読み込みエラー: {e}")
        return []

def write_agent_diary(entry_type, content):
    """エージェント日記を書き込む"""
    try:
        diary_file = AGENT_DIARY_FILE
        
        # 既存の日記を読み込み
        if diary_file.exists():
            with open(diary_file, "r", encoding="utf-8") as f:
                diary_data = json.load(f)
        else:
            diary_data = {"entries": []}
        
        # 新しいエントリーを作成
        new_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "type": entry_type,
            "content": content
        }
        
        diary_data["entries"].append(new_entry)
        
        # 最新30件のみ保持
        if len(diary_data["entries"]) > 30:
            diary_data["entries"] = diary_data["entries"][-30:]
        
        # 保存
        diary_file.parent.mkdir(exist_ok=True)
        with open(diary_file, "w", encoding="utf-8") as f:
            json.dump(diary_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"日記書き込みエラー: {e}")
        return False

def read_agent_diary():
    """エージェント日記を読み込む"""
    try:
        if AGENT_DIARY_FILE.exists():
            with open(AGENT_DIARY_FILE, "r", encoding="utf-8") as f:
                diary_data = json.load(f)
            return diary_data.get("entries", [])
        
        return []
        
    except Exception as e:
        print(f"日記読み込みエラー: {e}")
        return []

def cleanup_temp_files():
    """一時ファイルやバックアップを整理"""
    try:
        cleanup_log = []
        
        # generated_appsフォルダ内のバックアップファイルを整理
        if GENERATED_APPS_DIR.exists():
            backup_files = list(GENERATED_APPS_DIR.glob("*_backup.py"))
            for backup_file in backup_files:
                # 7日以上前のバックアップは削除
                file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_age.days > 7:
                    backup_file.unlink()
                    cleanup_log.append(f"古いバックアップを削除: {backup_file.name}")
        
        # dataフォルダ内の一時ファイルを整理
        if DATA_DIR.exists():
            temp_files = list(DATA_DIR.glob("temp_*"))
            for temp_file in temp_files:
                # 1日以上前の一時ファイルは削除
                file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(temp_file.stat().st_mtime)
                if file_age.days > 1:
                    temp_file.unlink()
                    cleanup_log.append(f"古い一時ファイルを削除: {temp_file.name}")
        
        if cleanup_log:
            print(f"🧹 セルフメンテナンス完了: {len(cleanup_log)}件のファイルを整理")
        
        return cleanup_log
        
    except Exception as e:
        print(f"クリーンアップエラー: {e}")
        return []

def cleanup_conversation_history():
    """会話履歴をクリーンアップ（最新100件を保持）"""
    try:
        if SESSION_KEYS['conversation_history'] in st.session_state:
            history = st.session_state[SESSION_KEYS['conversation_history']]
            if len(history) > 100:
                st.session_state[SESSION_KEYS['conversation_history']] = history[-100:]
                print("✅ 会話履歴をクリーンアップしました")
        
        return True
        
    except Exception as e:
        print(f"❌ 会話履歴クリーンアップエラー: {e}")
        return False

def archive_old_conversations():
    """古い会話をアーカイブ"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        archive_dir = DATA_DIR / "conversation_archive"
        archive_dir.mkdir(exist_ok=True)
        
        # アーカイブファイルが多すぎる場合は古いものを削除
        archive_files = list(archive_dir.glob("conversation_archive_*.json"))
        if len(archive_files) > 10:
            archive_files.sort(key=lambda x: x.stat().st_mtime)
            for old_file in archive_files[:-10]:
                old_file.unlink()
                print(f"🗑️ 古いアーカイブを削除: {old_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ アーカイブエラー: {e}")
        return False

def get_system_status():
    """システムステータスを取得"""
    try:
        status = {
            "workspace_state_exists": WORKSPACE_STATE_FILE.exists(),
            "conversation_history_exists": (DATA_DIR / "conversation_history.json").exists(),
            "agent_diary_exists": AGENT_DIARY_FILE.exists(),
            "generated_apps_count": len(list(GENERATED_APPS_DIR.glob("*.py"))) if GENERATED_APPS_DIR.exists() else 0,
            "data_dir_exists": DATA_DIR.exists(),
            "custom_personalities_exists": PERSONALITIES_CUSTOM_FILE.exists()
        }
        
        return status
        
    except Exception as e:
        print(f"❌ システムステータス取得エラー: {e}")
        return {}

def export_all_data():
    """すべてのデータをエクスポート"""
    try:
        export_data = {
            "export_timestamp": datetime.datetime.now().isoformat(),
            "workspace_state": {},
            "conversation_history": [],
            "agent_diary": [],
            "evolution_rules": []
        }
        
        # ワークスペース状態
        if WORKSPACE_STATE_FILE.exists():
            with open(WORKSPACE_STATE_FILE, "r", encoding="utf-8") as f:
                export_data["workspace_state"] = json.load(f)
        
        # 会話履歴
        history_file = DATA_DIR / "conversation_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                export_data["conversation_history"] = json.load(f)
        
        # エージェント日記
        if AGENT_DIARY_FILE.exists():
            with open(AGENT_DIARY_FILE, "r", encoding="utf-8") as f:
                diary_data = json.load(f)
                export_data["agent_diary"] = diary_data.get("entries", [])
        
        # 進化ルール
        export_data["evolution_rules"] = load_evolution_rules()
        
        return export_data
        
    except Exception as e:
        print(f"❌ データエクスポートエラー: {e}")
        return None

def import_all_data(import_data):
    """すべてのデータをインポート"""
    try:
        success_count = 0
        
        # ワークスペース状態
        if import_data.get("workspace_state"):
            with open(WORKSPACE_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(import_data["workspace_state"], f, ensure_ascii=False, indent=2)
            success_count += 1
        
        # 会話履歴
        if import_data.get("conversation_history"):
            history_file = DATA_DIR / "conversation_history.json"
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(import_data["conversation_history"], f, ensure_ascii=False, indent=2)
            success_count += 1
        
        # エージェント日記
        if import_data.get("agent_diary"):
            diary_data = {"entries": import_data["agent_diary"]}
            with open(AGENT_DIARY_FILE, "w", encoding="utf-8") as f:
                json.dump(diary_data, f, ensure_ascii=False, indent=2)
            success_count += 1
        
        # 進化ルール
        if import_data.get("evolution_rules"):
            save_evolution_rules(import_data["evolution_rules"])
            success_count += 1
        
        print(f"✅ データインポート完了: {success_count}/4 項目")
        return success_count
        
    except Exception as e:
        print(f"❌ データインポートエラー: {e}")
        return 0
