#!/bin/bash

# Docker テストスクリプト - Cloud Run環境を再現
set -e

echo "🐳 Cloud Run環境をローカルで再現中..."

# Dockerイメージをビルド
echo "📦 Dockerイメージをビルド中..."
docker build -t no-smoking-adk-backend .

# コンテナを起動
echo "🚀 コンテナを起動中..."
docker run -d --name no-smoking-test -p 8080:8080 no-smoking-adk-backend

# コンテナが起動するまで待機
echo "⏳ コンテナ起動を待機中..."
sleep 10

# ヘルスチェック
echo "🩺 ヘルスチェック実行中..."
if curl -f http://localhost:8080/health; then
    echo "✅ ヘルスチェック成功"
else
    echo "❌ ヘルスチェック失敗"
    docker logs no-smoking-test
    docker stop no-smoking-test
    docker rm no-smoking-test
    exit 1
fi

# APIテスト
echo "🧪 API動作テスト中..."
if curl -f http://localhost:8080/; then
    echo "✅ API動作確認成功"
else
    echo "❌ API動作確認失敗"
    docker logs no-smoking-test
    docker stop no-smoking-test
    docker rm no-smoking-test
    exit 1
fi

echo "🎉 すべてのテストが成功しました！"
echo "🌐 アプリケーションは http://localhost:8080 で利用可能です"
echo ""
echo "コンテナを停止するには："
echo "  docker stop no-smoking-test"
echo "  docker rm no-smoking-test"