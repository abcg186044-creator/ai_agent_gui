#!/usr/bin/env python3
"""
永続化対応モデルプリロードスクリプト
"""

import os
import requests
import time
import json
import logging
import shutil

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersistentModelPreloader:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.models_path = os.getenv('OLLAMA_MODELS_PATH', '/app/data/ollama')
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
    
    def check_model_exists(self, model_name):
        """モデルが既存するか確認"""
        model_path = os.path.join(self.models_path, 'models', model_name)
        return os.path.exists(model_path) and os.path.isdir(model_path)
    
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
    
    def setup_persistent_storage(self):
        """永続化ストレージのセットアップ"""
        logger.info("💾 永続化ストレージをセットアップします...")
        
        # モデル保存ディレクトリの作成
        models_dir = os.path.join(self.models_path, 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        # ChromaDBディレクトリの作成
        chroma_path = os.getenv('CHROMA_DB_PATH', '/app/data/chroma')
        os.makedirs(chroma_path, exist_ok=True)
        
        logger.info("✅ 永続化ストレージのセットアップ完了")
    
    def create_model_cache(self):
        """モデルキャッシュの作成"""
        logger.info("💾 モデルキャッシュを作成します...")
        
        cache_info = {
            "preloaded_models": self.models_to_preload,
            "last_preload": time.time(),
            "version": "1.0"
        }
        
        cache_file = os.path.join(self.models_path, 'preload_cache.json')
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_info, f, indent=2)
            logger.info("✅ モデルキャッシュを作成しました")
        except Exception as e:
            logger.error(f"❌ モデルキャッシュ作成エラー: {e}")
    
    def check_model_cache(self):
        """モデルキャッシュの確認"""
        cache_file = os.path.join(self.models_path, 'preload_cache.json')
        
        if not os.path.exists(cache_file):
            return False
        
        try:
            with open(cache_file, 'r') as f:
                cache_info = json.load(f)
            
            # キャッシュの有効性チェック
            cached_models = cache_info.get('preloaded_models', [])
            if all(model in cached_models for model in self.models_to_preload):
                logger.info("✅ モデルキャッシュが有効です")
                return True
            else:
                logger.info("⚠️ モデルキャッシュが無効です")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ モデルキャッシュ確認エラー: {e}")
            return False
    
    def preload(self):
        """プリロードプロセス全体"""
        logger.info("🚀 永続化対応モデルプリロードを開始します...")
        
        # 1. 永続化ストレージのセットアップ
        self.setup_persistent_storage()
        
        # 2. Ollamaの起動を待つ
        if not self.wait_for_ollama():
            return False
        
        # 3. モデルキャッシュの確認
        if self.check_model_cache():
            logger.info("✅ キャッシュされたモデルが利用可能です")
            return True
        
        # 4. モデルの存在を確認
        models_ok, missing_models = self.check_models()
        
        # 5. 欠けているモデルをダウンロード
        if missing_models:
            if not self.pull_models(missing_models):
                return False
        
        # 6. モデルのウォームアップ
        self.warmup_models()
        
        # 7. キャッシュの作成
        self.create_model_cache()
        
        logger.info("✅ 永続化対応モデルプリロード完了")
        return True

def main():
    """メイン処理"""
    logger.info("🎯 永続化対応 AI Agent System モデルプリロード")
    
    preloader = PersistentModelPreloader()
    
    try:
        success = preloader.preload()
        if success:
            logger.info("🎉 永続化対応プリロード成功 - AIエージェントが利用可能です")
            return 0
        else:
            logger.error("❌ 永続化対応プリロード失敗")
            return 1
            
    except KeyboardInterrupt:
        logger.info("👋 プリロードを中断しました")
        return 0
    except Exception as e:
        logger.error(f"❌ プリロードエラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
