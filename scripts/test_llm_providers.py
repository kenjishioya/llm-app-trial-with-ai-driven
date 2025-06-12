#!/usr/bin/env python3
"""
QRAI LLMプロバイダー動作テストスクリプト
=====================================

OpenRouter、Google AI Studio、Azure OpenAI（オプション）の
詳細な動作テスト、パフォーマンステスト、ストリーミングテストを実行します。

使用方法:
    python scripts/test_llm_providers.py
    python scripts/test_llm_providers.py --test chat
    python scripts/test_llm_providers.py --test streaming --provider openrouter
"""

import os
import sys
import time
import asyncio
import argparse
from typing import Dict, Any
from datetime import datetime

# 依存関係チェック
try:
    from openai import OpenAI
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ 必要なライブラリが不足しています: {e}")
    print("以下のコマンドで依存関係をインストールしてください:")
    print("pip install openai google-generativeai python-dotenv")
    sys.exit(1)

# 環境変数読み込み
load_dotenv()


class LLMPerformanceTester:
    """LLMプロバイダー詳細テストクラス"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}

    def log(self, message: str, level: str = "INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            print(f"[{timestamp}] ❌ {message}")
        elif level == "SUCCESS":
            print(f"[{timestamp}] ✅ {message}")
        elif level == "WARNING":
            print(f"[{timestamp}] ⚠️ {message}")
        elif self.verbose or level == "INFO":
            print(f"[{timestamp}] ℹ️ {message}")

    def measure_time(self, start_time: float) -> float:
        """実行時間測定"""
        return round(time.time() - start_time, 2)

    async def test_chat_completion_openrouter(self) -> Dict[str, Any]:
        """OpenRouter チャット完了テスト"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return {"status": "skipped", "error": "API key not set"}

        try:
            client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

            # 複数のテストケース
            test_cases = [
                {
                    "name": "簡単な質問",
                    "messages": [{"role": "user", "content": "Hello, how are you?"}],
                    "expected_tokens": 20,
                },
                {
                    "name": "日本語対応",
                    "messages": [
                        {
                            "role": "user",
                            "content": "こんにちは！今日はいい天気ですね。",
                        }
                    ],
                    "expected_tokens": 30,
                },
                {
                    "name": "コーディング質問",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Write a simple Python function to calculate fibonacci numbers.",
                        }
                    ],
                    "expected_tokens": 100,
                },
                {
                    "name": "推論タスク",
                    "messages": [
                        {
                            "role": "user",
                            "content": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
                        }
                    ],
                    "expected_tokens": 50,
                },
            ]

            results = []
            total_time = 0

            for test_case in test_cases:
                self.log(f"OpenRouter: {test_case['name']} テスト中...", "INFO")
                start_time = time.time()

                response = client.chat.completions.create(
                    model="deepseek/deepseek-r1:free",
                    messages=test_case["messages"],
                    max_tokens=test_case["expected_tokens"],
                    temperature=0.7,
                )

                elapsed_time = self.measure_time(start_time)
                total_time += elapsed_time

                if response.choices and response.choices[0].message.content:
                    content = response.choices[0].message.content.strip()
                    results.append(
                        {
                            "test": test_case["name"],
                            "success": True,
                            "response_length": len(content),
                            "elapsed_time": elapsed_time,
                            "usage": (
                                response.usage.model_dump() if response.usage else None
                            ),
                        }
                    )

                    if self.verbose:
                        self.log(
                            f"応答: {content[:100]}{'...' if len(content) > 100 else ''}",
                            "INFO",
                        )
                else:
                    results.append(
                        {
                            "test": test_case["name"],
                            "success": False,
                            "error": "Empty response",
                        }
                    )

            success_rate = (
                sum(1 for r in results if r.get("success", False)) / len(results) * 100
            )
            avg_time = total_time / len(results)

            return {
                "status": "success",
                "provider": "openrouter",
                "model": "deepseek/deepseek-r1:free",
                "test_results": results,
                "summary": {
                    "success_rate": success_rate,
                    "total_time": total_time,
                    "average_time": avg_time,
                    "tests_count": len(results),
                },
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def test_streaming_openrouter(self) -> Dict[str, Any]:
        """OpenRouter ストリーミングテスト"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return {"status": "skipped", "error": "API key not set"}

        try:
            client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

            self.log("OpenRouter: ストリーミングテスト開始...", "INFO")
            start_time = time.time()

            stream = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {
                        "role": "user",
                        "content": "Write a short story about a robot learning to paint. Make it about 200 words.",
                    }
                ],
                max_tokens=300,
                temperature=0.7,
                stream=True,
            )

            chunks = []
            content_parts = []
            first_chunk_time = None

            for chunk in stream:
                if first_chunk_time is None:
                    first_chunk_time = self.measure_time(start_time)

                chunks.append(chunk)
                if chunk.choices and chunk.choices[0].delta.content:
                    content_parts.append(chunk.choices[0].delta.content)

            total_time = self.measure_time(start_time)
            full_content = "".join(content_parts)

            return {
                "status": "success",
                "provider": "openrouter",
                "streaming": True,
                "total_chunks": len(chunks),
                "content_length": len(full_content),
                "first_chunk_time": first_chunk_time,
                "total_time": total_time,
                "chunks_per_second": len(chunks) / total_time if total_time > 0 else 0,
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def test_chat_completion_google_ai(self) -> Dict[str, Any]:
        """Google AI チャット完了テスト"""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            return {"status": "skipped", "error": "API key not set"}

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            # テストケース
            test_cases = [
                {
                    "name": "簡単な質問",
                    "prompt": "Hello, how are you today?",
                    "max_tokens": 50,
                },
                {
                    "name": "日本語対応",
                    "prompt": "日本の文化について教えてください。",
                    "max_tokens": 100,
                },
                {
                    "name": "創作タスク",
                    "prompt": "Write a haiku about artificial intelligence.",
                    "max_tokens": 100,
                },
                {
                    "name": "分析タスク",
                    "prompt": "Analyze the pros and cons of renewable energy.",
                    "max_tokens": 200,
                },
            ]

            results = []
            total_time = 0

            for test_case in test_cases:
                self.log(f"Google AI: {test_case['name']} テスト中...", "INFO")
                start_time = time.time()

                response = model.generate_content(
                    test_case["prompt"],
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=test_case["max_tokens"], temperature=0.7
                    ),
                )

                elapsed_time = self.measure_time(start_time)
                total_time += elapsed_time

                if response.text:
                    content = response.text.strip()
                    results.append(
                        {
                            "test": test_case["name"],
                            "success": True,
                            "response_length": len(content),
                            "elapsed_time": elapsed_time,
                        }
                    )

                    if self.verbose:
                        self.log(
                            f"応答: {content[:100]}{'...' if len(content) > 100 else ''}",
                            "INFO",
                        )
                else:
                    results.append(
                        {
                            "test": test_case["name"],
                            "success": False,
                            "error": "Empty response",
                        }
                    )

            success_rate = (
                sum(1 for r in results if r.get("success", False)) / len(results) * 100
            )
            avg_time = total_time / len(results)

            return {
                "status": "success",
                "provider": "google_ai",
                "model": "gemini-2.5-flash",
                "test_results": results,
                "summary": {
                    "success_rate": success_rate,
                    "total_time": total_time,
                    "average_time": avg_time,
                    "tests_count": len(results),
                },
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def test_embedding_comparison(self) -> Dict[str, Any]:
        """埋め込みベクトル比較テスト"""
        results = {}

        # OpenRouter埋め込みテスト
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            try:
                client = OpenAI(
                    api_key=openrouter_key, base_url="https://openrouter.ai/api/v1"
                )

                test_text = "This is a sample text for embedding generation."
                start_time = time.time()

                response = client.embeddings.create(
                    model="text-embedding-ada-002", input=test_text
                )

                elapsed_time = self.measure_time(start_time)

                if response.data and len(response.data) > 0:
                    embedding = response.data[0].embedding
                    results["openrouter"] = {
                        "status": "success",
                        "dimensions": len(embedding),
                        "elapsed_time": elapsed_time,
                        "model": "text-embedding-ada-002",
                    }
                else:
                    results["openrouter"] = {
                        "status": "failed",
                        "error": "No embedding data",
                    }

            except Exception as e:
                results["openrouter"] = {"status": "failed", "error": str(e)}

        # Google AI埋め込みテスト（Text Embedding APIが利用可能な場合）
        google_key = os.getenv("GOOGLE_AI_API_KEY")
        if google_key:
            try:
                genai.configure(api_key=google_key)

                test_text = "This is a sample text for embedding generation."
                start_time = time.time()

                # Google AI のembedding APIを使用
                response = genai.embed_content(
                    model="models/text-embedding-004", content=test_text
                )

                elapsed_time = self.measure_time(start_time)

                if response and "embedding" in response:
                    embedding = response["embedding"]
                    results["google_ai"] = {
                        "status": "success",
                        "dimensions": len(embedding),
                        "elapsed_time": elapsed_time,
                        "model": "text-embedding-004",
                    }
                else:
                    results["google_ai"] = {
                        "status": "failed",
                        "error": "No embedding data",
                    }

            except Exception as e:
                results["google_ai"] = {"status": "failed", "error": str(e)}

        return results

    async def run_performance_tests(
        self, test_type: str = "all", provider_filter: str = None
    ) -> Dict[str, Any]:
        """パフォーマンステスト実行"""
        self.log("🔧 QRAI LLMプロバイダー詳細テスト開始", "INFO")
        self.log("=" * 60, "INFO")

        all_results = {}

        # チャット完了テスト
        if test_type in ["all", "chat"]:
            self.log("\n📝 チャット完了テスト", "INFO")
            self.log("-" * 30, "INFO")

            if not provider_filter or provider_filter == "openrouter":
                self.log("OpenRouter テスト中...", "INFO")
                result = await self.test_chat_completion_openrouter()
                all_results["openrouter_chat"] = result

                if result["status"] == "success":
                    summary = result["summary"]
                    self.log(
                        f"✅ OpenRouter: 成功率 {summary['success_rate']:.1f}%, 平均応答時間 {summary['average_time']:.2f}秒",
                        "SUCCESS",
                    )
                else:
                    self.log(
                        f"❌ OpenRouter: {result.get('error', 'Unknown error')}",
                        "ERROR",
                    )

            if not provider_filter or provider_filter == "google_ai":
                self.log("Google AI テスト中...", "INFO")
                result = await self.test_chat_completion_google_ai()
                all_results["google_ai_chat"] = result

                if result["status"] == "success":
                    summary = result["summary"]
                    self.log(
                        f"✅ Google AI: 成功率 {summary['success_rate']:.1f}%, 平均応答時間 {summary['average_time']:.2f}秒",
                        "SUCCESS",
                    )
                else:
                    self.log(
                        f"❌ Google AI: {result.get('error', 'Unknown error')}", "ERROR"
                    )

        # ストリーミングテスト
        if test_type in ["all", "streaming"]:
            self.log("\n🌊 ストリーミングテスト", "INFO")
            self.log("-" * 30, "INFO")

            if not provider_filter or provider_filter == "openrouter":
                result = await self.test_streaming_openrouter()
                all_results["openrouter_streaming"] = result

                if result["status"] == "success":
                    self.log(
                        f"✅ OpenRouter ストリーミング: {result['total_chunks']} chunks, 初回応答 {result['first_chunk_time']}秒",
                        "SUCCESS",
                    )
                else:
                    self.log(
                        f"❌ OpenRouter ストリーミング: {result.get('error', 'Unknown error')}",
                        "ERROR",
                    )

        # 埋め込みテスト
        if test_type in ["all", "embedding"]:
            self.log("\n🧮 埋め込みベクトルテスト", "INFO")
            self.log("-" * 30, "INFO")

            embedding_results = await self.test_embedding_comparison()
            all_results["embedding"] = embedding_results

            for provider, result in embedding_results.items():
                if result["status"] == "success":
                    self.log(
                        f"✅ {provider}: {result['dimensions']} 次元, {result['elapsed_time']}秒",
                        "SUCCESS",
                    )
                else:
                    self.log(
                        f"❌ {provider}: {result.get('error', 'Unknown error')}",
                        "ERROR",
                    )

        # 結果サマリー
        self.log("\n📊 テスト結果サマリー", "INFO")
        self.log("=" * 60, "INFO")

        successful_tests = 0
        total_tests = 0

        for test_name, result in all_results.items():
            total_tests += 1
            if isinstance(result, dict) and result.get("status") == "success":
                successful_tests += 1
                self.log(f"✅ {test_name}: 成功", "SUCCESS")
            elif isinstance(result, dict):
                # 埋め込みテストは複数プロバイダーの結果
                if test_name == "embedding":
                    for provider, prov_result in result.items():
                        total_tests += 1
                        if prov_result.get("status") == "success":
                            successful_tests += 1
                            self.log(f"✅ {test_name}_{provider}: 成功", "SUCCESS")
                        else:
                            self.log(f"❌ {test_name}_{provider}: 失敗", "ERROR")
                else:
                    self.log(f"❌ {test_name}: 失敗", "ERROR")

        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        self.log(
            f"\n🎯 総合成功率: {success_rate:.1f}% ({successful_tests}/{total_tests})",
            "SUCCESS",
        )

        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
            },
            "detailed_results": all_results,
        }


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="QRAI LLMプロバイダー詳細テスト")
    parser.add_argument(
        "--test",
        choices=["all", "chat", "streaming", "embedding"],
        default="all",
        help="実行するテストタイプ",
    )
    parser.add_argument(
        "--provider",
        choices=["openrouter", "google_ai", "azure_openai"],
        help="特定のプロバイダーのみテスト",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細出力")

    args = parser.parse_args()

    # テスト実行
    tester = LLMPerformanceTester(verbose=args.verbose)

    try:
        result = asyncio.run(tester.run_performance_tests(args.test, args.provider))

        # 終了コード決定
        summary = result.get("summary", {})
        if summary.get("successful_tests", 0) == 0:
            sys.exit(1)  # 全テスト失敗

        sys.exit(0)  # 正常終了

    except KeyboardInterrupt:
        print("\n⚠️ テストが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
