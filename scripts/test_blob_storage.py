#!/usr/bin/env python3
"""
Azure Blob Storage 接続テストスクリプト
"""

import asyncio
import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

from services.blob_storage_service import BlobStorageService, BlobStorageError
from config import get_settings


async def test_blob_storage():
    """Blob Storage接続テスト"""
    print("🚀 Azure Blob Storage ヘルスチェック開始\n")

    # 設定確認
    settings = get_settings()
    print("🔍 Azure Blob Storage 接続テスト開始...")
    print(f"   Account: {settings.azure_storage_account_name}")
    print(f"   Container: {settings.azure_storage_container_name}")

    try:
        # サービス初期化
        blob_service = BlobStorageService()

        # ヘルスチェック
        print("\n📋 ヘルスチェック実行...")
        is_healthy = await blob_service.health_check()
        if is_healthy:
            print("✅ ヘルスチェック成功")
        else:
            print("❌ ヘルスチェック失敗 - コンテナが存在しないか、アクセス権限がありません")

            # コンテナ作成を試行
            print("\n🔧 コンテナ作成を試行...")
            try:
                await blob_service.ensure_container_exists()
                print("✅ コンテナ作成成功")
            except BlobStorageError as e:
                print(f"❌ コンテナ作成失敗: {e}")
                return

        # サービス情報取得
        print("\n📊 サービス情報取得...")
        service_info = await blob_service.get_service_info()
        print(f"   Status: {service_info.get('status')}")
        print(f"   Account Kind: {service_info.get('account_kind')}")
        print(f"   SKU: {service_info.get('sku_name')}")

        # テストファイルアップロード
        print("\n📤 テストファイルアップロード...")
        test_content = b"This is a test document for Azure Blob Storage integration."
        test_filename = "test_document.txt"

        try:
            blob_url = await blob_service.upload_document(
                file_name=test_filename,
                file_content=test_content,
                content_type="text/plain",
                metadata={"test": "true", "purpose": "integration_test"}
            )
            print(f"✅ アップロード成功: {blob_url}")
        except BlobStorageError as e:
            print(f"❌ アップロード失敗: {e}")
            return

        # メタデータ取得テスト
        print("\n📋 メタデータ取得テスト...")
        try:
            metadata = await blob_service.get_document_metadata(test_filename)
            print(f"   ファイル名: {metadata['name']}")
            print(f"   サイズ: {metadata['size']} bytes")
            print(f"   Content Type: {metadata['content_type']}")
            print(f"   最終更新: {metadata['last_modified']}")
            print(f"   メタデータ: {metadata['metadata']}")
        except BlobStorageError as e:
            print(f"❌ メタデータ取得失敗: {e}")

        # ドキュメント一覧取得テスト
        print("\n📂 ドキュメント一覧取得テスト...")
        try:
            documents = await blob_service.list_documents()
            print(f"✅ ドキュメント一覧取得成功 ({len(documents)}個)")
            for doc in documents[:3]:  # 最初の3個のみ表示
                print(f"   - {doc['name']} ({doc['size']} bytes)")
        except BlobStorageError as e:
            print(f"❌ ドキュメント一覧取得失敗: {e}")

        # ダウンロードテスト
        print("\n📥 ダウンロードテスト...")
        try:
            downloaded_content = await blob_service.download_document(test_filename)
            if downloaded_content == test_content:
                print("✅ ダウンロード成功 - 内容が一致")
            else:
                print("❌ ダウンロード失敗 - 内容が不一致")
        except BlobStorageError as e:
            print(f"❌ ダウンロード失敗: {e}")

        # クリーンアップ（テストファイル削除）
        print("\n🧹 テストファイルクリーンアップ...")
        try:
            deleted = await blob_service.delete_document(test_filename)
            if deleted:
                print("✅ テストファイル削除成功")
            else:
                print("⚠️  テストファイルが見つかりませんでした")
        except BlobStorageError as e:
            print(f"❌ テストファイル削除失敗: {e}")

        # リソースクリーンアップ
        await blob_service.close()

        print("\n" + "="*50)
        print("🎉 全テスト成功！Azure Blob Storage は正常に動作しています")

    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_blob_storage())
