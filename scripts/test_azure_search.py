#!/usr/bin/env python3
"""
Azure AI Search 接続テスト・ヘルスチェックスクリプト
Task 3-1A-1: Azure AI Search接続設定

Usage:
    python scripts/test_azure_search.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# ruff: noqa: E402
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from config import get_settings


class AzureSearchHealthChecker:
    """Azure AI Search ヘルスチェッククラス"""

    def __init__(self):
        self.settings = get_settings()
        self.endpoint = self.settings.azure_search_endpoint
        self.api_key = self.settings.azure_search_api_key
        self.index_name = self.settings.azure_search_index_name

        if not self.endpoint or not self.api_key:
            raise ValueError("Azure Search endpoint and API key are required")

        self.credential = AzureKeyCredential(self.api_key)
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint, credential=self.credential
        )

    async def test_connection(self) -> bool:
        """Azure AI Search 接続テスト"""
        try:
            print("🔍 Azure AI Search 接続テスト開始...")
            print(f"   Endpoint: {self.endpoint}")
            print(f"   Index: {self.index_name}")

            # サービス統計を取得
            service_stats = self.index_client.get_service_statistics()
            print("✅ 接続成功！サービス統計取得完了")
            print(f"   Storage Size: {service_stats.get('storage_size', 'N/A')} bytes")
            print(f"   Document Count: {service_stats.get('document_count', 'N/A')}")

            return True

        except Exception as e:
            print(f"❌ 接続失敗: {str(e)}")
            return False

    async def test_index_operations(self) -> bool:
        """インデックス操作テスト"""
        try:
            print("\n📋 インデックス一覧取得テスト...")

            # インデックス一覧を取得
            indexes = list(self.index_client.list_indexes())
            print(f"✅ インデックス一覧取得成功 ({len(indexes)}個)")

            for index in indexes:
                print(f"   - {index.name}")

            # 対象インデックスの存在確認
            try:
                index = self.index_client.get_index(self.index_name)
                print(f"✅ インデックス '{self.index_name}' 存在確認")
                print(f"   Fields: {len(index.fields)}個")
            except Exception:
                print(f"⚠️  インデックス '{self.index_name}' が存在しません")
                print("   インデックス作成が必要です")

            return True

        except Exception as e:
            print(f"❌ インデックス操作失敗: {str(e)}")
            return False

    async def test_search_query(self) -> bool:
        """基本的な検索クエリテスト"""
        try:
            print(f"\n🔎 基本検索クエリテスト（インデックス: {self.index_name}）...")

            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=self.credential,
            )

            # 空の検索クエリでテスト
            results = search_client.search(search_text="*", top=1)
            result_count = 0
            for result in results:
                result_count += 1

            print("✅ 検索クエリ実行成功")
            print(f"   結果件数: {result_count}")

            return True

        except Exception as e:
            print(f"❌ 検索クエリ失敗: {str(e)}")
            if "index not found" in str(e).lower():
                print(
                    "   インデックスが存在しません。先にインデックスを作成してください"
                )
            return False

    async def run_all_tests(self) -> bool:
        """全テストを実行"""
        print("🚀 Azure AI Search ヘルスチェック開始\n")

        tests = [
            ("接続テスト", self.test_connection),
            ("インデックス操作テスト", self.test_index_operations),
            ("検索クエリテスト", self.test_search_query),
        ]

        all_passed = True
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ {test_name} 実行エラー: {str(e)}")
                all_passed = False

        print(f"\n{'='*50}")
        if all_passed:
            print("🎉 全テスト成功！Azure AI Search は正常に動作しています")
        else:
            print("⚠️  一部テストが失敗しました。設定を確認してください")

        return all_passed


async def main():
    """メイン関数"""
    try:
        checker = AzureSearchHealthChecker()
        success = await checker.run_all_tests()
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"❌ 初期化エラー: {str(e)}")
        print("\n設定確認項目:")
        print("  - AZURE_SEARCH_ENDPOINT が正しく設定されているか")
        print("  - AZURE_SEARCH_API_KEY が正しく設定されているか")
        print("  - Azure Search サービスがアクティブか")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
