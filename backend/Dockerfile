# Python 3.11-slimベースイメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ ./app/

# Cloud Runの標準ポート8080を公開
EXPOSE 8080

# uvicornでアプリケーションを起動
# Cloud Runは環境変数PORTを提供するため、それを使用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]