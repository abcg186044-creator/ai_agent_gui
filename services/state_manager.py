"""
ステートマネージャーモジュール
会話履歴、TODO、進化ルールのJSON保存・読み込みを管理
"""

import json
import os
import datetime
from pathlib import Path
from core.constants import *
from core.file_map import file_resolver, get_relevant_files, should_load_file
from services.import_validator import import_error_detector, auto_import_fixer

# ファイルキャッシュ（パフォーマンス向上）
_file_cache = {}

def safe_function_call(module_path: str, function_name: str, *args, **kwargs):
    """安全な関数呼び出し with インポート不足検知"""
    try:
        # モジュールを動的にインポート
        module = __import__(module_path, fromlist=[function_name])
        func = getattr(module, function_name)
        return func(*args, **kwargs)
        
    except AttributeError as e:
        # AttributeErrorを検知して自動修正を試みる
        error_info = import_error_detector.analyze_error(str(e))
        
        if error_info['error_type'] != 'unknown':
            print(f"🔍 インポート不足を検知: {error_info}")
            
            # 呼び出し元ファイルを特定して自動修正
            caller_file = _get_caller_file()
            if caller_file:
                print("🔧 インポートを自動修正中...")
                fix_result = auto_import_fixer.fix_import_error(error_info, caller_file)
                
                if fix_result['success']:
                    print(f"✅ {fix_result['message']}")
                    
                    # 修正を検証
                    validation = auto_import_fixer.validate_import_fix(caller_file)
                    if validation['success']:
                        print("✅ インポート修正を検証しました")
                        # 再度関数呼び出しを試行
                        module = __import__(module_path, fromlist=[function_name])
                        func = getattr(module, function_name)
                        return func(*args, **kwargs)
                    else:
                        print(f"❌ 検証失敗: {validation['error']}")
                else:
                    print(f"❌ 自動修正失敗: {fix_result['error']}")
        
        raise e
        
    except ImportError as e:
        # ImportErrorを検知して自動修正を試みる
        error_info = import_error_detector.analyze_error(str(e))
        
        if error_info['error_type'] != 'unknown':
            print(f"🔍 ImportErrorを検知: {error_info}")
            
            caller_file = _get_caller_file()
            if caller_file:
                print("🔧 ImportErrorを自動修正中...")
                fix_result = auto_import_fixer.fix_import_error(error_info, caller_file)
                
                if fix_result['success']:
                    print(f"✅ {fix_result['message']}")
                    # 再度インポートを試行
                    module = __import__(module_path, fromlist=[function_name])
                    func = getattr(module, function_name)
                    return func(*args, **kwargs)
        
        raise e
    
    except Exception as e:
        print(f"❌ 関数呼び出しエラー: {str(e)}")
        raise e

def _get_caller_file():
    """呼び出し元ファイルを取得"""
    import inspect
    frame = inspect.currentframe()
    try:
        # 呼び出し元を遡ってファイルを特定
        for _ in range(3):  # 3階層遡る
            frame = frame.f_back
            if frame and frame.f_code.co_filename:
                return frame.f_code.co_filename
    finally:
        del frame
    return None

def load_file_with_cache(file_path: str, user_request: str = None) -> str:
    """キャッシュ付きファイル読み込み"""
    # ユーザー要求に基づいて読み込み必要性をチェック
    if user_request and not should_load_file(file_path, user_request):
        return ""
    
    # キャッシュチェック
    if file_path in _file_cache:
        cache_time, content = _file_cache[file_path]
        file_mtime = Path(file_path).stat().st_mtime if Path(file_path).exists() else 0
        
        # ファイルが変更されていなければキャッシュを返す
        if cache_time >= file_mtime:
            return content
    
    # ファイル読み込み
    try:
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # キャッシュに保存
            file_mtime = Path(file_path).stat().st_mtime
            _file_cache[file_path] = (file_mtime, content)
            
            return content
        else:
            return ""
    except Exception as e:
        print(f"ファイル読み込みエラー {file_path}: {e}")
        return ""

def clear_file_cache():
    """ファイルキャッシュをクリア"""
    global _file_cache
    _file_cache.clear()

def resolve_target_file(user_request: str) -> Optional[str]:
    """ユーザー要求から修正対象ファイルを特定"""
    try:
        from ..core.file_map import resolve_target_file as file_map_resolver
        return file_map_resolver(user_request)
    except Exception as e:
        print(f"ターゲットファイル解決エラー: {e}")
        return None

def get_optimized_file_list(user_request: str) -> list:
    """ユーザー要求に基づいて最適化されたファイルリストを取得"""
    all_files = list(file_resolver.file_map.keys())
    relevant_files = get_relevant_files(user_request)
    
    # 関連ファイルを優先し、残りを優先度順にソート
    prioritized_files = []
    
    # 関連ファイルを先頭に追加
    for file_path in relevant_files:
        if file_path in all_files:
            prioritized_files.append(file_path)
    
    # 残りのファイルを優先度順に追加
    remaining_files = [f for f in all_files if f not in prioritized_files]
    remaining_files = file_resolver.optimize_loading_order(remaining_files)
    prioritized_files.extend(remaining_files)
    
    return prioritized_files

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
