@echo off
chcp 65001 >nul
title AI Agent System - Cleanup

echo.
echo ========================================
echo 🧹 AI Agent System Cleanup
echo ========================================
echo.

REM 確認メッセージ
echo ⚠️ この操作により、既存のコンテナ、イメージ、ボリュームが削除されます
echo 💡 続行するには何かキーを押してください...
pause >nul

REM プロジェクトディレクトリに移動
cd /d "%~dp0"
echo 📁 プロジェクトディレクトリ: %CD%
echo.

REM コンテナの停止と削除
echo 🛑 コンテナを停止・削除中...
docker-compose -f docker-compose.yml down -v >nul 2>&1
docker-compose -f docker-compose-gpu.yml down -v >nul 2>&1
docker-compose -f docker-compose-cpu.yml down -v >nul 2>&1

REM 個別コンテナの停止
echo 🛑 個別コンテナを停止中...
docker stop ai-ollama ai-agent-app ai-voicevox ai-redis >nul 2>&1
docker rm ai-ollama ai-agent-app ai-voicevox ai-redis >nul 2>&1

REM イメージの削除
echo 🖼️ イメージを削除中...
docker rmi ai-agent_gui_ai-app >nul 2>&1
docker rmi ai-agent-test >nul 2>&1
docker image prune -f >nul 2>&1

REM ボリュームの削除
echo 💾 ボリュームを削除中...
docker volume rm ai_agent_gui_ollama_data >nul 2>&1
docker volume rm ai_agent_gui_voicevox_data >nul 2>&1
docker volume rm ai_agent_gui_redis_data >nul 2>&1
docker volume prune -f >nul 2>&1

REM ネットワークの削除
echo 🌐 ネットワークを削除中...
docker network rm ai-agent_gui_ai-network >nul 2>&1
docker network prune -f >nul 2>&1

REM システムのクリーンアップ
echo 🧹 Dockerシステムのクリーンアップ...
docker system prune -a -f >nul 2>&1

REM 一時ファイルの削除
echo 🗑️ 一時ファイルを削除中...
del requirements-docker.txt >nul 2>&1
del docker-compose-cpu.yml >nul 2>&1

REM 結果の表示
echo.
echo ========================================
echo ✅ クリーンアップ完了
echo ========================================
echo.
echo 📊 削除されたリソース:
echo    - 全てのコンテナ
echo    - 全てのイメージ
echo    - 全てのボリューム
echo    - 全てのネットワーク
echo.
echo 💡 次回の起動方法:
echo    GPU版: docker_ultra_minimal_start.bat
echo    CPU版: docker_cpu_start.bat
echo.

pause
