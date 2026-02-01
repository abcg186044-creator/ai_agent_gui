@echo off
chcp 65001 >nul
title Fix Line Endings

echo.
echo ========================================
echo 🔧 改行コード修正ツール
echo ========================================
echo.

REM プロジェクトディレクトリに移動
cd /d "%~dp0"
echo 📁 プロジェクトディレクトリ: %CD%
echo.

REM Pythonスクリプトの実行
echo 🔄 改行コードを修正中...
python scripts/fix_line_endings.py

if errorlevel 1 (
    echo ❌ 改行コードの修正に失敗しました
    pause
    exit /b 1
)

echo.
echo ✅ 改行コードの修正完了
echo.
echo 💡 修正内容:
echo    - Windows形式 (CRLF) → Unix形式 (LF)
echo    - scripts/ ディレクトリ内の全ファイル
echo.
echo 🚀 これでDockerコンテナ内でスクリプトが正常に実行されます
echo.

pause
