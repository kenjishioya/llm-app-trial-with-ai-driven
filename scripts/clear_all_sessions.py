#!/usr/bin/env python3
"""
セッション全削除スクリプト（PostgreSQL対応）

使用方法:
    python scripts/clear_all_sessions.py

注意:
    - 全てのセッションとメッセージが削除されます
    - 実行前に確認プロンプトが表示されます
    - バックアップは作成されません
    - docker-compose環境のPostgreSQLに接続します
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ psycopg2がインストールされていません。")
    print("インストール方法: pip install psycopg2-binary")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenvがインストールされていません。")
    print("インストール方法: pip install python-dotenv")
    sys.exit(1)

# グローバル変数で環境変数読み込み状態を管理
_env_loaded = False

def load_environment():
    """環境変数を.env.developmentから読み込み"""
    global _env_loaded
    if _env_loaded:
        return

    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env.development"

    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 環境変数を読み込みました: {env_file}")
        _env_loaded = True
    else:
        print(f"⚠️  .env.developmentファイルが見つかりません: {env_file}")
        print("環境変数が設定されていることを確認してください。")


def get_database_config():
    """データベース接続設定を取得"""
    # .env.developmentから環境変数を読み込み（初回のみ）
    load_environment()

    config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', 'qrai_dev'),
        'user': os.getenv('POSTGRES_USER', 'qrai_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'qrai_password')
    }

    return config


def get_database_connection():
    """データベース接続を取得"""
    config = get_database_config()

    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ データベース接続エラー: {e}")
        print("docker-compose環境が起動していることを確認してください。")
        print("起動方法: docker-compose up -d")
        return None


def clear_all_sessions():
    """全てのセッションとメッセージを削除"""
    print("🗑️  セッション全削除スクリプト（PostgreSQL）")
    print("=" * 50)

    # 確認プロンプト
    confirm = input("⚠️  全てのセッションとメッセージが削除されます。続行しますか？ (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("❌ 削除をキャンセルしました。")
        return

    conn = get_database_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            # 現在のセッション数とメッセージ数を取得
            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            session_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM messages")
            message_count = cursor.fetchone()['count']

            print(f"📊 削除対象: セッション {session_count}件, メッセージ {message_count}件")

            if session_count == 0 and message_count == 0:
                print("✅ 削除対象のデータがありません。")
                return

            # 最終確認
            final_confirm = input(f"本当に削除しますか？ (DELETE と入力してください): ")
            if final_confirm != "DELETE":
                print("❌ 削除をキャンセルしました。")
                return

            # メッセージを削除（外部キー制約のため先に削除）
            if message_count > 0:
                print("🗑️  メッセージを削除中...")
                cursor.execute("DELETE FROM messages")
                print(f"✅ {message_count}件のメッセージを削除しました。")

            # セッションを削除
            if session_count > 0:
                print("🗑️  セッションを削除中...")
                cursor.execute("DELETE FROM sessions")
                print(f"✅ {session_count}件のセッションを削除しました。")

            # コミット
            conn.commit()
            print("✅ 全ての削除処理が完了しました。")

    except psycopg2.Error as e:
        print(f"❌ データベースエラーが発生しました: {e}")
        conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def show_current_sessions():
    """現在のセッション一覧を表示"""
    conn = get_database_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            # セッション一覧を取得
            cursor.execute("SELECT id, title, created_at FROM sessions ORDER BY created_at DESC")
            sessions = cursor.fetchall()

            if not sessions:
                print("📝 現在セッションはありません。")
                return

            print("📝 現在のセッション一覧:")
            print("-" * 80)
            for sess in sessions:
                session_id = sess['id'][:8] + "..." if len(sess['id']) > 8 else sess['id']
                title = sess['title'] or "無題"
                created_at = sess['created_at']
                print(f"ID: {session_id} | タイトル: {title} | 作成日: {created_at}")
            print("-" * 80)
            print(f"合計: {len(sessions)}件")

    except psycopg2.Error as e:
        print(f"❌ セッション一覧の取得でエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


def check_database_connection():
    """データベース接続を確認"""
    conn = get_database_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            # テーブルの存在確認
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('sessions', 'messages')
            """)
            tables = [row['table_name'] for row in cursor.fetchall()]

            if 'sessions' not in tables:
                print("❌ sessionsテーブルが見つかりません。")
                return False

            if 'messages' not in tables:
                print("❌ messagesテーブルが見つかりません。")
                return False

            print("✅ データベース接続とテーブル確認が完了しました。")
            return True

    except psycopg2.Error as e:
        print(f"❌ データベース接続エラー: {e}")
        return False
    finally:
        conn.close()


def main():
    """メイン処理"""
    print("🔍 PostgreSQLデータベース接続を確認中...")

    # データベース接続確認
    if not check_database_connection():
        print("❌ データベースに接続できません。")
        print("docker-compose環境が起動していることを確認してください。")
        sys.exit(1)

    print()

    # コマンドライン引数の処理
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        show_current_sessions()
        return

    # 現在のセッション一覧を表示
    show_current_sessions()
    print()

    # 削除処理を実行
    clear_all_sessions()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ 処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
