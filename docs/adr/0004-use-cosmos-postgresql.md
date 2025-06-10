# 0004 – Cosmos DB for PostgreSQL 採用

*Status*: **Accepted**
*Date*: 2025-06-03

## 背景

* セッション・メッセージ・Deep Researchノートを永続化する必要がある。
* チャット履歴とリサーチ結果の関係をリレーショナルで管理したい。
* 無料枠で利用可能で、PostgreSQL互換性があることが重要。
* 将来的にスケールアウトやマルチリージョン展開を考慮したい。

## 決定

* **Azure Cosmos DB for PostgreSQL** をメインデータベースとして採用。

  * PostgreSQL 16互換でSQLAlchemyが使用可能。
  * 単一ノード無料枠 (vCore 1, 32GB storage) でMVP要件を満たす。
  * 将来的にマルチノード分散への移行パスがある。

## 根拠・代替案

| 代替                        | 理由                    | 却下理由                                   |
| ------------------------- | --------------------- | -------------------------------------- |
| **Azure SQL Database**    | エンタープライズ標準、ツール豊富    | 無料枠なし (最小 DTU 10 で月額 $4.9~)、コスト制約に合わない |
| **PostgreSQL (Container)** | 完全無料、フルコントロール       | 永続化・バックアップ・HA を自前構築、運用負荷大              |
| **Cosmos DB (NoSQL)**     | マルチモデル、グローバル分散       | リレーショナルクエリが複雑、セッション-メッセージ関係の表現が困難   |
| **Azure Table Storage**   | 極安価、シンプル              | リレーショナル機能なし、複雑クエリ不可                    |

## 影響範囲

* **ORM**: SQLAlchemy async + Alembic migration。
* **データmodel**: `sessions`, `messages`, `research_notes` テーブル設計。
* **コスト**: 無料枠内で運用、容量監視が必要。
* **接続**: asyncpg ドライバー、connection pooling。

## フォローアップ

* 無料枠 32GB 上限に近づいたら古いセッションのTTL削除。
* パフォーマンス監視でクエリ最適化、必要に応じてインデックス追加。
* マルチノード分散が必要になったら 0007-scale-cosmos-multinode.md を作成。
