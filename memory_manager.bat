@echo off
chcp 932 >nul
title AI Agent Memory Manager

:MENU
cls
echo.
echo ========================================
echo 🧠 AI Agent Memory Manager
echo ========================================
echo.
echo 1. 記憶ボリューム一覧
echo 2. 記憶バックアップ
echo 3. 記憶リストア
echo 4. 記憶内容確認
echo 5. 記憶クリア
echo 6. システムログ確認
echo 7. コンテナ管理
echo 0. 終了
echo.
set /p choice="選択してください (0-7): "

if "%choice%"=="1" goto LIST_VOLUMES
if "%choice%"=="2" goto BACKUP_MEMORY
if "%choice%"=="3" goto RESTORE_MEMORY
if "%choice%"=="4" goto CHECK_MEMORY
if "%choice%"=="5" goto CLEAR_MEMORY
if "%choice%"=="6" goto VIEW_LOGS
if "%choice%"=="7" goto CONTAINER_MANAGE
if "%choice%"=="0" goto END
goto MENU

:LIST_VOLUMES
echo.
echo 📊 記憶ボリューム一覧:
echo ========================================
docker volume ls | findstr ai_
echo.
pause
goto MENU

:BACKUP_MEMORY
echo.
echo 💾 記憶バックアップ
echo ========================================
echo バックアップを作成しています...
docker run --rm -v ai_chroma_data:/data -v "%CD%":/backup alpine tar czf /backup/memory_backup_%date:~0,4%%date:~5,2%%date:~8,2%.tar.gz -C /data .
if errorlevel 1 (
    echo ❌ バックアップに失敗しました
) else (
    echo ✅ バックアップが完了しました
    echo ファイル: memory_backup_%date:~0,4%%date:~5,2%%date:~8,2%.tar.gz
)
echo.
pause
goto MENU

:RESTORE_MEMORY
echo.
echo 🔄 記憶リストア
echo ========================================
echo 利用可能なバックアップ:
dir /b memory_backup_*.tar.gz 2>nul
if errorlevel 1 (
    echo ❌ バックアップファイルが見つかりません
    pause
    goto MENU
)
echo.
set /p backup_file="リストアするバックアップファイル名: "
if not exist "%backup_file%" (
    echo ❌ ファイルが見つかりません: %backup_file%
    pause
    goto MENU
)
echo リストア中...
docker run --rm -v ai_chroma_data:/data -v "%CD%":/backup alpine tar xzf /backup/%backup_file% -C /data
if errorlevel 1 (
    echo ❌ リストアに失敗しました
) else (
    echo ✅ リストアが完了しました
)
echo.
pause
goto MENU

:CHECK_MEMORY
echo.
echo 🔍 記憶内容確認
echo ========================================
echo ボリュームの詳細情報:
docker volume inspect ai_chroma_data
echo.
echo 記憶ファイル一覧:
docker run --rm -v ai_chroma_data:/data alpine ls -la /data 2>nul || echo 記憶データがありません
echo.
pause
goto MENU

:CLEAR_MEMORY
echo.
echo 🗑️ 記憶クリア
echo ========================================
echo ⚠️ 警告: すべての記憶データが削除されます
echo 続行しますか？ (Y/N)
set /p confirm=
if /i not "%confirm%"=="Y" goto MENU
echo 記憶をクリア中...
docker volume rm ai_chroma_data 2>nul
docker volume create ai_chroma_data
docker volume rm ai_conversation_history 2>nul
docker volume create ai_conversation_history
docker volume rm ai_user_settings 2>nul
docker volume create ai_user_settings
docker volume rm ai_logs 2>nul
docker volume create ai_logs
echo ✅ 記憶をクリアしました
echo.
pause
goto MENU

:VIEW_LOGS
echo.
echo 📋 システムログ確認
echo ========================================
echo 最新のログを表示中...
docker-compose -f docker-compose.memory.yml logs --tail=50
echo.
pause
goto MENU

:CONTAINER_MANAGE
echo.
echo 🐳 コンテナ管理
echo ========================================
echo 1. コンテナ状態確認
echo 2. コンテナ再起動
echo 3. コンテナ停止
echo 4. コンテナ起動
echo 0. メニューに戻る
echo.
set /p container_choice="選択してください (0-4): "

if "%container_choice%"=="1" (
    echo コンテナ状態:
    docker-compose -f docker-compose.memory.yml ps
)
if "%container_choice%"=="2" (
    echo コンテナを再起動中...
    docker-compose -f docker-compose.memory.yml restart
)
if "%container_choice%"=="3" (
    echo コンテナを停止中...
    docker-compose -f docker-compose.memory.yml down
)
if "%container_choice%"=="4" (
    echo コンテナを起動中...
    docker-compose -f docker-compose.memory.yml up -d
)
echo.
pause
goto MENU

:END
echo.
echo 🎉 Memory Manager を終了します
echo.
pause
