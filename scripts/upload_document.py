#!/usr/bin/env python3
"""
ドキュメントアップロードCLIスクリプト
Task 3-2B-1: CLIアップロードスクリプト

使用例:
    python scripts/upload_document.py file.pdf
    python scripts/upload_document.py --batch documents/
    python scripts/upload_document.py --help
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.document_pipeline import DocumentPipeline, DocumentPipelineError, ProcessingResult
from services.blob_storage_service import BlobStorageService, BlobStorageError
from services.document_parser import DocumentParser, DocumentParserError
from services.search_service import SearchService, SearchServiceError
from config import get_settings


class DocumentUploader:
    """ドキュメントアップロード管理クラス"""

    def __init__(self, verbose: bool = False):
        """初期化"""
        self.verbose = verbose
        self.settings = get_settings()
        self.pipeline = DocumentPipeline()
        self.results: List[Dict[str, Any]] = []

    async def upload_single_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """単一ファイルのアップロード"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # ファイル読み込み
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        except Exception as e:
            raise DocumentPipelineError(f"Failed to read file {file_path}: {e}")

        # Content-Typeの推定
        content_type = self._detect_content_type(file_path)

        # メタデータの準備
        file_metadata = {
            "source_path": str(file_path.absolute()),
            "file_size": len(file_content),
            "uploaded_via": "cli_script",
            "upload_timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }

        if self.verbose:
            print(f"📄 Processing: {file_path.name}")
            print(f"   Size: {len(file_content):,} bytes")
            print(f"   Type: {content_type}")

        # ドキュメント処理実行
        start_time = time.time()
        try:
            result = await self.pipeline.process_document(
                file_content=file_content,
                filename=file_path.name,
                content_type=content_type,
                metadata=file_metadata
            )

            processing_time = time.time() - start_time

            if self.verbose:
                print(f"✅ Success: {result.chunks_count} chunks indexed in {processing_time:.2f}s")
                print(f"   Document ID: {result.document_id}")
                print(f"   Blob URL: {result.blob_url}")

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            if self.verbose:
                print(f"❌ Failed: {str(e)} (after {processing_time:.2f}s)")
            raise

    async def upload_batch(
        self,
        directory: Path,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[ProcessingResult]:
        """バッチアップロード"""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # ファイル一覧取得
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))

        # ファイルのみをフィルタ
        files = [f for f in files if f.is_file() and self._is_supported_file(f)]

        if not files:
            print(f"⚠️  No supported files found in {directory}")
            return []

        print(f"📁 Found {len(files)} files to process")

        results = []
        success_count = 0
        error_count = 0

        for i, file_path in enumerate(files, 1):
            try:
                if self.verbose:
                    print(f"\n[{i}/{len(files)}] ", end="")
                else:
                    print(f"Processing {file_path.name}... ", end="", flush=True)

                result = await self.upload_single_file(file_path)
                results.append(result)
                success_count += 1

                if not self.verbose:
                    print("✅")

            except Exception as e:
                error_count += 1
                error_info = {
                    "file_path": str(file_path),
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                results.append(error_info)

                if self.verbose:
                    print(f"❌ Error: {e}")
                else:
                    print(f"❌ {e}")

        print(f"\n📊 Batch upload completed:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📄 Total: {len(files)}")

        return results

    def _detect_content_type(self, file_path: Path) -> str:
        """ファイル拡張子からContent-Typeを推定"""
        ext = file_path.suffix.lower()
        content_type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.markdown': 'text/markdown'
        }
        return content_type_map.get(ext, 'application/octet-stream')

    def _is_supported_file(self, file_path: Path) -> bool:
        """サポートされるファイル形式かチェック"""
        content_type = self._detect_content_type(file_path)
        return self.pipeline.is_supported_file_type(content_type)

    async def health_check(self) -> Dict[str, Any]:
        """システムヘルスチェック"""
        print("🔍 Checking system health...")

        health = await self.pipeline.health_check()

        print(f"Overall Status: {health['status'].upper()}")
        print("\nComponents:")

        for component, status in health.get('components', {}).items():
            status_icon = "✅" if status['status'] == 'healthy' else "❌"
            print(f"  {status_icon} {component}: {status['status']}")

        if health['status'] != 'healthy':
            print("\n⚠️  Some components are not healthy. Upload may fail.")
            return health

        print("\n✅ All systems ready for upload!")
        return health

    def save_results(self, results: List[Any], output_file: Path) -> None:
        """結果をJSONファイルに保存"""
        try:
            # ProcessingResultオブジェクトを辞書に変換
            serializable_results = []
            for result in results:
                if hasattr(result, '__dict__'):
                    # dataclassの場合
                    result_dict = {
                        k: v for k, v in result.__dict__.items()
                        if not k.startswith('_')
                    }
                    serializable_results.append(result_dict)
                else:
                    # 既に辞書の場合（エラー情報など）
                    serializable_results.append(result)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False, default=str)

            print(f"📄 Results saved to: {output_file}")

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")


async def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="ドキュメントアップロードCLIツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 単一ファイルアップロード
  python scripts/upload_document.py document.pdf

  # バッチアップロード
  python scripts/upload_document.py --batch documents/

  # 再帰的バッチアップロード
  python scripts/upload_document.py --batch documents/ --recursive

  # 詳細ログ付きアップロード
  python scripts/upload_document.py document.pdf --verbose

  # ヘルスチェックのみ
  python scripts/upload_document.py --health-check

  # 結果をファイルに保存
  python scripts/upload_document.py --batch documents/ --output results.json
        """
    )

    # 引数定義
    parser.add_argument(
        'path',
        nargs='?',
        type=Path,
        help='アップロードするファイルまたはディレクトリのパス'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='バッチアップロードモード（ディレクトリ内の全ファイル）'
    )

    parser.add_argument(
        '--recursive',
        action='store_true',
        help='再帰的にサブディレクトリも処理'
    )

    parser.add_argument(
        '--pattern',
        default='*',
        help='バッチモードでのファイルパターン（デフォルト: *）'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを表示'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='結果をJSONファイルに保存'
    )

    parser.add_argument(
        '--health-check',
        action='store_true',
        help='ヘルスチェックのみ実行'
    )

    args = parser.parse_args()

    # 引数検証
    if not args.health_check and not args.path:
        parser.error("ファイルパスまたは --health-check が必要です")

    try:
        uploader = DocumentUploader(verbose=args.verbose)

        # ヘルスチェック
        if args.health_check:
            await uploader.health_check()
            return

        # ヘルスチェック（アップロード前）
        health = await uploader.health_check()
        if health['status'] != 'healthy':
            print("\n⚠️  System is not healthy. Continue anyway? (y/N): ", end="")
            if input().lower() != 'y':
                print("Upload cancelled.")
                sys.exit(1)

        # アップロード実行
        results = []
        start_time = time.time()

        if args.batch:
            results = await uploader.upload_batch(
                directory=args.path,
                pattern=args.pattern,
                recursive=args.recursive
            )
        else:
            result = await uploader.upload_single_file(args.path)
            results = [result]

        total_time = time.time() - start_time

        # 結果サマリー
        print(f"\n🎉 Upload completed in {total_time:.2f}s")

        if args.output:
            uploader.save_results(results, args.output)

    except KeyboardInterrupt:
        print("\n\n⚠️  Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
