# 0003 – GraphQL 採用（REST ではなく）

*Status*: **Accepted**
*Date*: 2025-06-03

## 背景

* QRAI は **チャット UI + RAG ストリーミング** を中核とし、モバイル展開や将来の画面追加を前提にしている。
* 質問応答ごとに「欲しいフィールド」がクライアント側で頻繁に変わる見込み。
* API 仕様も MVP → Premium へ段階的に拡張予定で **エンドポイントの変化が早い**。

## 決定

* 外部クライアント（Next.js UI、モバイル）との通信は **GraphQL (Strawberry)** を正式 API とする。
* REST は `/health`, `/openapi.json` のみ最低限残す。

## 根拠 / 代替案比較

| 案                    | メリット                                                    | デメリット                       | 結論                               |
| -------------------- | ------------------------------------------------------- | --------------------------- | -------------------------------- |
| **REST (エンドポイント分割)** | 実装が簡単、学習済みメンバー多い                                        | オーバーフェッチ、N+1 呼び出し、バージョン分裂   | *却下* – RAG ストリーミングで 3 連続呼び出しが非効率 |
| **gRPC + Protobuf**  | 型安全・高速                                                  | ブラウザから直呼びは厳しい、DevOps ツール少なめ | *未採用* – ブラウザ SSE と相性△            |
| **GraphQL**          | オーバー／アンダーフェッチ回避、1 エンドポイント、型自動生成、Subscription で SSE 標準対応 | スキーマ学習コスト、キャッシュ工夫要          | **採用** – 学習コスト < 開発スピード向上        |

> **要約** — *チャット＋RAG でストリーミング・モバイル拡張を視野・API 変化が早い* プロダクトでは **GraphQL の追加メリットが学習コストを上回る** と判断。

## 影響範囲

* **backend/**: FastAPI + Strawberry GraphQL Router を実装、SSE 用 `@stream` 拡張。
* **frontend/**: `@graphql-codegen` で TypeScript 型生成。
* **docs/api\_spec.md** にスキーマ Snapshot を更新。
* **CI**: `graphql-schema-linter` を追加し breaking change を検出。

## フォローアップ

* キャッシュ戦略：Apollo Client InMemoryCache + SWR fallback を検証。
* エラーフォーマット：REST 互換が欲しい場合 [GraphQL over HTTP](https://graphql.org/learn/serving-over-http/) 仕様に準拠。
