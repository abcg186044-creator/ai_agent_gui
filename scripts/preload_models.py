#!/usr/bin/env python3
"""
モデルプリロードスクリプト - 起動時にモデルをVRAMに展開
"""

import requests
import time
import json
import logging
import os

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPreloader:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.models_to_preload = [
            'llama3.2',
            'llama3.2-vision'
        ]
        self.warmup_prompts = [
            "こんにちは",
            "Hello, how are you?",
            "今日の天気は？",
            "What is AI?"
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
                for model in self.models_to_preload:
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
    
    def pull_models(self, missing_models):
        """欠けているモデルをプル"""
        for model in missing_models:
            logger.info(f"📥 モデル {model} をダウンロード中...")
            try:
                response = requests.post(
                    f"{self.ollama_host}/api/pull",
                    json={"name": model},
                    timeout=600  # 10分タイムアウト
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ モデル {model} のダウンロード完了")
                else:
                    logger.error(f"❌ モデル {model} のダウンロード失敗: {response.status_code}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ モデル {model} のダウンロードエラー: {e}")
                return False
        
        return True
    
    def warmup_models(self):
        """モデルをウォームアップ"""
        logger.info("🔥 モデルのウォームアップを開始します...")
        
        for model in self.models_to_preload:
            logger.info(f"🔥 モデル {model} をウォームアップ中...")
            
            for prompt in self.warmup_prompts:
                try:
                    response = requests.post(
                        f"{self.ollama_host}/api/generate",
                        json={
                            "model": model,
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"✅ {model}: {prompt[:30]}... -> {result.get('response', '')[:50]}...")
                    else:
                        logger.warning(f"⚠️ {model}: ウォームアップ失敗")
                        
                except Exception as e:
                    logger.warning(f"⚠️ {model}: ウォームアップエラー: {e}")
                
                time.sleep(1)  # モデル間のクールダウン
    
    def preload(self):
        """プリロードプロセス全体"""
        logger.info("🚀 モデルプリロードを開始します...")
        
        # 1. Ollamaの起動を待つ
        if not self.wait_for_ollama():
            return False
        
        # 2. モデルの存在を確認
        models_ok, missing_models = self.check_models()
        
        # 3. 欠けているモデルをダウンロード
        if missing_models:
            if not self.pull_models(missing_models):
                return False
        
        # 4. モデルのウォームアップ
        self.warmup_models()
        
        logger.info("✅ モデルプリロード完了")
        return True

def main():
    """メイン処理"""
    logger.info("🎯 AI Agent System モデルプリロード")
    
    preloader = ModelPreloader()
    
    try:
        success = preloader.preload()
        if success:
            logger.info("🎉 プリロード成功 - AIエージェントが利用可能です")
            return 0
        else:
            logger.error("❌ プリロード失敗")
            return 1
            
    except KeyboardInterrupt:
        logger.info("👋 プリロードを中断しました")
        return 0
    except Exception as e:
        logger.error(f"❌ プリロードエラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
