@echo off
chcp 65001 >nul
title AI Agent System - 起動中...

echo.
echo ========================================
echo 🤖 AI Agent System 起動スクリプト
echo ========================================
echo.

REM プロジェクトディレクトリに移動
cd /d "%~dp0"
echo 📁 プロジェクトディレクトリ: %CD%
echo.

REM 仮想環境の有無をチェック
if exist ".venv\Scripts\activate.bat" (
    echo 🔄 仮想環境を有効化します...
    call .venv\Scripts\activate.bat
    echo ✅ 仮想環境が有効化されました
    echo.
) else if exist "venv\Scripts\activate.bat" (
    echo 🔄 仮想環境を有効化します...
    call venv\Scripts\activate.bat
    echo ✅ 仮想環境が有効化されました
    echo.
) else (
    echo ⚠️ 仮想環境が見つかりません
    echo 💡 グローバル環境で実行します
    echo.
)

REM Pythonの存在確認
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonが見つかりません
    echo 💡 Pythonをインストールしてください
    echo.
    pause
    exit /b 1
)

REM 必要ライブラリのチェック
echo 📦 必要ライブラリを確認中...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ streamlitが見つかりません
    echo 🔄 streamlitをインストールします...
    pip install streamlit
)

python -c "import sounddevice" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ sounddeviceが見つかりません
    echo 🔄 sounddeviceをインストールします...
    pip install sounddevice
)

python -c "import faster_whisper" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ faster_whisperが見つかりません
    echo 🔄 faster_whisperをインストールします...
    pip install faster_whisper
)

echo ✅ ライブラリチェック完了
echo.

REM Ollamaの状態をチェック
echo 🤖 Ollamaの状態を確認中...
python check_ollama.py
if errorlevel 1 (
    echo.
    echo ❌ Ollamaの準備ができていません
    echo 💡 上記の指示に従ってOllamaを設定してください
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Ollamaの準備が完了しました
echo.

REM マイク選択の確認
echo 🎤️ マイク選択を確認中...
if exist "selected_microphone.txt" (
    echo ✅ 保存されたマイク設定が見つかりました
    set /p SELECTED_MIC=<selected_microphone.txt
    echo 選択されたマイクID: %SELECTED_MIC%
) else (
    echo 📋 マイク選択ツールを起動します...
    python select_microphone.py
    if errorlevel 1 (
        echo.
        echo ❌ マイク選択がキャンセルされました
        echo 💡 手動でマイクを設定してください
        echo.
        pause
        exit /b 1
    )
)

REM マイク設定のチェック
echo 🎤️ マイク設定を確認中...
python check_microphone_setup.py
if errorlevel 1 (
    echo.
    echo ❌ マイクの設定が必要です
    echo 💡 上記の指示に従ってマイクを設定してください
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ マイクの設定が完了しました
echo.

REM アプリケーションの起動
echo 🚀 AI Agent Systemを起動します...
echo.

REM 使用可能なポートを探す
set PORT=8501
:CHECK_PORT
netstat -an | findstr ":%PORT%" >nul
if not errorlevel 1 (
    echo ⚠️ ポート %PORT% は使用中です
    set /a PORT+=1
    if %PORT% gtr 8550 (
        echo ❌ 使用可能なポートが見つかりません
        pause
        exit /b 1
    )
    goto CHECK_PORT
)

echo ✅ ポート %PORT% を使用します
echo 🌐 ブラウザで http://localhost:%PORT% にアクセスしてください
echo.
echo ⏹️  終了するには Ctrl+C を押してください
echo.

REM メインアプリケーションを起動
streamlit run smart_voice_agent.py --server.port %PORT%

REM エラー時の処理
if errorlevel 1 (
    echo.
    echo ❌ アプリケーションの起動に失敗しました
    echo 💡 エラー内容を確認してください
    echo.
    pause
)

echo.
echo 🛑 AI Agent Systemを終了します
pause
