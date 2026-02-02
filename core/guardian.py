"""
インポートガードの聖域
このファイルはAIのFILE_MAP（書き換え対象）から完全に除外されています
インポートチェック関数のみを含む純粋なPythonロジック
"""

import re
from typing import Optional

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
    
    return content
