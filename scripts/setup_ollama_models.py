#!/usr/bin/env python3
"""
Ollamaモデルセットアップスクリプト
"""

import os
import requests
import time
import json
import logging
import subprocess

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaModelSetup:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.models_to_pull = [
            'llama3.2',
            'llama3.2-vision'
        ]
    
    def wait_for_ollama(self, timeout=300):
        """Ollamaが起動するのを待つ"""
        logger.info("🔄 Ollamaの起動を待っています...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollamaが起動しました")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info("⏳ Ollama起動中...")
            time.sleep(5)
        
        logger.error("❌ Ollamaの起動タイムアウト")
        return False
    
    def check_models(self):
        """必要なモデルが存在するか確認"""
        logger.info("🔍 モデルの存在を確認します...")
        
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                available_models = [model['name'] for model in data.get('models', [])]
                
                missing_models = []
                for model in self.models_to_pull:
                    if model not in available_models:
                        missing_models.append(model)
                
                if missing_models:
                    logger.info(f"⚠️ 欠けているモデル: {missing_models}")
                    return False, missing_models
                else:
                    logger.info("✅ 全てのモデルが利用可能です")
                    return True, []
            else:
                logger.error(f"❌ モデルリスト取得エラー: {response.status_code}")
                return False, []
        
        except Exception as e:
            logger.error(f"❌ モデル確認エラー: {e}")
            return False, []
    
    def pull_model_background(self, model_name):
        """モデルをバックグラウンドでプル"""
        logger.info(f"📥 モデル {model_name} をバックグラウンドでダウンロード中...")
        
        try:
            # Dockerコンテナ内で実行
            cmd = f"docker exec -d ai-ollama ollama pull {model_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ モデル {model_name} のダウンロードを開始しました")
                return True
            else:
                logger.error(f"❌ モデル {model_name} のダウンロード開始失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ モデル {model_name} のダウンロードエラー: {e}")
            return False
    
    def check_pull_progress(self, model_name):
        """プルの進捗を確認"""
        try:
            cmd = f"docker exec ai-ollama ollama list"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                if model_name in output:
                    logger.info(f"✅ モデル {model_name} が利用可能です")
                    return True
                else:
                    logger.info(f"⏳ モデル {model_name} ダウンロード中...")
                    return False
            else:
                logger.error(f"❌ モデルリスト取得エラー: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ プル進捗確認エラー: {e}")
            return False
    
    def setup_models(self):
        """モデルセットアップ全体"""
        logger.info("🚀 Ollamaモデルセットアップを開始します...")
        
        # 1. Ollamaの起動を待つ
        if not self.wait_for_ollama():
            return False
        
        # 2. モデルの存在を確認
        models_ok, missing_models = self.check_models()
        
        if models_ok:
            logger.info("✅ 全てのモデルが既に利用可能です")
            return True
        
        # 3. 欠けているモデルをバックグラウンドでプル
        logger.info("📥 欠けているモデルをダウンロードします...")
        
        for model in missing_models:
            if self.pull_model_background(model):
                logger.info(f"✅ モデル {model} のダウンロードを開始しました")
            else:
                logger.error(f"❌ モデル {model} のダウンロード開始失敗")
                return False
        
        # 4. プルの完了を待つ
        logger.info("⏳ モデルのダウンロード完了を待っています...")
        
        max_wait_time = 600  # 10分
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            all_ready = True
            
            for model in missing_models:
                if not self.check_pull_progress(model):
                    all_ready = False
                    break
            
            if all_ready:
                logger.info("✅ 全てのモデルのダウンロードが完了しました")
                return True
            
            logger.info("⏳ ダウンロード中...")
            time.sleep(30)
        
        logger.error("❌ モデルのダウンロードタイムアウト")
        return False

def main():
    """メイン処理"""
    logger.info("🎯 Ollamaモデルセットアップ")
    
    setup = OllamaModelSetup()
    
    try:
        success = setup.setup_models()
        if success:
            logger.info("🎉 モデルセットアップ成功")
            return 0
        else:
            logger.error("❌ モデルセットアップ失敗")
            return 1
            
    except KeyboardInterrupt:
        logger.info("👋 セットアップを中断しました")
        return 0
    except Exception as e:
        logger.error(f"❌ セットアップエラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
