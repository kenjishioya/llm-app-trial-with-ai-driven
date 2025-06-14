"""
Azure Key Vault統合サービス
Phase 1.5D3: Key Vault統合準備
"""

from typing import Optional, Dict, Any
import asyncio
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
import structlog

logger = structlog.get_logger(__name__)


class KeyVaultService:
    """Azure Key Vault統合サービス"""

    def __init__(
        self,
        vault_url: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ):
        """
        Key Vaultサービス初期化

        Args:
            vault_url: Key Vault URL
            client_id: Azure クライアントID（オプション）
            client_secret: Azure クライアントシークレット（オプション）
            tenant_id: Azure テナントID（オプション）
        """
        self.vault_url = vault_url

        # 認証情報が提供された場合はClientSecretCredential、
        # そうでなければDefaultAzureCredentialを使用
        if client_id and client_secret and tenant_id:
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
            logger.info("🔐 Key Vault: ClientSecretCredential使用")
        else:
            self.credential = DefaultAzureCredential()
            logger.info("🔐 Key Vault: DefaultAzureCredential使用")

        self.client = SecretClient(vault_url=vault_url, credential=self.credential)

    async def get_secret(self, secret_name: str) -> Optional[str]:
        """
        シークレットを取得

        Args:
            secret_name: シークレット名

        Returns:
            str: シークレット値、見つからない場合はNone

        Raises:
            Exception: Key Vault接続エラー
        """
        try:
            # Key Vault操作は同期なので、別スレッドで実行
            secret = await asyncio.to_thread(self.client.get_secret, secret_name)
            logger.info(f"✅ シークレット取得成功: {secret_name}")
            return str(secret.value) if secret.value is not None else None

        except ResourceNotFoundError:
            logger.warning(f"⚠️  シークレットが見つかりません: {secret_name}")
            return None

        except HttpResponseError as e:
            logger.error(f"❌ Key Vault HTTPエラー: {e.status_code} - {e.message}")
            raise Exception(f"Key Vault access error: {e.status_code}")

        except Exception as e:
            logger.error(f"❌ Key Vault接続エラー: {str(e)}")
            raise Exception(f"Key Vault connection failed: {str(e)}")

    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        シークレットを設定

        Args:
            secret_name: シークレット名
            secret_value: シークレット値

        Returns:
            bool: 成功時True

        Raises:
            Exception: Key Vault接続エラー
        """
        try:
            await asyncio.to_thread(self.client.set_secret, secret_name, secret_value)
            logger.info(f"✅ シークレット設定成功: {secret_name}")
            return True

        except HttpResponseError as e:
            logger.error(f"❌ Key Vault HTTPエラー: {e.status_code} - {e.message}")
            raise Exception(f"Key Vault access error: {e.status_code}")

        except Exception as e:
            logger.error(f"❌ Key Vault設定エラー: {str(e)}")
            raise Exception(f"Key Vault set failed: {str(e)}")

    async def list_secrets(self) -> Dict[str, Any]:
        """
        シークレット一覧を取得

        Returns:
            Dict[str, Any]: シークレット一覧情報
        """
        try:
            # すべてのシークレットプロパティを取得
            secret_properties = await asyncio.to_thread(
                lambda: list(self.client.list_properties_of_secrets())
            )

            secrets_info = {}
            for secret_property in secret_properties:
                secrets_info[secret_property.name] = {
                    "enabled": secret_property.enabled,
                    "created_on": (
                        secret_property.created_on.isoformat()
                        if secret_property.created_on
                        else None
                    ),
                    "updated_on": (
                        secret_property.updated_on.isoformat()
                        if secret_property.updated_on
                        else None
                    ),
                }

            logger.info(f"✅ シークレット一覧取得成功: {len(secrets_info)}個")
            return secrets_info

        except Exception as e:
            logger.error(f"❌ シークレット一覧取得エラー: {str(e)}")
            raise Exception(f"Key Vault list failed: {str(e)}")

    async def delete_secret(self, secret_name: str) -> bool:
        """
        シークレットを削除

        Args:
            secret_name: シークレット名

        Returns:
            bool: 成功時True
        """
        try:
            await asyncio.to_thread(self.client.begin_delete_secret, secret_name)
            logger.info(f"✅ シークレット削除開始: {secret_name}")
            return True

        except ResourceNotFoundError:
            logger.warning(f"⚠️  削除対象シークレットが見つかりません: {secret_name}")
            return False

        except Exception as e:
            logger.error(f"❌ シークレット削除エラー: {str(e)}")
            raise Exception(f"Key Vault delete failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Key Vault接続ヘルスチェック

        Returns:
            Dict[str, Any]: ヘルスチェック結果
        """
        try:
            # テスト用シークレットを取得してみる（存在しなくても良い）
            test_secret_name = "health-check-test"  # pragma: allowlist secret
            start_time = asyncio.get_event_loop().time()

            try:
                await self.get_secret(test_secret_name)
            except Exception:
                # ヘルスチェックなので、シークレットが存在しなくても問題なし
                pass

            end_time = asyncio.get_event_loop().time()
            response_time = round((end_time - start_time) * 1000, 2)

            return {
                "status": "healthy",
                "vault_url": self.vault_url,
                "response_time_ms": response_time,
                "credential_type": type(self.credential).__name__,
                "timestamp": asyncio.get_event_loop().time(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "vault_url": self.vault_url,
                "error": str(e),
                "credential_type": type(self.credential).__name__,
                "timestamp": asyncio.get_event_loop().time(),
            }


async def create_keyvault_service(
    vault_url: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> Optional[KeyVaultService]:
    """
    Key Vaultサービスファクトリー

    Args:
        vault_url: Key Vault URL
        client_id: Azure クライアントID
        client_secret: Azure クライアントシークレット
        tenant_id: Azure テナントID

    Returns:
        KeyVaultService: Key Vaultサービス、設定不備の場合はNone
    """
    if not vault_url:
        logger.warning("⚠️  Key Vault URL未設定、Key Vault統合をスキップします")
        return None

    try:
        service = KeyVaultService(
            vault_url=vault_url,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )

        # 接続テスト
        health = await service.health_check()
        if health["status"] == "healthy":
            logger.info("✅ Key Vault接続確認完了")
            return service
        else:
            logger.error(
                f"❌ Key Vault接続失敗: {health.get('error', 'Unknown error')}"
            )
            return None

    except Exception as e:
        logger.error(f"❌ Key Vaultサービス作成失敗: {str(e)}")
        return None
