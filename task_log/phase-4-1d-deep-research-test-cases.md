# Phase 4-1D Deep Research 動作確認テストケース

## 概要
LangGraph Deep Research機能の動作確認用テストケースです。
フロントエンドのDeep Researchアイコン（🔍）をクリックした際の期待動作を定義します。

## テスト環境
- フロントエンド: http://localhost:3000
- バックエンド: http://localhost:8000
- GraphQL Playground: http://localhost:8000/graphql

## テストケース

### 1. 基本的なDeep Research実行

#### 入力
```
質問: "Azure AI Searchの料金体系について教えてください"
Deep Research: ON（🔍アイコンをクリック）
```

#### 期待される動作フロー
1. **UI表示**
   - Deep Researchアイコンが押下状態になる
   - プログレスバーが表示される
   - 「Deep Research を開始しています...」メッセージ

2. **進捗表示（順次更新）**
   ```
   🔍 Deep Research を開始しています...
   📚 情報を検索中... (1/3)
   🔄 追加の情報収集が必要です
   📚 情報を検索中... (2/3)
   ✅ 十分な情報が収集されました
   📝 レポートを生成中...
   ✅ Deep Research が完了しました
   📊 レポート生成完了 (XXXX 文字)
   ```

3. **最終出力**
   - Markdownフォーマットの詳細レポート
   - 見出し構造（#, ##, ###）
   - 出典情報の明記
   - 参考文献リスト
   - レポート生成メタデータ

#### 期待されるレポート構造
```markdown
# Azure AI Searchの料金体系

## 概要
- 主要なポイントの要約

## 詳細分析
### 価格プラン
### 課金モデル
### コスト最適化

## 結論
- 質問に対する明確な回答

## 参考文献
- [出典1]: ソース名
- [出典2]: ソース名

---
**レポート生成情報**
- 生成日時: 2025-06-13 XX:XX:XX
- 使用ドキュメント数: X
- ユニークソース数: X
---
```

### 2. 情報不足時のDeep Research

#### 入力
```
質問: "2025年の新しいAI技術トレンド"
Deep Research: ON
```

#### 期待される動作
1. 最大検索回数（3回）まで検索を実行
2. 情報が不十分でも最終的にレポートを生成
3. 「情報が限定的である」旨の注記を含む

#### 期待される進捗表示
```
🔍 Deep Research を開始しています...
📚 情報を検索中... (1/3)
🔄 追加の情報収集が必要です
📚 情報を検索中... (2/3)
🔄 追加の情報収集が必要です
📚 情報を検索中... (3/3)
📝 レポートを生成中...
✅ Deep Research が完了しました
```

### 3. エラーハンドリングテスト

#### 入力
```
質問: ""（空文字）
Deep Research: ON
```

#### 期待される動作
1. バリデーションエラーの表示
2. 適切なエラーメッセージ
3. UIの正常な復帰

#### 期待されるエラー表示
```
❌ エラーが発生しました: 質問が入力されていません
```

### 4. 通常質問との比較テスト

#### 入力A（通常質問）
```
質問: "Azure AI Searchとは何ですか？"
Deep Research: OFF
```

#### 入力B（Deep Research）
```
質問: "Azure AI Searchとは何ですか？"
Deep Research: ON
```

#### 期待される違い
- **通常質問**: 簡潔な回答（1-2段落）
- **Deep Research**: 詳細なレポート（複数セクション、出典付き）

## UI要素の動作確認

### Deep Researchアイコン（🔍）
- **通常状態**: グレー、クリック可能
- **実行中**: 青色、ローディング表示
- **完了後**: グレーに戻る

### プログレスバー
- **表示タイミング**: Deep Research開始時
- **更新頻度**: 進捗メッセージと連動
- **完了時**: 100%表示後に非表示

### メッセージ表示
- **位置**: チャット画面内
- **スタイル**: システムメッセージとして区別
- **更新**: リアルタイムストリーミング

## GraphQL動作確認

### Mutation: deepResearch
```graphql
mutation {
  deepResearch(input: {
    sessionId: "session-uuid"
    question: "Azure AI Searchの料金体系について教えてください"
  }) {
    sessionId
    researchId
    streamUrl
    status
    message
  }
}
```

#### 期待レスポンス
```json
{
  "data": {
    "deepResearch": {
      "sessionId": "session-uuid",
      "researchId": "research-uuid",
      "streamUrl": "/graphql/stream/deep-research?id=research-uuid",
      "status": "started",
      "message": "Deep Research has been initiated"
    }
  }
}
```

### Subscription: streamDeepResearch
```graphql
subscription {
  streamDeepResearch(
    researchId: "research-uuid"
    sessionId: "session-uuid"
    question: "Azure AI Searchの料金体系について教えてください"
  ) {
    content
    researchId
    sessionId
    isComplete
    currentNode
    progressPercentage
  }
}
```

## パフォーマンス要件

### 応答時間
- **初期応答**: 1秒以内
- **進捗更新**: 2-5秒間隔
- **完了まで**: 30-60秒以内

### リソース使用量
- **メモリ**: 正常範囲内
- **CPU**: 高負荷時でも応答性維持
- **ネットワーク**: ストリーミング接続の安定性

## 既知の制限事項

1. **検索回数制限**: 最大3回まで
2. **レポート長制限**: 8000文字まで
3. **同時実行**: 1セッションあたり1つのDeep Researchのみ
4. **タイムアウト**: 5分で自動終了

## トラブルシューティング

### よくある問題
1. **プログレスバーが表示されない**
   - ブラウザの開発者ツールでWebSocket接続を確認

2. **進捗が更新されない**
   - バックエンドログでLangGraphの実行状況を確認

3. **レポートが生成されない**
   - LLMサービスの接続状況を確認

### デバッグ用ログ
```bash
# バックエンドログ確認
docker-compose logs -f backend

# フロントエンドコンソール確認
# ブラウザ開発者ツール > Console
```

## 成功基準

✅ **Phase 4-1D完了条件**
1. Deep Researchアイコンが正常に動作する
2. プログレスバーが適切に表示・更新される
3. 進捗メッセージがリアルタイムで表示される
4. 最終的に構造化されたレポートが生成される
5. エラー時に適切なメッセージが表示される
6. UIが正常な状態に復帰する

---
**作成日**: 2025-06-13
**更新日**: 2025-06-13
**テスト対象**: Phase 4-1D Deep Research UI Integration
