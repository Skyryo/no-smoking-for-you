# Python 3.11-slimベースイメージを使用 (Cloud Run対応のamd64/linux指定)
FROM --platform=linux/amd64 python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システム依存関係とビルドツールをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ ./app/

# Cloud Runの標準ポート8080を公開
EXPOSE 8080

# 非rootユーザーを作成して実行 (セキュリティ強化)
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# uvicornでアプリケーションを起動
# Cloud RunではPORT環境変数を使用する場合もあるため柔軟に対応
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]