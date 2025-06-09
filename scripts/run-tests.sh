#!/bin/bash

set -e

echo "🧪 Starting QRAI Test Suite"
echo "==============================="

# テストコンテナを停止・削除
echo "Cleaning up existing test containers..."
docker-compose -f docker-compose.test.yml down --volumes --remove-orphans

# テストコンテナをビルド・起動
echo "Building and starting test containers..."
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# テスト終了後のクリーンアップ
echo "Cleaning up test containers..."
docker-compose -f docker-compose.test.yml down --volumes

echo "🎉 Test execution completed!"
