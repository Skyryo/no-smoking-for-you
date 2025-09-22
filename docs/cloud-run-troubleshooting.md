# Cloud Run Docker アーキテクチャ問題 - 完全トラブルシューティングガイド

## 🚨 発生したエラー

```
ERROR: (gcloud.run.services.update) Revision 'no-smoking-api-00003-qmm' is not ready and cannot serve traffic.
Cloud Run does not support image 'gcr.io/no-smoking-adk-app/no-smoking-api:latest':
Container manifest type 'application/vnd.oci.image.index.v1+json' must support amd64/linux.
```

## 🔍 根本原因の分析

### 特定された問題

1. **アーキテクチャ不一致**: Apple Silicon (ARM64) 環境でビルドされたイメージ
2. **プラットフォーム未指定**: Dockerfile でアーキテクチャが明示されていない
3. **Cloud Run 要件**: `amd64/linux` アーキテクチャのみサポート

### 診断コマンド

```bash
# 現在のマシンアーキテクチャ確認
uname -m  # -> arm64 (Apple Silicon の場合)

# Docker buildx サポート確認
docker buildx version

# 利用可能なプラットフォーム確認
docker buildx ls
```

## 🛠️ 実施した修正

### 1. Dockerfile 修正

```dockerfile
# 修正前
FROM python:3.11-slim

# 修正後 (プラットフォーム明示指定)
FROM --platform=linux/amd64 python:3.11-slim
```

### 2. セキュリティとパフォーマンス改善

- 非 root ユーザーでの実行
- ビルドツール (`gcc`) の追加
- pip の最新版使用

## ⚡ 即座に解決する手順

### クイック解決 (3 ステップ)

```bash
# 1. backendディレクトリに移動
cd backend

# 2. Cloud Run対応ビルド
docker buildx build --platform linux/amd64 -t gcr.io/no-smoking-adk-app/no-smoking-api:latest .

# 3. プッシュ & デプロイ
docker push gcr.io/no-smoking-adk-app/no-smoking-api:latest
gcloud run services update no-smoking-api --image gcr.io/no-smoking-adk-app/no-smoking-api:latest --region asia-northeast1
```

## 🔧 詳細なトラブルシューティング

### よくある追加エラーと対処法

#### 1. `buildx` コマンドが見つからない

```bash
# Docker Desktop を最新版に更新するか、buildx プラグインを有効化
docker buildx create --use
```

#### 2. GCR 認証エラー

```bash
# 認証を再設定
gcloud auth login
gcloud auth configure-docker
```

#### 3. Cloud Run デプロイタイムアウト

```bash
# タイムアウト時間を延長してリトライ
gcloud run services update no-smoking-api \
  --image gcr.io/no-smoking-adk-app/no-smoking-api:latest \
  --region asia-northeast1 \
  --timeout 900s
```

#### 4. メモリ不足エラー

```bash
# Cloud Run メモリ制限を増加
gcloud run services update no-smoking-api \
  --memory 2Gi \
  --region asia-northeast1
```

### デバッグ用確認コマンド

```bash
# イメージのアーキテクチャ確認
docker buildx imagetools inspect gcr.io/no-smoking-adk-app/no-smoking-api:latest

# Cloud Run サービス詳細確認
gcloud run services describe no-smoking-api --region asia-northeast1

# リアルタイムログ確認
gcloud logging tail "resource.type=cloud_run_revision"
```

## 🎯 予防策

### 1. `.dockerignore` ファイル作成

```gitignore
__pycache__/
*.pyc
.git/
.env
venv/
.pytest_cache/
```

### 2. CI/CD パイプラインでの自動化

```yaml
# GitHub Actions例
- name: Build and push Docker image
  run: |
    docker buildx build \
      --platform linux/amd64 \
      --tag gcr.io/${{ secrets.GCP_PROJECT }}/no-smoking-api:${{ github.sha }} \
      --push \
      backend/
```

### 3. 定期的なテスト

```bash
# ローカルでの動作確認
docker run --rm -p 8080:8080 gcr.io/no-smoking-adk-app/no-smoking-api:latest
```

## ✅ 成功確認チェックリスト

- [ ] `docker buildx build --platform linux/amd64` が成功する
- [ ] `docker push` で GCR にプッシュできる
- [ ] Cloud Run サービスが正常に更新される
- [ ] ヘルスチェックエンドポイントが応答する
- [ ] アプリケーションが期待通りに動作する

## 📚 参考リンク

- [Cloud Run コンテナ要件](https://cloud.google.com/run/docs/container-contract)
- [Docker Buildx マルチプラットフォーム](https://docs.docker.com/build/building/multi-platform/)
- [Google Container Registry 認証](https://cloud.google.com/container-registry/docs/advanced-authentication)

---

**修正完了日**: 2025-01-22  
**対象エラー**: Container manifest amd64/linux 非対応  
**解決方法**: `--platform=linux/amd64` 明示指定
