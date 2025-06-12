#!/usr/bin/env python3
"""
Azure AI Search インデックス作成スクリプト
Task 3-1A-3: 検索インデックス設計・作成

RAGアーキテクチャに基づいたインデックススキーマ:
- ドキュメント管理（id, title, content, metadata）
- チャンク分割対応（chunk_id, chunk_index）
- ベクトル検索対応（content_vector）
- 日本語検索最適化（ja.microsoft analyzer）
- 引用・関連性スコア対応
"""

import asyncio
import sys
import os
from typing import Dict, Any, List, Optional

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ComplexField,
    VectorSearch,
    VectorSearchProfile,
    VectorSearchAlgorithmConfiguration,
    HnswAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    LexicalAnalyzerName,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceExistsError, HttpResponseError

from config import get_settings


class SearchIndexManager:
    """Azure AI Search インデックス管理クラス"""

    def __init__(self):
        """初期化"""
        self.settings = get_settings()
        self.index_client: Optional[SearchIndexClient] = None
        self._initialize_client()

    def _initialize_client(self):
        """Azure AI Search Index Clientを初期化"""
        try:
            if not self.settings.azure_search_endpoint:
                raise ValueError("Azure Search endpoint not configured")

            if not self.settings.azure_search_api_key:
                raise ValueError("Azure Search API key not configured")

            credential = AzureKeyCredential(self.settings.azure_search_api_key)
            self.index_client = SearchIndexClient(
                endpoint=self.settings.azure_search_endpoint, credential=credential
            )

            print(f"✅ Azure AI Search Index Client initialized")
            print(f"   Endpoint: {self.settings.azure_search_endpoint}")
            print(f"   Index Name: {self.settings.azure_search_index_name}")

        except Exception as e:
            print(f"❌ Failed to initialize Azure AI Search Index Client: {e}")
            raise

    def create_index_schema(self) -> SearchIndex:
        """
        RAG最適化インデックススキーマを作成

        スキーマ設計:
        - ドキュメント識別: id (key), document_id, chunk_id
        - コンテンツ: title, content, summary
        - メタデータ: file_name, file_type, file_size, created_at, updated_at
        - チャンク情報: chunk_index, chunk_count, chunk_overlap
        - ベクトル検索: content_vector (1536次元, text-embedding-ada-002)
        - 引用情報: source_url, page_number
        """

        # フィールド定義
        fields = [
            # === 主キー・識別子 ===
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
                sortable=True,
                facetable=False,
            ),
            SimpleField(
                name="document_id",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            SimpleField(
                name="chunk_id",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                facetable=False,
            ),

            # === コンテンツフィールド ===
            SearchableField(
                name="title",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=True,
                sortable=True,
                facetable=False,
                analyzer_name=LexicalAnalyzerName.JA_MICROSOFT,  # 日本語最適化
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                analyzer_name=LexicalAnalyzerName.JA_MICROSOFT,  # 日本語最適化
            ),
            SearchableField(
                name="summary",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                analyzer_name=LexicalAnalyzerName.JA_MICROSOFT,
            ),

            # === ファイルメタデータ ===
            SimpleField(
                name="file_name",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            SimpleField(
                name="file_type",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=False,
                facetable=True,
            ),
            SimpleField(
                name="file_size",
                type=SearchFieldDataType.Int64,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            SimpleField(
                name="created_at",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            SimpleField(
                name="updated_at",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
                facetable=False,
            ),

            # === チャンク情報 ===
            SimpleField(
                name="chunk_index",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=True,
                facetable=False,
            ),
            SimpleField(
                name="chunk_count",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=False,
                facetable=True,
            ),
            SimpleField(
                name="chunk_overlap",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=False,
                facetable=False,
            ),

            # === 引用・ソース情報 ===
            SimpleField(
                name="source_url",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=False,
                facetable=False,
            ),
            SimpleField(
                name="page_number",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=True,
                facetable=False,
            ),

            # === カテゴリ・タグ ===
            SimpleField(
                name="category",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=False,
                facetable=True,
            ),
            SimpleField(
                name="tags",
                type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                filterable=True,
                sortable=False,
                facetable=True,
            ),

            # === ベクトル検索フィールド ===
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                vector_search_dimensions=1536,  # text-embedding-ada-002の次元数
                vector_search_profile_name="default-vector-profile",
            ),
        ]

        # ベクトル検索設定
        vector_search = VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="default-vector-profile",
                    algorithm_configuration_name="default-hnsw-config",
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="default-hnsw-config",
                    kind=VectorSearchAlgorithmKind.HNSW,
                    parameters={
                        "m": 4,  # 接続数（デフォルト4、高精度なら16）
                        "efConstruction": 400,  # 構築時探索数（デフォルト400）
                        "efSearch": 500,  # 検索時探索数（デフォルト500）
                        "metric": VectorSearchAlgorithmMetric.COSINE,  # コサイン類似度
                    },
                )
            ],
        )

        # インデックス作成
        index = SearchIndex(
            name=self.settings.azure_search_index_name,
            fields=fields,
            vector_search=vector_search,
        )

        return index

    def create_index(self, force_recreate: bool = False) -> bool:
        """
        インデックスを作成

        Args:
            force_recreate: 既存インデックスを削除して再作成するか

        Returns:
            bool: 作成成功かどうか
        """
        try:
            if not self.index_client:
                raise ValueError("Index client not initialized")

            index_name = self.settings.azure_search_index_name

            # 既存インデックス確認
            try:
                existing_index = self.index_client.get_index(index_name)
                print(f"📋 既存インデックス '{index_name}' が見つかりました")

                if force_recreate:
                    print(f"🗑️  既存インデックス '{index_name}' を削除します...")
                    self.index_client.delete_index(index_name)
                    print(f"✅ インデックス削除完了")
                else:
                    print(f"⚠️  既存インデックスが存在します。再作成する場合は --force オプションを使用してください")
                    return False

            except Exception:
                print(f"📝 新規インデックス '{index_name}' を作成します")

            # インデックススキーマ作成
            print(f"🔧 インデックススキーマを設計中...")
            index = self.create_index_schema()

            # インデックス作成実行
            print(f"🚀 インデックス '{index_name}' を作成中...")
            result = self.index_client.create_index(index)

            print(f"✅ インデックス作成成功!")
            print(f"   インデックス名: {result.name}")
            print(f"   フィールド数: {len(result.fields)}")
            print(f"   ベクトル検索: {'有効' if result.vector_search else '無効'}")

            return True

        except ResourceExistsError:
            print(f"⚠️  インデックス '{index_name}' は既に存在します")
            return False
        except Exception as e:
            print(f"❌ インデックス作成失敗: {e}")
            return False

    def get_index_info(self) -> Dict[str, Any]:
        """インデックス情報を取得"""
        try:
            if not self.index_client:
                raise ValueError("Index client not initialized")

            index_name = self.settings.azure_search_index_name
            index = self.index_client.get_index(index_name)

            # フィールド情報を整理
            fields_info = []
            for field in index.fields:
                field_info = {
                    "name": field.name,
                    "type": str(field.type),
                    "key": getattr(field, "key", False),
                    "searchable": getattr(field, "searchable", False),
                    "filterable": getattr(field, "filterable", False),
                    "sortable": getattr(field, "sortable", False),
                    "facetable": getattr(field, "facetable", False),
                    "retrievable": getattr(field, "retrievable", True),
                }

                # ベクトルフィールドの場合
                if hasattr(field, "vector_search_dimensions"):
                    field_info["vector_dimensions"] = field.vector_search_dimensions
                    field_info["vector_profile"] = getattr(field, "vector_search_profile_name", None)

                # アナライザー情報
                if hasattr(field, "analyzer_name"):
                    field_info["analyzer"] = str(field.analyzer_name)

                fields_info.append(field_info)

            return {
                "name": index.name,
                "fields_count": len(index.fields),
                "fields": fields_info,
                "vector_search_enabled": index.vector_search is not None,
                "vector_profiles": [p.name for p in index.vector_search.profiles] if index.vector_search else [],
            }

        except Exception as e:
            print(f"❌ インデックス情報取得失敗: {e}")
            return {}

    def delete_index(self) -> bool:
        """インデックスを削除"""
        try:
            if not self.index_client:
                raise ValueError("Index client not initialized")

            index_name = self.settings.azure_search_index_name
            self.index_client.delete_index(index_name)
            print(f"✅ インデックス '{index_name}' を削除しました")
            return True

        except Exception as e:
            print(f"❌ インデックス削除失敗: {e}")
            return False

    def print_schema_summary(self):
        """スキーマ設計の概要を表示"""
        print("\n" + "=" * 60)
        print("🏗️  Azure AI Search インデックススキーマ設計")
        print("=" * 60)

        print("\n📋 フィールド構成:")
        print("  🔑 主キー・識別子:")
        print("    - id (key): ユニークID")
        print("    - document_id: ドキュメント識別子")
        print("    - chunk_id: チャンク識別子")

        print("\n  📝 コンテンツ:")
        print("    - title: タイトル（日本語検索最適化）")
        print("    - content: 本文（日本語検索最適化）")
        print("    - summary: 要約")

        print("\n  📁 ファイルメタデータ:")
        print("    - file_name, file_type, file_size")
        print("    - created_at, updated_at")

        print("\n  🧩 チャンク情報:")
        print("    - chunk_index, chunk_count, chunk_overlap")

        print("\n  🔗 引用・ソース:")
        print("    - source_url, page_number")
        print("    - category, tags")

        print("\n  🎯 ベクトル検索:")
        print("    - content_vector (1536次元)")
        print("    - HNSW アルゴリズム（コサイン類似度）")

        print("\n🌐 日本語対応:")
        print("  - アナライザー: ja.microsoft")
        print("  - 検索フィールド: title, content, summary")

        print("\n🔍 検索機能:")
        print("  - テキスト検索（キーワード）")
        print("  - ベクトル検索（セマンティック）")
        print("  - ハイブリッド検索（テキスト + ベクトル）")
        print("  - フィルタリング（ファイル種別、日付、カテゴリ）")
        print("=" * 60)


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="Azure AI Search インデックス管理")
    parser.add_argument("--create", action="store_true", help="インデックスを作成")
    parser.add_argument("--force", action="store_true", help="既存インデックスを削除して再作成")
    parser.add_argument("--info", action="store_true", help="インデックス情報を表示")
    parser.add_argument("--delete", action="store_true", help="インデックスを削除")
    parser.add_argument("--schema", action="store_true", help="スキーマ設計概要を表示")

    args = parser.parse_args()

    # 引数なしの場合はヘルプを表示
    if not any([args.create, args.info, args.delete, args.schema]):
        parser.print_help()
        return

    try:
        manager = SearchIndexManager()

        if args.schema:
            manager.print_schema_summary()
            return

        if args.create:
            success = manager.create_index(force_recreate=args.force)
            if success:
                print(f"\n🎉 インデックス作成完了!")
                # 作成後に情報表示
                info = manager.get_index_info()
                if info:
                    print(f"\n📊 インデックス情報:")
                    print(f"  名前: {info['name']}")
                    print(f"  フィールド数: {info['fields_count']}")
                    print(f"  ベクトル検索: {'有効' if info['vector_search_enabled'] else '無効'}")
            else:
                print(f"\n❌ インデックス作成に失敗しました")
                return 1

        if args.info:
            info = manager.get_index_info()
            if info:
                print(f"\n📊 インデックス情報:")
                print(f"  名前: {info['name']}")
                print(f"  フィールド数: {info['fields_count']}")
                print(f"  ベクトル検索: {'有効' if info['vector_search_enabled'] else '無効'}")

                if info['vector_search_enabled']:
                    print(f"  ベクトルプロファイル: {', '.join(info['vector_profiles'])}")

                print(f"\n📋 フィールド一覧:")
                for field in info['fields'][:10]:  # 最初の10フィールドのみ表示
                    flags = []
                    if field.get('key'): flags.append('KEY')
                    if field.get('searchable'): flags.append('SEARCH')
                    if field.get('filterable'): flags.append('FILTER')
                    if field.get('vector_dimensions'): flags.append(f"VECTOR({field['vector_dimensions']})")

                    flag_str = f" [{', '.join(flags)}]" if flags else ""
                    print(f"    - {field['name']} ({field['type']}){flag_str}")

                if len(info['fields']) > 10:
                    print(f"    ... 他 {len(info['fields']) - 10} フィールド")
            else:
                print(f"\n❌ インデックス情報の取得に失敗しました")
                return 1

        if args.delete:
            confirm = input(f"\n⚠️  インデックス '{manager.settings.azure_search_index_name}' を削除しますか? (y/N): ")
            if confirm.lower() == 'y':
                success = manager.delete_index()
                if not success:
                    return 1
            else:
                print("削除をキャンセルしました")

        return 0

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
