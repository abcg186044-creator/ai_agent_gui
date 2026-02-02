"""
インポートガードの聖域
このファイルはAIのFILE_MAP（書き換え対象）から完全に除外されています
インポートチェック関数のみを含む純粋なPythonロジック
"""

import re
import os
from pathlib import Path
from typing import Optional, Dict, List

def ensure_streamlit_import(content: str) -> str:
    """
    ファイル保存時にimport streamlit as stが無ければ強制的に先頭に挿入する
    
    Args:
        content (str): 保存しようとするコンテンツ
        
    Returns:
        str: streamlitインポートが保証されたコンテンツ
    """
    try:
        # 既にimport streamlit as stが存在するかチェック
        if re.search(r'^import\s+streamlit\s+as\s+st', content, re.MULTILINE):
            return content
        
        # ファイルの先頭にimport streamlit as stを挿入
        lines = content.split('\n')
        
        # 空行やコメント行をスキップして最初の実行コード行を見つける
        insert_index = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                insert_index = i
                break
        
        # import streamlit as stを挿入
        lines.insert(insert_index, 'import streamlit as st')
        
        return '\n'.join(lines)
        
    except Exception as e:
        # エラー時でも強制的に先頭に追加
        return 'import streamlit as st\n' + content

def clean_duplicate_imports(content: str) -> str:
    """
    重複したimport文をクリーンアップする
    
    Args:
        content (str): クリーンアップするコンテンツ
        
    Returns:
        str: 重複が除去されたコンテンツ
    """
    try:
        lines = content.split('\n')
        seen_imports = set()
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            # import文のみをチェック
            if stripped.startswith('import ') or stripped.startswith('from '):
                if stripped not in seen_imports:
                    seen_imports.add(stripped)
                    cleaned_lines.append(line)
                # 重複はスキップ
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
        
    except Exception as e:
        return content

def validate_and_clean_content(content: str) -> str:
    """
    コンテンツを検証し、クリーンアップする
    
    Args:
        content (str): 検証・クリーンアップするコンテンツ
        
    Returns:
        str: 検証・クリーンアップされたコンテンツ
    """
    # 1. streamlitインポートを保証
    content = ensure_streamlit_import(content)
    
    # 2. 重複インポートをクリーンアップ
    content = clean_duplicate_imports(content)
    
    # 3. 住所確認：インポートパスを検証・修正
    content = validate_import_paths(content)
    
    return content

def check_import_path_exists(import_path: str) -> bool:
    """
    インポートパスが存在するか確認する
    
    Args:
        import_path (str): インポートパス（例: services.state_manager）
        
    Returns:
        bool: パスが存在する場合はTrue
    """
    try:
        # パスを分解
        parts = import_path.split('.')
        
        # プロジェクトルートを取得
        current_dir = Path(__file__).parent.parent
        target_path = current_dir
        
        # 各階層を順番に確認
        for part in parts:
            target_path = target_path / part
            if not target_path.exists():
                return False
                
        # 最後が.pyファイルの場合は確認
        if target_path.suffix == '' and target_path.with_suffix('.py').exists():
            return True
        elif target_path.suffix == '.py':
            return True
            
        return target_path.exists()
        
    except Exception:
        return False

def find_correct_import_path(module_name: str) -> Optional[str]:
    """
    全ディレクトリを検索して正しいインポートパスを見つけ出す
    
    Args:
        module_name (str): モジュール名（例: state_manager）
        
    Returns:
        Optional[str]: 正しいインポートパス、見つからない場合はNone
    """
    try:
        # プロジェクトルートを取得
        current_dir = Path(__file__).parent.parent
        
        # 全ディレクトリを再帰的に検索
        for root_dir in ['core', 'services', 'ui']:
            search_path = current_dir / root_dir
            if search_path.exists():
                for file_path in search_path.rglob(f"{module_name}.py"):
                    # 相対パスを計算
                    relative_path = file_path.relative_to(current_dir)
                    # .py拡張子を除去し、パスをドット区切りに変換
                    import_path = str(relative_path.with_suffix('')).replace(os.sep, '.')
                    return import_path
                    
        return None
        
    except Exception:
        return None

def validate_import_paths(content: str) -> str:
    """
    コンテンツ内のすべてのインポートパスを検証し、修正する
    
    Args:
        content (str): 検証するコンテンツ
        
    Returns:
        str: 修正されたコンテンツ
    """
    try:
        # インポート文を抽出
        import_pattern = r'(from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import|import\s+([a-zA-Z_][a-zA-Z0-9_.]*))'
        
        def replace_import(match):
            full_match = match.group(0)
            import_path = match.group(2) if match.group(2) else match.group(3)
            
            # パスが存在するか確認
            if check_import_path_exists(import_path):
                return full_match
            
            # モジュール名を抽出
            module_name = import_path.split('.')[-1]
            
            # 正しいパスを検索
            correct_path = find_correct_import_path(module_name)
            
            if correct_path:
                # パスを置換
                if match.group(2):  # from ... import
                    return full_match.replace(import_path, correct_path)
                else:  # import ...
                    return full_match.replace(import_path, correct_path)
            
            return full_match
        
        # すべてのインポートを置換
        content = re.sub(import_pattern, replace_import, content)
        
        return content
        
    except Exception:
        return content
