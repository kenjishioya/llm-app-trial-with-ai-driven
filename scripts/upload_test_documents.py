#!/usr/bin/env python3
"""
テストドキュメントアップロードスクリプト
Task 3-3A-2: テストドキュメントインデックス投入

使用例:
    python scripts/upload_test_documents.py
    python scripts/upload_test_documents.py --verify-only
    python scripts/upload_test_documents.py --category wikipedia
"""

import asyncio
import argparse
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
from tqdm import tqdm

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.document_pipeline import DocumentPipeline, DocumentPipelineError, ProcessingResult
from services.search_service import SearchService, SearchServiceError
from config import get_settings


class TestDocumentUploader:
    """テストドキュメント専用アップローダー"""

    def __init__(self, verbose: bool = False):
        """初期化"""
        self.verbose = verbose
        self.settings = get_settings()
        self.pipeline = DocumentPipeline()
        self.search_service = SearchService()
        self.test_docs_dir = Path(__file__).parent.parent / "test_documents"
        self.manifest_file = self.test_docs_dir / "test_documents_manifest.json"
        self.results: List[Dict[str, Any]] = []

    async def load_manifest(self) -> Dict[str, Any]:
        """マニフェストファイルを読み込み"""
        if not self.manifest_file.exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_file}")

        with open(self.manifest_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def upload_all_test_documents(self) -> Dict[str, Any]:
        """全テストドキュメントをアップロード"""
        print("🚀 Starting test document upload process...")

        # マニフェスト読み込み
        manifest = await self.load_manifest()
        print(f"📋 Loaded manifest: {manifest['total_documents']} documents in {len(manifest['categories'])} categories")

        # ヘルスチェック
        await self._health_check()

        # カテゴリ別アップロード
        upload_summary = {
            "start_time": datetime.utcnow().isoformat(),
            "categories": {},
            "total_success": 0,
            "total_errors": 0,
            "total_chunks": 0
        }

        for category_name, category_info in manifest['categories'].items():
            print(f"\n📁 Processing category: {category_name}")
            print(f"   Description: {category_info['description']}")
            print(f"   Files: {category_info['count']}")

            category_result = await self._upload_category(category_name, category_info)
            upload_summary["categories"][category_name] = category_result
            upload_summary["total_success"] += category_result["success_count"]
            upload_summary["total_errors"] += category_result["error_count"]
            upload_summary["total_chunks"] += category_result["total_chunks"]

        upload_summary["end_time"] = datetime.utcnow().isoformat()
        upload_summary["duration_seconds"] = (
            datetime.fromisoformat(upload_summary["end_time"]) -
            datetime.fromisoformat(upload_summary["start_time"])
        ).total_seconds()

        # 結果サマリー表示
        self._print_upload_summary(upload_summary)

        return upload_summary

    async def upload_category(self, category_name: str) -> Dict[str, Any]:
        """特定カテゴリのドキュメントをアップロード"""
        manifest = await self.load_manifest()

        if category_name not in manifest['categories']:
            raise ValueError(f"Category '{category_name}' not found in manifest")

        category_info = manifest['categories'][category_name]
        print(f"📁 Processing category: {category_name}")
        print(f"   Description: {category_info['description']}")

        await self._health_check()

        return await self._upload_category(category_name, category_info)

    async def _upload_category(self, category_name: str, category_info: Dict[str, Any]) -> Dict[str, Any]:
        """カテゴリ内のファイルをアップロード"""
        category_dir = self.test_docs_dir / category_name
        files = category_info['files']

        success_count = 0
        error_count = 0
        total_chunks = 0
        results = []

        # プログレスバー付きでファイル処理
        with tqdm(files, desc=f"Uploading {category_name}", unit="file") as pbar:
            for filename in pbar:
                file_path = category_dir / filename
                pbar.set_postfix(file=filename[:20])

                try:
                    # ファイル存在確認
                    if not file_path.exists():
                        raise FileNotFoundError(f"File not found: {file_path}")

                    # サポートされるファイル形式かチェック
                    if not self._is_supported_file(file_path):
                        if self.verbose:
                            print(f"⏭️  Skipping unsupported file: {filename}")
                        continue

                    # アップロード実行
                    result = await self._upload_single_file(file_path, category_name)

                    if isinstance(result, ProcessingResult):
                        success_count += 1
                        total_chunks += result.chunks_count
                        results.append({
                            "file": filename,
                            "status": "success",
                            "document_id": result.document_id,
                            "chunks_count": result.chunks_count,
                            "processing_time": result.processing_time
                        })

                        if self.verbose:
                            print(f"✅ {filename}: {result.chunks_count} chunks")

                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    results.append({
                        "file": filename,
                        "status": "error",
                        "error": error_msg
                    })

                    if self.verbose:
                        print(f"❌ {filename}: {error_msg}")

        return {
            "category": category_name,
            "success_count": success_count,
            "error_count": error_count,
            "total_chunks": total_chunks,
            "files_processed": len(files),
            "results": results
        }

    async def _upload_single_file(
        self,
        file_path: Path,
        category: str
    ) -> ProcessingResult:
        """単一ファイルのアップロード"""
        # ファイル読み込み
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Content-Typeの推定
        content_type = self._detect_content_type(file_path)

        # テストドキュメント用メタデータ
        metadata = {
            "source": "test_documents",
            "category": category,
            "test_document": True,
            "file_size": len(file_content),
            "uploaded_via": "test_upload_script",
            "upload_timestamp": datetime.utcnow().isoformat()
        }

        # ドキュメント処理実行
        return await self.pipeline.process_document(
            file_content=file_content,
            filename=file_path.name,
            content_type=content_type,
            metadata=metadata
        )

    async def verify_upload(self) -> Dict[str, Any]:
        """アップロード結果の検証"""
        print("🔍 Verifying uploaded test documents...")

        # 検索テストクエリ
        test_queries = [
            "Azure AI Search",
            "machine learning",
            "Python best practices",
            "cloud computing",
            "natural language processing"
        ]

        verification_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "queries_tested": len(test_queries),
            "search_results": {}
        }

        for query in test_queries:
            try:
                print(f"🔎 Testing query: '{query}'")

                # 検索実行
                search_results = await self.search_service.search_documents(
                    query=query,
                    top_k=5
                )

                verification_results["search_results"][query] = {
                    "status": "success",
                    "results_count": len(search_results),
                    "top_score": search_results[0]["score"] if search_results else 0.0,
                    "has_test_documents": any(
                        result.get("metadata", {}).get("test_document", False)
                        for result in search_results
                    )
                }

                print(f"   Found {len(search_results)} results (top score: {search_results[0]['score']:.3f})" if search_results else "   No results found")

            except Exception as e:
                verification_results["search_results"][query] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"   ❌ Error: {e}")

        return verification_results

    async def _health_check(self) -> None:
        """システムヘルスチェック"""
        if self.verbose:
            print("🔍 Checking system health...")

        health = await self.pipeline.health_check()

        if health['status'] != 'healthy':
            print(f"⚠️  System health check failed: {health['status']}")
            for component, status in health.get('components', {}).items():
                if status['status'] != 'healthy':
                    print(f"   ❌ {component}: {status['status']}")
            raise RuntimeError("System is not healthy")

        if self.verbose:
            print("✅ System health check passed")

    def _detect_content_type(self, file_path: Path) -> str:
        """ファイル拡張子からContent-Typeを推定"""
        ext = file_path.suffix.lower()
        content_type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.markdown': 'text/markdown',
            '.json': 'application/json'
        }
        return content_type_map.get(ext, 'text/plain')

    def _is_supported_file(self, file_path: Path) -> bool:
        """サポートされるファイル形式かチェック"""
        # JSONファイルはスキップ（メタデータファイル）
        if file_path.suffix.lower() == '.json':
            return False

        content_type = self._detect_content_type(file_path)
        return self.pipeline.is_supported_file_type(content_type)

    def _print_upload_summary(self, summary: Dict[str, Any]) -> None:
        """アップロード結果サマリーを表示"""
        print("\n" + "="*60)
        print("📊 UPLOAD SUMMARY")
        print("="*60)

        print(f"⏱️  Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"✅ Total Success: {summary['total_success']}")
        print(f"❌ Total Errors: {summary['total_errors']}")
        print(f"📄 Total Chunks Created: {summary['total_chunks']}")

        print("\n📁 Category Breakdown:")
        for category, result in summary['categories'].items():
            success_rate = (result['success_count'] / result['files_processed'] * 100) if result['files_processed'] > 0 else 0
            print(f"   {category}: {result['success_count']}/{result['files_processed']} files ({success_rate:.1f}%) - {result['total_chunks']} chunks")

        if summary['total_errors'] > 0:
            print("\n❌ Errors occurred. Use --verbose for details.")

        print("="*60)

    async def save_results(self, results: Dict[str, Any], output_file: Optional[Path] = None) -> None:
        """結果をJSONファイルに保存"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(f"test_upload_results_{timestamp}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: {output_file}")


async def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Upload test documents to Azure AI Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/upload_test_documents.py                    # Upload all test documents
  python scripts/upload_test_documents.py --category wikipedia  # Upload only wikipedia category
  python scripts/upload_test_documents.py --verify-only      # Only verify existing uploads
  python scripts/upload_test_documents.py --verbose          # Verbose output
        """
    )

    parser.add_argument(
        '--category',
        type=str,
        help='Upload only specific category (wikipedia, qa_datasets, technical_docs, sample_pdfs)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify uploaded documents, do not upload'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file for results (JSON format)'
    )

    args = parser.parse_args()

    try:
        uploader = TestDocumentUploader(verbose=args.verbose)

        if args.verify_only:
            # 検証のみ実行
            results = await uploader.verify_upload()
            print("\n✅ Verification completed")
        elif args.category:
            # 特定カテゴリのみアップロード
            results = await uploader.upload_category(args.category)
            print(f"\n✅ Category '{args.category}' upload completed")
        else:
            # 全ドキュメントアップロード
            results = await uploader.upload_all_test_documents()
            print("\n✅ All test documents upload completed")

            # アップロード後の検証
            print("\n" + "-"*40)
            verification_results = await uploader.verify_upload()
            results["verification"] = verification_results

        # 結果保存
        if args.output:
            await uploader.save_results(results, args.output)

    except KeyboardInterrupt:
        print("\n⚠️  Upload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
