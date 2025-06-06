# 0005 – ストリーミングに SSE (Server-Sent Events) 採用

*Status*: **Accepted**
*Date*: 2025-06-03

## 背景

* LLM応答は生成に数秒〜数十秒かかるため、ユーザー体験向上のため**逐次表示**が必須。
* Deep Researchモードでは進行状況（Step 1/3など）をリアルタイムで表示したい。
* GraphQLとの統合性を保ちつつ、実装とデバッグの複雑性を最小化したい。
* モバイルブラウザでも安定動作することが望ましい。

## 決定

* **Server-Sent Events (SSE)** をストリーミング実装方式として採用。

  * FastAPI の `StreamingResponse` + `yield` でチャンク送信。
  * フロントエンドは `EventSource` API でリアルタイム受信。
  * GraphQL mutation でストリームURLを返し、SSE接続で実際のデータを送信。

## 根拠・代替案

| 代替                    | 理由                      | 却下理由                                        |
| --------------------- | ----------------------- | ------------------------------------------- |
| **WebSocket**         | 双方向通信、リアルタイム性が最高      | MVP では一方向で十分、接続状態管理が複雑、GraphQLとの統合が困難      |
| **HTTP Long Polling** | 実装が単純、すべてのクライアントで動作   | サーバーリソース効率が悪い、タイムアウト管理が煩雑                   |
| **GraphQL Subscription** | GraphQLエコシステム内で完結      | WebSocket必須、Strawberry GraphQLでの実装が複雑          |
| **定期的なREST API呼び出し** | 最もシンプル、デバッグ容易         | ユーザー体験が悪い（カクカクした表示）、サーバー負荷が高い（無駄なポーリング） |

SSEは**HTTP/2でのマルチプレキシング**に対応し、プロキシ・CDN通過も良好。GraphQL+SSEの組み合わせは実績も多い。

## 影響範囲

* **バックエンド**: FastAPI で `/stream/{message_id}` エンドポイント実装。
* **フロントエンド**: `EventSource` + React hooks でリアルタイム状態管理。
* **GraphQL**: mutation で `stream: String!` フィールドを返却。
* **エラーハンドリング**: SSE切断・再接続ロジックの実装。

## フォローアップ

* SSE接続数の監視（同時接続制限の設定）。
* モバイルブラウザでの接続安定性テスト。
* 将来的に双方向チャット機能が必要になったらWebSocketへの移行を検討（0008-upgrade-to-websocket.md）。 