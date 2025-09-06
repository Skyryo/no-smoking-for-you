# Cloud Run用Dockerfile - Python 3.12ベース
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 非rootユーザーを作成（セキュリティのため）
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Pythonの依存関係をインストール
COPY --chown=app:app requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# アプリケーションコードをコピー
COPY --chown=app:app . ./app/

# PYTHONPATHを設定
ENV PYTHONPATH=/app
ENV PATH="/home/app/.local/bin:${PATH}"

# Cloud Runのポート（デフォルト8080）を公開
EXPOSE 8080

# ヘルスチェック用エンドポイント
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Gunicornを使用してアプリケーションを起動
# Cloud Runの要件に合わせて設定
CMD ["python", "-m", "gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8080", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "1", \
     "--timeout", "0", \
     "--keep-alive", "2", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--preload"]