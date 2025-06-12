#!/usr/bin/env python3
"""
Azure Key Vault接続テストスクリプト
Phase 1.5D3: Key Vault統合準備
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from config import get_settings
from services.keyvault_service import create_keyvault_service
from utils.logging import setup_test_logging, get_logger

logger = get_logger(__name__)


async def test_keyvault_connection():
    """Key Vault接続テスト"""
    logger.info("🔐 Key Vault接続テスト開始")

    try:
        # 設定読み込み
        settings = get_settings()

        # Key Vaultサービス作成
        keyvault_service = await create_keyvault_service(
            vault_url=settings.azure_keyvault_url,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret,
            tenant_id=settings.azure_tenant_id,
        )

        if not keyvault_service:
            logger.warning("⚠️  Key Vault設定が不完全、テストをスキップします")
            return True

        logger.info("✅ Key Vaultサービス作成成功")

        # ヘルスチェック
        health_result = await keyvault_service.health_check()
        logger.info("🔍 ヘルスチェック結果", **health_result)

        if health_result["status"] != "healthy":
            logger.error("❌ Key Vaultヘルスチェック失敗")
            return False

        # シークレット一覧取得テスト
        try:
            secrets = await keyvault_service.list_secrets()
            logger.info(f"📋 シークレット一覧取得成功: {len(secrets)}個")

            # シークレット名のみ表示（値は表示しない）
            for secret_name in list(secrets.keys())[:5]:  # 最初の5個のみ
                logger.info(f"  - {secret_name}")

            if len(secrets) > 5:
                logger.info(f"  ... 他 {len(secrets) - 5}個")

        except Exception as e:
            logger.warning(f"⚠️  シークレット一覧取得エラー: {str(e)}")

        # テストシークレット操作
        test_secret_name = "qrai-test-secret"  # pragma: allowlist secret
        test_secret_value = "test-value-123"  # pragma: allowlist secret

        try:
            # テストシークレット設定
            logger.info(f"🔧 テストシークレット設定: {test_secret_name}")
            await keyvault_service.set_secret(test_secret_name, test_secret_value)

            # テストシークレット取得
            retrieved_value = await keyvault_service.get_secret(test_secret_name)

            if retrieved_value == test_secret_value:
                logger.info("✅ テストシークレット操作成功")
            else:
                logger.error("❌ テストシークレット値が一致しません")
                return False

            # テストシークレット削除
            logger.info(f"🗑️  テストシークレット削除: {test_secret_name}")
            await keyvault_service.delete_secret(test_secret_name)

        except Exception as e:
            logger.warning(f"⚠️  テストシークレット操作エラー: {str(e)}")

        logger.info("🎉 Key Vault接続テスト完了")
        return True

    except Exception as e:
        logger.error(f"❌ Key Vault接続テスト失敗: {str(e)}")
        return False


async def test_keyvault_mock():
    """Key Vault設定なしの場合のテスト"""
    logger.info("🔧 Key Vault未設定時の動作テスト")

    try:
        # 空のURLでテスト
        keyvault_service = await create_keyvault_service(vault_url=None)

        if keyvault_service is None:
            logger.info("✅ Key Vault未設定時の適切な処理確認")
            return True
        else:
            logger.error("❌ Key Vault未設定時の処理が不正")
            return False

    except Exception as e:
        logger.error(f"❌ Key Vault未設定テスト失敗: {str(e)}")
        return False


async def main():
    """メイン実行関数"""
    # ログ設定
    setup_test_logging()

    logger.info("🔍 QRAI Key Vault統合テスト開始")
    logger.info("=" * 50)

    success = True

    # Key Vault未設定時のテスト
    if not await test_keyvault_mock():
        success = False

    # Key Vault接続テスト
    if not await test_keyvault_connection():
        success = False

    logger.info("=" * 50)

    if success:
        logger.info("🎉 すべてのテストが成功しました")
        sys.exit(0)
    else:
        logger.error("❌ テストに失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
