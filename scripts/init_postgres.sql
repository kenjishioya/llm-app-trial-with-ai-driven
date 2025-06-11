-- PostgreSQL初期化スクリプト
-- QRAI プロジェクト用データベース設定

-- 必要な拡張機能を有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 接続文字エンコーディング確認
SELECT current_setting('server_encoding') as server_encoding;

-- タイムゾーン設定
SET timezone = 'Asia/Tokyo';

-- ログ出力設定
-- CREATE SCHEMA IF NOT EXISTS logs;

-- インデックス用関数（将来の全文検索用）
-- CREATE INDEX IF NOT EXISTS idx_sessions_title_trgm ON sessions USING gin (title gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS idx_messages_content_trgm ON messages USING gin (content gin_trgm_ops);

-- ユーザーパスワードをSCRAM-SHA-256形式で再設定（認証方式統一）
-- 環境変数POSTGRES_PASSWORDを使用
\set password `echo $POSTGRES_PASSWORD`
ALTER USER qrai_user WITH PASSWORD :'password';

-- データベース設定完了メッセージ
\echo 'PostgreSQL database initialized for QRAI project'
\echo 'Database: qrai_dev'
\echo 'User: qrai_user (SCRAM-SHA-256 password set)'
\echo 'Extensions: uuid-ossp, pg_trgm'
\echo 'Timezone: Asia/Tokyo'
