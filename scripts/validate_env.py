#!/usr/bin/env python3
"""
Phase 1.5D2: 環境設定検証スクリプト

環境変数とアプリケーション設定の検証を行います。
CI/CD、デプロイ前、トラブルシューティング時に使用。

使用方法:
    python scripts/validate_env.py [--environment ENV] [--detailed] [--fix-suggestions]

例:
    python scripts/validate_env.py --environment production --detailed
    python scripts/validate_env.py --fix-suggestions
"""

import argparse
import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from config import Settings, validate_environment
    from pydantic import ValidationError
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("backend/config.py が正しく設定されているか確認してください")
    sys.exit(1)


# ログ設定
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """環境設定検証クラス"""

    def __init__(self, target_environment: Optional[str] = None):
        self.target_environment = target_environment
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info: List[str] = []

    def log_issue(
        self, category: str, field: str, message: str, severity: str = "error"
    ):
        """問題を記録"""
        issue = {
            "category": category,
            "field": field,
            "message": message,
            "severity": severity,
        }

        if severity == "error":
            self.issues.append(issue)
        elif severity == "warning":
            self.warnings.append(issue)

    def validate_file_access(self) -> bool:
        """設定ファイルアクセス検証"""
        logger.info("📂 設定ファイルアクセス検証")

        success = True

        # .env ファイル確認
        env_files = [".env", ".env.development", ".env.test", ".env.production"]

        for env_file in env_files:
            env_path = project_root / env_file

            if env_path.exists():
                try:
                    with open(env_path, "r") as f:
                        content = f.read()
                    self.info.append(f"✅ {env_file}: {len(content)} 文字")
                except Exception as e:
                    self.log_issue("file_access", env_file, f"読み取り失敗: {e}")
                    success = False
            else:
                if env_file == ".env.sample":
                    self.log_issue(
                        "file_access",
                        env_file,
                        "サンプルファイルが存在しません",
                        "warning",
                    )
                elif (
                    env_file != ".env.production"
                ):  # 本番環境ファイルは存在しなくても良い
                    self.info.append(f"ℹ️  {env_file}: 存在しません")

        return success

    def validate_basic_config(self) -> Optional[Settings]:
        """基本設定検証"""
        logger.info("⚙️  基本設定検証")

        try:
            # 環境変数を一時的に設定
            if self.target_environment:
                os.environ["ENVIRONMENT"] = self.target_environment

            settings = validate_environment()

            self.info.append(f"✅ 環境: {settings.environment}")
            self.info.append(f"✅ アプリ: {settings.app_name} v{settings.app_version}")

            return settings

        except ValidationError as e:
            logger.error("❌ 設定検証エラー:")
            for error in e.errors():
                field = (
                    ".".join(str(loc) for loc in error["loc"])
                    if error["loc"]
                    else "unknown"
                )
                self.log_issue("validation", field, error["msg"])
            return None

        except Exception as e:
            self.log_issue("basic_config", "general", f"設定読み込みエラー: {e}")
            return None

    def validate_database_config(self, settings: Settings) -> bool:
        """データベース設定検証"""
        logger.info("💾 データベース設定検証")

        success = True

        # URL形式検証
        try:
            db_info = settings.get_database_info()

            if db_info["scheme"]:
                self.info.append(f"✅ DB種別: {db_info['scheme']}")
            else:
                self.log_issue("database", "url", "データベースURLの形式が不正です")
                success = False

            # PostgreSQL設定確認
            if db_info["scheme"] == "postgresql+asyncpg":
                if not db_info["hostname"]:
                    self.log_issue(
                        "database", "hostname", "PostgreSQLホスト名が設定されていません"
                    )
                    success = False
                if not db_info["database"]:
                    self.log_issue(
                        "database", "database", "データベース名が設定されていません"
                    )
                    success = False

                self.info.append(
                    f"✅ PostgreSQL: {db_info['hostname']}:{db_info['port']}/{db_info['database']}"
                )

            # SQLite設定確認
            elif db_info["scheme"] == "sqlite+aiosqlite":
                self.info.append("✅ SQLite: ローカルファイル")

        except Exception as e:
            self.log_issue("database", "parsing", f"データベース設定解析エラー: {e}")
            success = False

        # 接続プール設定確認
        if settings.db_pool_size < 1:
            self.log_issue(
                "database", "pool_size", "接続プールサイズが小さすぎます", "warning"
            )
        elif settings.db_pool_size > 50:
            self.log_issue(
                "database", "pool_size", "接続プールサイズが大きすぎます", "warning"
            )
        else:
            self.info.append(
                f"✅ 接続プール: {settings.db_pool_size}-{settings.db_pool_size + settings.db_max_overflow}"
            )

        return success

    def validate_api_keys(self, settings: Settings) -> bool:
        """APIキー設定検証"""
        logger.info("🔑 APIキー設定検証")

        success = True
        api_status = settings.validate_api_keys()

        # 各APIキーの状況確認
        for api_name, is_configured in api_status.items():
            if is_configured:
                self.info.append(f"✅ {api_name.upper()}: 設定済み")
            else:
                severity = (
                    "error"
                    if settings.is_production() and api_name == "openrouter"
                    else "warning"
                )
                self.log_issue(
                    "api_keys",
                    api_name,
                    f"{api_name.upper()} APIキーが設定されていません",
                    severity,
                )
                if severity == "error":
                    success = False

        # 本番環境特別チェック
        if settings.is_production():
            if not settings.openrouter_api_key:
                self.log_issue(
                    "api_keys", "openrouter", "本番環境では必須のAPIキーです"
                )
                success = False

        # 開発環境推奨チェック
        elif settings.is_development():
            if not any(api_status.values()):
                self.log_issue(
                    "api_keys",
                    "general",
                    "開発環境でもAPIキー設定を推奨します",
                    "warning",
                )

        return success

    def validate_security_config(self, settings: Settings) -> bool:
        """セキュリティ設定検証"""
        logger.info("🛡️  セキュリティ設定検証")

        success = True

        # JWT設定確認
        if len(settings.jwt_secret_key) < 32:
            self.log_issue(
                "security",
                "jwt_secret",
                "JWTシークレットキーが短すぎます（32文字以上推奨）",
            )
            success = False
        else:
            self.info.append("✅ JWT: 適切な長さのシークレットキー")

        # セッション設定確認
        if len(settings.session_secret_key) < 32:
            self.log_issue(
                "security",
                "session_secret",
                "セッションシークレットキーが短すぎます（32文字以上推奨）",
            )
            success = False
        else:
            self.info.append("✅ セッション: 適切な長さのシークレットキー")

        # 本番環境セキュリティチェック
        if settings.is_production():
            if settings.debug:
                self.log_issue(
                    "security", "debug", "本番環境でデバッグモードが有効です"
                )
                success = False

            if "localhost" in settings.allowed_origins:
                self.log_issue(
                    "security",
                    "cors",
                    "本番環境でlocalhostが許可されています",
                    "warning",
                )

            # デフォルトキーチェック
            default_keys = [
                "dev-jwt-secret-change-in-production",
                "dev-session-secret-change-in-production",
            ]
            if settings.jwt_secret_key in default_keys:
                self.log_issue(
                    "security",
                    "jwt_secret",
                    "本番環境でデフォルトJWTキーが使用されています",
                )
                success = False

            if settings.session_secret_key in default_keys:
                self.log_issue(
                    "security",
                    "session_secret",
                    "本番環境でデフォルトセッションキーが使用されています",
                )
                success = False

        return success

    def validate_network_config(self, settings: Settings) -> bool:
        """ネットワーク設定検証"""
        logger.info("🌐 ネットワーク設定検証")

        success = True

        # ポート番号確認
        if 1 <= settings.port <= 65535:
            self.info.append(f"✅ ポート: {settings.port}")
        else:
            self.log_issue("network", "port", f"無効なポート番号: {settings.port}")
            success = False

        # CORS設定確認
        origins = settings.get_allowed_origins_list()
        self.info.append(f"✅ CORS許可オリジン: {len(origins)}個")

        for origin in origins:
            if not origin.startswith(("http://", "https://")):
                self.log_issue(
                    "network", "cors", f"無効なオリジン形式: {origin}", "warning"
                )

        # URL設定確認
        for url_field, url_value in [
            ("frontend_url", settings.frontend_url),
            ("backend_url", settings.backend_url),
        ]:
            if url_value and not url_value.startswith(("http://", "https://")):
                self.log_issue("network", url_field, f"無効なURL形式: {url_value}")
                success = False
            else:
                self.info.append(f"✅ {url_field}: {url_value}")

        return success

    def generate_fix_suggestions(
        self, settings: Optional[Settings] = None
    ) -> List[str]:
        """修正提案生成"""
        suggestions = []

        if self.issues:
            suggestions.append("🔧 修正が必要な問題:")
            suggestions.append("")

            for issue in self.issues:
                category = issue["category"]
                field = issue["field"]
                message = issue["message"]

                suggestions.append(f"❌ [{category.upper()}] {field}: {message}")

                # 具体的な修正提案
                if category == "api_keys" and "設定されていません" in message:
                    api_name = field.upper()
                    suggestions.append(
                        f"   💡 .env.developmentに{api_name}_API_KEY=your_key_hereを追加"
                    )

                elif category == "security" and "短すぎます" in message:
                    suggestions.append(
                        "   💡 openssl rand -base64 32 でランダムキーを生成"
                    )

                elif category == "database" and "ホスト名" in message:
                    suggestions.append(
                        "   💡 DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname を設定"  # pragma: allowlist secret
                    )

                suggestions.append("")

        if self.warnings:
            suggestions.append("⚠️  改善推奨事項:")
            suggestions.append("")

            for warning in self.warnings:
                suggestions.append(
                    f"⚠️  [{warning['category'].upper()}] {warning['field']}: {warning['message']}"
                )

        return suggestions

    def run_validation(
        self, detailed: bool = False, fix_suggestions: bool = False
    ) -> bool:
        """包括的検証実行"""
        logger.info("🔍 QRAI Phase 1.5 環境設定検証開始")
        logger.info("=" * 50)

        all_success = True

        # 1. ファイルアクセス検証
        if not self.validate_file_access():
            all_success = False

        # 2. 基本設定検証
        settings = self.validate_basic_config()
        if not settings:
            all_success = False
            logger.error("❌ 基本設定検証失敗、以降の検証をスキップします")
            return False

        # 3. 詳細検証
        if not self.validate_database_config(settings):
            all_success = False

        if not self.validate_api_keys(settings):
            all_success = False

        if not self.validate_security_config(settings):
            all_success = False

        if not self.validate_network_config(settings):
            all_success = False

        # 結果表示
        logger.info("=" * 50)

        if detailed or self.info:
            logger.info("ℹ️  設定詳細:")
            for info in self.info:
                logger.info(f"  {info}")
            logger.info("")

        if self.warnings:
            logger.info("⚠️  警告:")
            for warning in self.warnings:
                logger.warning(
                    f"  [{warning['category'].upper()}] {warning['field']}: {warning['message']}"
                )
            logger.info("")

        if self.issues:
            logger.error("❌ エラー:")
            for issue in self.issues:
                logger.error(
                    f"  [{issue['category'].upper()}] {issue['field']}: {issue['message']}"
                )
            logger.info("")

        # 修正提案
        if fix_suggestions and (self.issues or self.warnings):
            suggestions = self.generate_fix_suggestions(settings)
            logger.info("\n".join(suggestions))

        # 最終結果
        if all_success:
            logger.info("✅ 環境設定検証完了: すべて正常")
        else:
            logger.error(f"❌ 環境設定検証失敗: {len(self.issues)}個のエラー")

        logger.info("=" * 50)
        return all_success


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="QRAI Phase 1.5 環境設定検証",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python scripts/validate_env.py                           # 基本検証
  python scripts/validate_env.py --detailed               # 詳細情報表示
  python scripts/validate_env.py --environment production # 本番環境として検証
  python scripts/validate_env.py --fix-suggestions        # 修正提案表示
        """,
    )

    parser.add_argument(
        "--environment",
        "-e",
        choices=["development", "test", "staging", "production"],
        help="検証対象環境",
    )

    parser.add_argument("--detailed", "-d", action="store_true", help="詳細情報を表示")

    parser.add_argument(
        "--fix-suggestions", "-f", action="store_true", help="修正提案を表示"
    )

    parser.add_argument(
        "--json-output", "-j", help="JSON形式で結果を出力するファイルパス"
    )

    args = parser.parse_args()

    # 検証実行
    validator = EnvironmentValidator(args.environment)
    success = validator.run_validation(
        detailed=args.detailed, fix_suggestions=args.fix_suggestions
    )

    # JSON出力
    if args.json_output:
        result = {
            "success": success,
            "environment": args.environment,
            "issues": validator.issues,
            "warnings": validator.warnings,
            "info": validator.info,
        }

        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"📄 結果をJSONで出力: {args.json_output}")

    # 終了コード
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
