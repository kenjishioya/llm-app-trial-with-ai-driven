"""
ログ設定ユーティリティ
Phase 1.5D4: ログ設定改善
"""

import logging
import logging.handlers
import sys
from typing import Optional, Dict, Any
from pathlib import Path

import structlog
from structlog.stdlib import LoggerFactory


def setup_logging(
    log_level: str = "INFO",
    environment: str = "development",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    structured: bool = True,
) -> None:
    """
    構造化ログ設定

    Args:
        log_level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: 環境識別子 (development, test, staging, production)
        log_file: ログファイルパス (指定時はファイル出力も行う)
        max_file_size: ログファイル最大サイズ (バイト)
        backup_count: ローテーション保持数
        structured: 構造化ログ使用フラグ
    """
    # ログレベル設定
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # ログフォーマット設定
    if environment == "production":
        # 本番環境: JSON形式
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
    else:
        # 開発・テスト環境: 読みやすい形式
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

    # ハンドラー設定
    handlers: list[logging.Handler] = []

    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # ファイルハンドラー (指定時)
    if log_file:
        # ログディレクトリ作成
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # ローテーションファイルハンドラー
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # 基本ログ設定
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True,  # 既存設定を上書き
    )

    # 構造化ログ設定
    if structured:
        configure_structlog(environment)

    # 特定ライブラリのログレベル調整
    configure_library_loggers(environment)


def configure_structlog(environment: str) -> None:
    """
    structlog設定

    Args:
        environment: 環境識別子
    """
    # プロセッサ設定
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
    ]

    # 環境別レンダラー
    if environment == "production":
        # 本番環境: JSON形式
        processors.append(structlog.processors.JSONRenderer())
    else:
        # 開発・テスト環境: 色付きコンソール
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                force_colors=environment != "test",  # テスト時は色無し
            )
        )

    # structlog設定
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def configure_library_loggers(environment: str) -> None:
    """
    外部ライブラリのログレベル調整

    Args:
        environment: 環境識別子
    """
    # うるさいライブラリのログレベル調整
    noisy_loggers = {
        "azure.core.pipeline.policies.http_logging_policy": logging.WARNING,
        "azure.identity": logging.WARNING,
        "azure.keyvault": logging.INFO,
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "urllib3": logging.WARNING,
        "sqlalchemy.engine": (
            logging.INFO if environment == "development" else logging.WARNING
        ),
        "sqlalchemy.pool": logging.WARNING,
        "alembic": logging.INFO,
    }

    for logger_name, level in noisy_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


class QraiLogger:
    """QRAI専用ログ出力クラス"""

    def __init__(self, name: str):
        """
        ロガー初期化

        Args:
            name: ロガー名（通常は__name__）
        """
        self.logger = structlog.get_logger(name)

    def debug(self, msg: str, **kwargs) -> None:
        """デバッグログ出力"""
        self.logger.debug(msg, **kwargs)

    def info(self, msg: str, **kwargs) -> None:
        """情報ログ出力"""
        self.logger.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        """警告ログ出力"""
        self.logger.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs) -> None:
        """エラーログ出力"""
        self.logger.error(msg, **kwargs)

    def critical(self, msg: str, **kwargs) -> None:
        """クリティカルログ出力"""
        self.logger.critical(msg, **kwargs)

    def bind(self, **kwargs) -> "QraiLogger":
        """
        コンテキスト情報をバインド

        Args:
            **kwargs: コンテキスト情報

        Returns:
            QraiLogger: 新しいロガーインスタンス
        """
        new_logger = QraiLogger(self.logger.name)
        new_logger.logger = self.logger.bind(**kwargs)
        return new_logger


def get_logger(name: str) -> QraiLogger:
    """
    QRAIロガー取得

    Args:
        name: ロガー名

    Returns:
        QraiLogger: ロガーインスタンス
    """
    return QraiLogger(name)


def create_log_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    ログ用コンテキスト情報作成

    Args:
        user_id: ユーザーID
        session_id: セッションID
        request_id: リクエストID
        **kwargs: 追加コンテキスト

    Returns:
        Dict[str, Any]: コンテキスト情報
    """
    context = {}

    if user_id:
        context["user_id"] = user_id
    if session_id:
        context["session_id"] = session_id
    if request_id:
        context["request_id"] = request_id

    context.update(kwargs)
    return context


def setup_production_logging(
    app_name: str = "qrai",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
) -> None:
    """
    本番環境用ログ設定

    Args:
        app_name: アプリケーション名
        log_level: ログレベル
        log_file: ログファイルパス
    """
    if not log_file:
        log_file = f"/var/log/{app_name}/{app_name}.log"

    setup_logging(
        log_level=log_level,
        environment="production",
        log_file=log_file,
        max_file_size=50 * 1024 * 1024,  # 50MB
        backup_count=10,
        structured=True,
    )


def setup_development_logging(log_level: str = "DEBUG") -> None:
    """
    開発環境用ログ設定

    Args:
        log_level: ログレベル
    """
    setup_logging(
        log_level=log_level,
        environment="development",
        structured=True,
    )


def setup_test_logging() -> None:
    """テスト環境用ログ設定"""
    setup_logging(
        log_level="WARNING",  # テスト時は警告以上のみ
        environment="test",
        structured=True,
    )
