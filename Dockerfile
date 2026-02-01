# AI Agent System Dockerfile
FROM python:3.10-slim

# 基本パッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    portaudio19-dev \
    python3-dev \
    ffmpeg \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Pythonパッケージの要件ファイル
ARG REQUIREMENTS_FILE=requirements.txt
COPY ${REQUIREMENTS_FILE} requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# アセットディレクトリの作成
RUN mkdir -p /app/assets/vrm
RUN mkdir -p /app/models
RUN mkdir -p /app/logs

# VRMモデルの自動配置スクリプト
COPY scripts/setup_vrm.sh /app/scripts/
RUN chmod +x /app/scripts/setup_vrm.sh

# モデルプリロードスクリプト
COPY scripts/preload_models.py /app/scripts/
RUN chmod +x /app/scripts/preload_models.py

# 起動スクリプト
COPY scripts/start_services.sh /app/scripts/
RUN chmod +x /app/scripts/start_services.sh

# 環境変数の設定
ENV PYTHONPATH=/app
ENV OLLAMA_HOST=http://ollama:11434
ENV VOICEVOX_HOST=http://voicevox:50021
ENV REDIS_HOST=redis

# ヘルスチェック用
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501 || exit 1

# ポートの公開
EXPOSE 8501

# サービス起動
CMD ["/app/scripts/start_services.sh"]
