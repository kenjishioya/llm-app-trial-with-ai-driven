#!/usr/bin/env python3
"""
QRAI LLMプロバイダー設定確認スクリプト
=========================================

OpenRouter、Google AI Studio、Azure OpenAI（オプション）の接続確認と
基本的な動作テストを実行します。

使用方法:
    python scripts/check_llm_config.py
    python scripts/check_llm_config.py --provider openrouter
    python scripts/check_llm_config.py --verbose
"""

import os
import sys
import asyncio
import argparse
from typing import Dict, Any, Optional
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


class LLMProviderTester:
    """LLMプロバイダーテストクラス"""

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

    async def check_openrouter(self) -> Dict[str, Any]:
        """OpenRouter接続確認"""
        provider_name = "OpenRouter"
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            self.log(
                f"{provider_name}: APIキーが設定されていません (OPENROUTER_API_KEY)",
                "ERROR",
            )
            return {"status": "failed", "error": "API key not set"}

        self.log(f"{provider_name}: 接続テスト開始...", "INFO")

        try:
            client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

            # 基本的なチャット完了テスト
            response = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {
                        "role": "user",
                        "content": "Hello! Please respond with 'OpenRouter is working!'",
                    }
                ],
                max_tokens=50,
                temperature=0.7,
            )

            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                self.log(f"{provider_name}: 接続成功", "SUCCESS")
                self.log(f"{provider_name}: レスポンス: {content}", "INFO")

                # モデル情報取得テスト
                try:
                    models_response = client.models.list()
                    available_models = (
                        len(models_response.data)
                        if hasattr(models_response, "data")
                        else 0
                    )
                    self.log(
                        f"{provider_name}: 利用可能モデル数: {available_models}", "INFO"
                    )
                except Exception as e:
                    self.log(f"{provider_name}: モデル一覧取得失敗: {e}", "WARNING")

                return {
                    "status": "success",
                    "response": content,
                    "model": "deepseek/deepseek-r1:free",
                    "usage": response.usage.model_dump() if response.usage else None,
                }
            else:
                self.log(f"{provider_name}: 空のレスポンス", "ERROR")
                return {"status": "failed", "error": "Empty response"}

        except Exception as e:
            self.log(f"{provider_name}: 接続失敗 - {str(e)}", "ERROR")
            return {"status": "failed", "error": str(e)}

    async def check_google_ai(self) -> Dict[str, Any]:
        """Google AI Studio接続確認"""
        provider_name = "Google AI"
        api_key = os.getenv("GOOGLE_AI_API_KEY")

        if not api_key:
            self.log(
                f"{provider_name}: APIキーが設定されていません (GOOGLE_AI_API_KEY)",
                "ERROR",
            )
            return {"status": "failed", "error": "API key not set"}

        self.log(f"{provider_name}: 接続テスト開始...", "INFO")

        try:
            genai.configure(api_key=api_key)

            # 利用可能モデル確認
            try:
                models = list(genai.list_models())
                available_models = [
                    m.name
                    for m in models
                    if "generateContent" in m.supported_generation_methods
                ]
                self.log(
                    f"{provider_name}: 利用可能モデル数: {len(available_models)}",
                    "INFO",
                )
            except Exception as e:
                self.log(f"{provider_name}: モデル一覧取得失敗: {e}", "WARNING")
                available_models = []

            # 基本的なチャット完了テスト
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                "Hello! Please respond with 'Google AI is working!'",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=50, temperature=0.7
                ),
            )

            if response.text:
                content = response.text.strip()
                self.log(f"{provider_name}: 接続成功", "SUCCESS")
                self.log(f"{provider_name}: レスポンス: {content}", "INFO")

                return {
                    "status": "success",
                    "response": content,
                    "model": "gemini-2.5-flash",
                    "available_models": len(available_models),
                }
            else:
                self.log(f"{provider_name}: 空のレスポンス", "ERROR")
                return {"status": "failed", "error": "Empty response"}

        except Exception as e:
            self.log(f"{provider_name}: 接続失敗 - {str(e)}", "ERROR")
            return {"status": "failed", "error": str(e)}

    async def check_azure_openai(self) -> Dict[str, Any]:
        """Azure OpenAI接続確認"""
        provider_name = "Azure OpenAI"
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

        if not api_key or not endpoint:
            self.log(
                f"{provider_name}: APIキーまたはエンドポイントが設定されていません",
                "WARNING",
            )
            return {"status": "skipped", "error": "API key or endpoint not set"}

        self.log(f"{provider_name}: 接続テスト開始...", "INFO")

        try:
            from openai import AzureOpenAI

            client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version="2024-02-15-preview",
            )

            # 基本的なチャット完了テスト
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # デプロイメント名
                messages=[
                    {
                        "role": "user",
                        "content": "Hello! Please respond with 'Azure OpenAI is working!'",
                    }
                ],
                max_tokens=50,
                temperature=0.7,
            )

            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                self.log(f"{provider_name}: 接続成功", "SUCCESS")
                self.log(f"{provider_name}: レスポンス: {content}", "INFO")

                return {
                    "status": "success",
                    "response": content,
                    "model": "gpt-4o-mini",
                    "endpoint": endpoint,
                    "usage": response.usage.model_dump() if response.usage else None,
                }
            else:
                self.log(f"{provider_name}: 空のレスポンス", "ERROR")
                return {"status": "failed", "error": "Empty response"}

        except Exception as e:
            self.log(f"{provider_name}: 接続失敗 - {str(e)}", "ERROR")
            return {"status": "failed", "error": str(e)}

    async def run_all_tests(
        self, provider_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """全プロバイダーのテスト実行"""
        self.log("🔍 QRAI LLMプロバイダー設定確認開始", "INFO")
        self.log("=" * 50, "INFO")

        # テスト対象プロバイダー
        tests = {
            "openrouter": self.check_openrouter,
            "google_ai": self.check_google_ai,
            "azure_openai": self.check_azure_openai,
        }

        # フィルタリング
        if provider_filter:
            if provider_filter in tests:
                tests = {provider_filter: tests[provider_filter]}
            else:
                self.log(f"不明なプロバイダー: {provider_filter}", "ERROR")
                return {"error": f"Unknown provider: {provider_filter}"}

        # テスト実行
        for provider_name, test_func in tests.items():
            self.log(f"\n--- {provider_name.upper()} テスト ---", "INFO")
            result = await test_func()
            self.results[provider_name] = result

        # 結果サマリー
        self.log("\n📊 テスト結果サマリー", "INFO")
        self.log("=" * 50, "INFO")

        success_count = 0
        total_count = 0

        for provider_name, result in self.results.items():
            total_count += 1
            status = result.get("status", "unknown")

            if status == "success":
                success_count += 1
                self.log(f"✅ {provider_name}: 正常", "SUCCESS")
            elif status == "skipped":
                self.log(f"⏭️ {provider_name}: スキップ (設定なし)", "WARNING")
            else:
                error = result.get("error", "Unknown error")
                self.log(f"❌ {provider_name}: 失敗 ({error})", "ERROR")

        # 推奨設定
        if success_count > 0:
            self.log(
                f"\n🎉 {success_count}/{total_count} プロバイダーが利用可能です",
                "SUCCESS",
            )

            # 推奨設定提案
            if (
                "openrouter" in self.results
                and self.results["openrouter"]["status"] == "success"
            ):
                self.log("💡 推奨: OpenRouterをプライマリプロバイダーに設定", "INFO")
            elif (
                "google_ai" in self.results
                and self.results["google_ai"]["status"] == "success"
            ):
                self.log("💡 推奨: Google AIをプライマリプロバイダーに設定", "INFO")
        else:
            self.log("⚠️ 利用可能なプロバイダーがありません", "WARNING")
            self.log(
                "📖 設定ガイド: docs/environment_setup.md を参照してください", "INFO"
            )

        return {
            "summary": {
                "total": total_count,
                "success": success_count,
                "failed": total_count - success_count,
            },
            "results": self.results,
        }


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="QRAI LLMプロバイダー設定確認")
    parser.add_argument(
        "--provider",
        choices=["openrouter", "google_ai", "azure_openai"],
        help="特定のプロバイダーのみテスト",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細出力")

    args = parser.parse_args()

    # テスト実行
    tester = LLMProviderTester(verbose=args.verbose)

    try:
        result = asyncio.run(tester.run_all_tests(args.provider))

        # 終了コード決定
        if "error" in result:
            sys.exit(1)

        summary = result.get("summary", {})
        if summary.get("success", 0) == 0:
            sys.exit(1)  # 全プロバイダー失敗

        sys.exit(0)  # 正常終了

    except KeyboardInterrupt:
        print("\n⚠️ テストが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
