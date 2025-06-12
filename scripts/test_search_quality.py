#!/usr/bin/env python3
"""
検索品質検証・テストスクリプト

Task 3-3A-3: 検索品質検証・テスト
- 様々な検索クエリでの品質評価
- レスポンス時間測定
- 関連性スコア分析
- エラーハンドリングテスト
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.search_service import SearchService, SearchServiceError


class SearchQualityTester:
    """検索品質テスト実行クラス"""

    def __init__(self):
        self.search_service = SearchService()
        self.test_results = []
        self.performance_metrics = []

    async def run_all_tests(self) -> Dict[str, Any]:
        """全テストを実行"""
        print("🔍 検索品質検証・テスト開始")
        print("=" * 50)

        # 1. 基本検索テスト
        await self._test_basic_search()

        # 2. 関連性テスト
        await self._test_relevance()

        # 3. パフォーマンステスト
        await self._test_performance()

        # 4. エラーハンドリングテスト
        await self._test_error_handling()

        # 5. 多様なクエリテスト
        await self._test_diverse_queries()

        # 6. 結果の分析と報告
        return await self._generate_report()

    async def _test_basic_search(self):
        """基本検索機能テスト"""
        print("\n📋 1. 基本検索機能テスト")
        print("-" * 30)

        basic_queries = [
            "machine learning",
            "Azure",
            "Python",
            "artificial intelligence",
            "cloud computing",
            "natural language processing"
        ]

        for query in basic_queries:
            try:
                start_time = time.time()
                result = await self.search_service.search_documents(
                    query=query,
                    top=5
                )
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # ms
                doc_count = len(result.get("documents", []))

                test_result = {
                    "test_type": "basic_search",
                    "query": query,
                    "success": True,
                    "document_count": doc_count,
                    "response_time_ms": response_time,
                    "has_results": doc_count > 0
                }

                self.test_results.append(test_result)
                self.performance_metrics.append({
                    "query": query,
                    "response_time_ms": response_time
                })

                status = "✅" if doc_count > 0 else "⚠️"
                print(f"{status} '{query}': {doc_count} docs, {response_time:.1f}ms")

            except Exception as e:
                test_result = {
                    "test_type": "basic_search",
                    "query": query,
                    "success": False,
                    "error": str(e)
                }
                self.test_results.append(test_result)
                print(f"❌ '{query}': Error - {e}")

    async def _test_relevance(self):
        """関連性テスト"""
        print("\n🎯 2. 関連性テスト")
        print("-" * 30)

        relevance_tests = [
            {
                "query": "machine learning algorithms",
                "expected_keywords": ["machine", "learning", "algorithm", "model"],
                "min_score": 1.0
            },
            {
                "query": "Azure AI services",
                "expected_keywords": ["azure", "ai", "artificial", "intelligence"],
                "min_score": 1.0
            },
            {
                "query": "Python programming best practices",
                "expected_keywords": ["python", "programming", "code", "practice"],
                "min_score": 1.0
            }
        ]

        for test_case in relevance_tests:
            try:
                result = await self.search_service.search_documents(
                    query=test_case["query"],
                    top=3
                )

                documents = result.get("documents", [])
                if not documents:
                    print(f"⚠️ '{test_case['query']}': No results found")
                    continue

                # 関連性分析
                relevance_scores = []
                keyword_matches = []

                for doc in documents:
                    score = doc.get("score", 0)
                    content = doc.get("document", {}).get("content", "").lower()
                    title = doc.get("document", {}).get("title", "").lower()
                    full_text = f"{title} {content}"

                    # キーワードマッチング
                    matches = sum(1 for keyword in test_case["expected_keywords"]
                                if keyword.lower() in full_text)
                    keyword_match_ratio = matches / len(test_case["expected_keywords"])

                    relevance_scores.append(score)
                    keyword_matches.append(keyword_match_ratio)

                avg_score = sum(relevance_scores) / len(relevance_scores)
                avg_keyword_match = sum(keyword_matches) / len(keyword_matches)

                test_result = {
                    "test_type": "relevance",
                    "query": test_case["query"],
                    "avg_score": avg_score,
                    "avg_keyword_match": avg_keyword_match,
                    "meets_min_score": avg_score >= test_case["min_score"],
                    "document_count": len(documents)
                }

                self.test_results.append(test_result)

                status = "✅" if avg_score >= test_case["min_score"] else "⚠️"
                print(f"{status} '{test_case['query']}': Score {avg_score:.2f}, Keywords {avg_keyword_match:.1%}")

            except Exception as e:
                print(f"❌ '{test_case['query']}': Error - {e}")

    async def _test_performance(self):
        """パフォーマンステスト"""
        print("\n⚡ 3. パフォーマンステスト")
        print("-" * 30)

        # 同時実行テスト
        concurrent_queries = [
            "AI", "ML", "Azure", "Python", "cloud", "data", "search", "algorithm"
        ]

        print("同時実行テスト (8クエリ並列)...")
        start_time = time.time()

        tasks = [
            self.search_service.search_documents(query=query, top=3)
            for query in concurrent_queries
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_time = (end_time - start_time) * 1000
            successful_queries = sum(1 for r in results if not isinstance(r, Exception))

            print(f"✅ 並列実行: {successful_queries}/{len(concurrent_queries)} 成功, {total_time:.1f}ms")

            # レスポンス時間分析
            if self.performance_metrics:
                response_times = [m["response_time_ms"] for m in self.performance_metrics]
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)

                print(f"📊 レスポンス時間統計:")
                print(f"   平均: {avg_time:.1f}ms")
                print(f"   最大: {max_time:.1f}ms")
                print(f"   最小: {min_time:.1f}ms")

                performance_result = {
                    "test_type": "performance",
                    "concurrent_success_rate": successful_queries / len(concurrent_queries),
                    "avg_response_time_ms": avg_time,
                    "max_response_time_ms": max_time,
                    "min_response_time_ms": min_time,
                    "total_concurrent_time_ms": total_time
                }
                self.test_results.append(performance_result)

        except Exception as e:
            print(f"❌ 並列実行テストエラー: {e}")

    async def _test_error_handling(self):
        """エラーハンドリングテスト"""
        print("\n🛡️ 4. エラーハンドリングテスト")
        print("-" * 30)

        error_test_cases = [
            {"query": "", "description": "空クエリ"},
            {"query": "a" * 1000, "description": "超長クエリ"},
            {"query": "!@#$%^&*()", "description": "特殊文字"},
            {"query": "SELECT * FROM users", "description": "SQLインジェクション試行"}
        ]

        for test_case in error_test_cases:
            try:
                result = await self.search_service.search_documents(
                    query=test_case["query"],
                    top=5
                )

                # エラーが発生しなかった場合
                doc_count = len(result.get("documents", []))
                print(f"✅ {test_case['description']}: {doc_count} docs (正常処理)")

                test_result = {
                    "test_type": "error_handling",
                    "description": test_case["description"],
                    "query": test_case["query"][:50] + "..." if len(test_case["query"]) > 50 else test_case["query"],
                    "handled_gracefully": True,
                    "document_count": doc_count
                }
                self.test_results.append(test_result)

            except SearchServiceError as e:
                print(f"✅ {test_case['description']}: 適切にエラーハンドリング - {e}")
                test_result = {
                    "test_type": "error_handling",
                    "description": test_case["description"],
                    "handled_gracefully": True,
                    "error_type": "SearchServiceError"
                }
                self.test_results.append(test_result)

            except Exception as e:
                print(f"⚠️ {test_case['description']}: 予期しないエラー - {e}")
                test_result = {
                    "test_type": "error_handling",
                    "description": test_case["description"],
                    "handled_gracefully": False,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                self.test_results.append(test_result)

    async def _test_diverse_queries(self):
        """多様なクエリテスト"""
        print("\n🌐 5. 多様なクエリテスト")
        print("-" * 30)

        diverse_queries = [
            # 技術用語
            {"query": "neural networks", "category": "technical"},
            {"query": "deep learning", "category": "technical"},
            {"query": "transformer architecture", "category": "technical"},

            # 日本語（もしあれば）
            {"query": "機械学習", "category": "japanese"},
            {"query": "人工知能", "category": "japanese"},

            # 複合クエリ
            {"query": "Azure machine learning service", "category": "compound"},
            {"query": "Python data science libraries", "category": "compound"},

            # 短いクエリ
            {"query": "AI", "category": "short"},
            {"query": "ML", "category": "short"},

            # 長いクエリ
            {"query": "how to implement machine learning algorithms in Python for data analysis", "category": "long"}
        ]

        category_results = {}

        for test_case in diverse_queries:
            try:
                start_time = time.time()
                result = await self.search_service.search_documents(
                    query=test_case["query"],
                    top=5
                )
                end_time = time.time()

                response_time = (end_time - start_time) * 1000
                doc_count = len(result.get("documents", []))

                category = test_case["category"]
                if category not in category_results:
                    category_results[category] = []

                category_results[category].append({
                    "query": test_case["query"],
                    "document_count": doc_count,
                    "response_time_ms": response_time
                })

                status = "✅" if doc_count > 0 else "⚠️"
                print(f"{status} [{category}] '{test_case['query']}': {doc_count} docs")

            except Exception as e:
                print(f"❌ [{test_case['category']}] '{test_case['query']}': Error - {e}")

        # カテゴリ別統計
        print("\n📊 カテゴリ別統計:")
        for category, results in category_results.items():
            if results:
                avg_docs = sum(r["document_count"] for r in results) / len(results)
                avg_time = sum(r["response_time_ms"] for r in results) / len(results)
                success_rate = sum(1 for r in results if r["document_count"] > 0) / len(results)

                print(f"   {category}: 平均{avg_docs:.1f}docs, {avg_time:.1f}ms, 成功率{success_rate:.1%}")

                category_result = {
                    "test_type": "diverse_queries",
                    "category": category,
                    "avg_document_count": avg_docs,
                    "avg_response_time_ms": avg_time,
                    "success_rate": success_rate,
                    "query_count": len(results)
                }
                self.test_results.append(category_result)

    async def _generate_report(self) -> Dict[str, Any]:
        """テスト結果レポート生成"""
        print("\n📋 6. テスト結果レポート")
        print("=" * 50)

        # 全体統計
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results
                             if r.get("success", True) and not r.get("error"))

        # パフォーマンス統計
        if self.performance_metrics:
            response_times = [m["response_time_ms"] for m in self.performance_metrics]
            avg_response_time = sum(response_times) / len(response_times)
        else:
            avg_response_time = 0

        # 検索品質統計
        relevance_tests = [r for r in self.test_results if r.get("test_type") == "relevance"]
        if relevance_tests:
            avg_relevance_score = sum(r.get("avg_score", 0) for r in relevance_tests) / len(relevance_tests)
            avg_keyword_match = sum(r.get("avg_keyword_match", 0) for r in relevance_tests) / len(relevance_tests)
        else:
            avg_relevance_score = 0
            avg_keyword_match = 0

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "test_timestamp": datetime.now().isoformat()
            },
            "performance_metrics": {
                "avg_response_time_ms": avg_response_time,
                "total_queries_tested": len(self.performance_metrics)
            },
            "quality_metrics": {
                "avg_relevance_score": avg_relevance_score,
                "avg_keyword_match_rate": avg_keyword_match,
                "relevance_tests_count": len(relevance_tests)
            },
            "detailed_results": self.test_results
        }

        # コンソール出力
        print(f"✅ 総合成功率: {report['test_summary']['success_rate']:.1%}")
        print(f"⚡ 平均レスポンス時間: {avg_response_time:.1f}ms")
        print(f"🎯 平均関連性スコア: {avg_relevance_score:.2f}")
        print(f"🔍 キーワードマッチ率: {avg_keyword_match:.1%}")

        # 推奨事項
        print("\n💡 推奨事項:")
        if avg_response_time > 5000:
            print("   ⚠️ レスポンス時間が5秒を超えています。インデックス最適化を検討してください。")
        if avg_relevance_score < 2.0:
            print("   ⚠️ 関連性スコアが低めです。検索アルゴリズムの調整を検討してください。")
        if avg_keyword_match < 0.5:
            print("   ⚠️ キーワードマッチ率が低めです。ドキュメントの品質向上を検討してください。")

        if (avg_response_time <= 5000 and avg_relevance_score >= 2.0 and avg_keyword_match >= 0.5):
            print("   ✅ 検索品質は良好です！")

        return report


async def main():
    """メイン実行関数"""
    try:
        tester = SearchQualityTester()
        report = await tester.run_all_tests()

        # レポートをファイルに保存
        report_file = Path("test_results") / f"search_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 詳細レポートを保存しました: {report_file}")
        print("\n🎉 検索品質検証・テスト完了！")

        return report

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(main())
