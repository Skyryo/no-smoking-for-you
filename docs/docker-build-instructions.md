# Cloud Run 対応 Docker ビルド・デプロイ手順

## 🔧 修正されたポイント

### Dockerfile の改善点

1. **プラットフォーム指定**: `--platform=linux/amd64` で Cloud Run 対応
2. **ビルドツール追加**: `gcc` で Python パッケージコンパイル対応
3. **セキュリティ強化**: 非 root ユーザーでの実行
4. **pip 最適化**: `--upgrade pip` で最新版使用

## 🚀 ビルド・デプロイ手順

### 1. amd64/linux 対応の Docker イメージビルド

```bash
# backendディレクトリに移動
cd backend

# Cloud Run対応のamd64/linuxイメージをビルド
docker buildx build --platform linux/amd64 -t gcr.io/no-smoking-adk-app/no-smoking-api:latest .

# buildxを使用した詳細版（推奨）
docker buildx build \
  --platform linux/amd64 \
  --tag gcr.io/no-smoking-adk-app/no-smoking-api:latest \
  --load \
  .
```

# Docker イメージをビルド（GCR タグ付き）

```bash
docker buildx build --platform linux/amd64 -t gcr.io/no-smoking-adk-app/no-smoking-frontend:latest .

docker push gcr.io/no-smoking-adk-app/no-smoking-frontend:latest
```

### 2. Google Container Registry (GCR) へのプッシュ

```bash
# GCRに認証（初回のみ）
gcloud auth configure-docker

# イメージをGCRにプッシュ
docker push gcr.io/no-smoking-adk-app/no-smoking-api:latest
```

### 3. Cloud Run 再デプロイ

```bash
# Cloud Runサービスを更新
gcloud run services update no-smoking-api \
  --image gcr.io/no-smoking-adk-app/no-smoking-api:latest \
  --region asia-northeast1 \
  --platform managed
```

### 4. デプロイ状況確認

```bash
# サービス状態確認
gcloud run services describe no-smoking-api --region asia-northeast1

# アクセステスト
curl -X GET "https://your-service-url/health"
```

## 🔍 トラブルシューティング

### よくあるエラーと対処法

1. **buildx 未対応エラー**

```bash
# buildxプラグイン有効化
docker buildx create --use
```

2. **プラットフォーム指定エラー**

```bash
# 明示的なbuildx使用
docker buildx build --platform linux/amd64 --tag your-image .
```

3. **GCR 認証エラー**

```bash
# 認証再設定
gcloud auth login
gcloud auth configure-docker
```

### ビルド時のベストプラクティス

- **キャッシュ効率化**: `.dockerignore` で不要ファイル除外
- **レイヤー最適化**: 依存関係とアプリコードを分離
- **セキュリティ**: 非 root ユーザーでの実行
- **マルチアーキテクチャ**: `--platform` 明示指定

## 📊 確認コマンド集

```bash
# イメージの詳細情報確認
docker inspect gcr.io/no-smoking-adk-app/no-smoking-api:latest

# プラットフォーム情報確認
docker buildx imagetools inspect gcr.io/no-smoking-adk-app/no-smoking-api:latest

# Cloud Runログ確認
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```
