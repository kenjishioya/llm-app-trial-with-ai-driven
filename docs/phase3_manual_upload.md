# 📄 Phase 3 手動ドキュメントアップロード手順書
**Task 3-2B-2: Azure Portal アップロード手順書**

> **目的** — Azure Portal経由でドキュメントを手動アップロードし、AI Search インデックスに登録する手順を提供する。CLIスクリプトが使用できない場合や、管理者による直接操作が必要な場合に使用。

---

## 📋 概要

### アップロード方法の比較

| 方法 | 適用場面 | 難易度 | 自動化レベル |
|------|----------|--------|-------------|
| **CLIスクリプト** | 開発・テスト環境 | 低 | 完全自動 |
| **Azure Portal** | 本番環境・管理者操作 | 中 | 半自動 |
| **Azure Storage Explorer** | 大量ファイル・バッチ操作 | 中 | 手動 |

### 前提条件

- Azure Portal へのアクセス権限
- `qrai-storage-dev` Blob Storage への書き込み権限
- `qrai-search-dev` AI Search への管理権限
- サポートファイル形式: PDF, DOCX, TXT, Markdown

---

## 🔧 方法1: Azure Portal Blob Storage 直接アップロード

### Step 1: Azure Portal にアクセス

1. **Azure Portal** にログイン: https://portal.azure.com
2. **リソースグループ** `qrai-dev` を選択
3. **ストレージアカウント** `qraistoragedev` をクリック

### Step 2: Blob Storage コンテナーにアクセス

1. 左メニューから **「コンテナー」** を選択
2. **`documents`** コンテナーをクリック
3. 上部の **「アップロード」** ボタンをクリック

### Step 3: ファイルアップロード

1. **「ファイルの選択」** でアップロードするファイルを選択
2. **詳細設定** を展開（推奨）:
   ```
   BLOB の種類: ブロック BLOB
   ブロック サイズ: 4 MiB（デフォルト）
   アクセス層: ホット
   暗号化スコープ: (既定値)
   ```

3. **メタデータ** セクションで以下を追加:
   ```
   キー: uploaded_via     値: azure_portal
   キー: upload_date      値: 2025-06-12
   キー: content_type     値: application/pdf (ファイル形式に応じて)
   キー: uploader         値: [アップロード者名]
   ```

4. **「アップロード」** をクリック

### Step 4: アップロード確認

1. ファイルがコンテナー内に表示されることを確認
2. ファイルをクリックして **「プロパティ」** でメタデータを確認
3. **URL** をコピーして保存（後でAI Searchで使用）

---

## 🔍 方法2: AI Search インデックス手動登録

### Step 1: AI Search サービスにアクセス

1. Azure Portal で **AI Search サービス** `qrai-search-dev` を選択
2. 左メニューから **「インデックス」** を選択
3. **`qrai-documents-index`** をクリック

### Step 2: ドキュメント追加

1. 上部の **「ドキュメントの追加」** をクリック
2. **「JSON形式でアップロード」** を選択

### Step 3: JSON ドキュメント作成

以下のテンプレートを使用してJSONドキュメントを作成:

```json
{
  "value": [
    {
      "id": "doc_[UNIQUE_ID]_chunk_0",
      "document_id": "doc_[UNIQUE_ID]",
      "title": "ドキュメントタイトル",
      "content": "ドキュメントの内容テキスト（チャンク分割済み）",
      "file_name": "example.pdf",
      "source_url": "https://qraistoragedev.blob.core.windows.net/documents/example.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "content_type": "application/pdf",
      "chunk_index": 0,
      "chunk_count": 1,
      "chunk_overlap": 0,
      "start_char": 0,
      "end_char": 500,
      "text_length": 500,
      "created_at": "2025-06-12T00:00:00Z",
      "processed_at": "2025-06-12T00:00:00Z",
      "metadata": {
        "uploaded_via": "azure_portal",
        "uploader": "admin_user"
      }
    }
  ]
}
```

### Step 4: フィールド値の設定

| フィールド | 説明 | 例 |
|-----------|------|-----|
| `id` | 一意識別子 | `doc_20250612_001_chunk_0` |
| `document_id` | ドキュメントID | `doc_20250612_001` |
| `title` | ドキュメントタイトル | `Azure AI 導入ガイド` |
| `content` | テキスト内容 | `Azure AI サービスは...` |
| `file_name` | ファイル名 | `azure_ai_guide.pdf` |
| `source_url` | Blob Storage URL | `https://qraistoragedev.blob...` |
| `file_type` | ファイル形式 | `pdf`, `docx`, `txt` |
| `file_size` | ファイルサイズ（バイト） | `1024000` |

### Step 5: インデックス登録実行

1. JSON を **「ドキュメント」** テキストエリアに貼り付け
2. **「アップロード」** をクリック
3. **「成功」** メッセージを確認

---

## 🔍 方法3: Azure Storage Explorer 使用

### Step 1: Azure Storage Explorer インストール

1. **Azure Storage Explorer** をダウンロード: https://azure.microsoft.com/features/storage-explorer/
2. インストール後、Azure アカウントでサインイン

### Step 2: ストレージアカウント接続

1. **「アカウント管理」** → **「アカウントの追加」**
2. **「Azure 環境」** で適切な環境を選択
3. **「サインイン」** でAzureアカウント認証

### Step 3: ファイルアップロード

1. **「ストレージアカウント」** → **`qraistoragedev`** → **「Blob コンテナー」** → **`documents`**
2. **「アップロード」** → **「ファイルのアップロード」**
3. 複数ファイルを選択してバッチアップロード可能

### Step 4: メタデータ設定

1. アップロード後、ファイルを右クリック → **「プロパティ」**
2. **「メタデータ」** タブでキー・値ペアを追加
3. **「保存」** をクリック

---

## 🛠️ トラブルシューティング

### 問題1: アップロードが失敗する

**症状**: ファイルアップロード時にエラーが発生

**原因と対処法**:
- **権限不足**: ストレージアカウントの「ストレージ BLOB データ共同作成者」ロールを確認
- **ファイルサイズ制限**: 単一ファイル最大 5 TB、ブロック BLOB 制限を確認
- **ネットワーク問題**: 接続を確認し、VPN経由の場合は直接接続を試行

```bash
# 権限確認コマンド（Azure CLI）
az role assignment list --assignee [USER_EMAIL] --scope /subscriptions/[SUBSCRIPTION_ID]/resourceGroups/qrai-dev/providers/Microsoft.Storage/storageAccounts/qraistoragedev
```

### 問題2: AI Search インデックス登録エラー

**症状**: JSON ドキュメントアップロード時にエラー

**原因と対処法**:
- **JSON 形式エラー**: JSON Validator でフォーマットを確認
- **必須フィールド不足**: `id`, `content` フィールドが必須
- **データ型不一致**: `file_size` は数値、`created_at` は ISO 8601 形式

```json
// エラー例と修正
// ❌ 間違い
"file_size": "1024000"
"created_at": "2025/06/12"

// ✅ 正しい
"file_size": 1024000
"created_at": "2025-06-12T00:00:00Z"
```

### 問題3: 検索結果に表示されない

**症状**: アップロードしたドキュメントが検索で見つからない

**原因と対処法**:
- **インデックス更新遅延**: 5-10分待ってから再検索
- **content フィールド空**: テキスト内容が正しく設定されているか確認
- **インデックス状態確認**: AI Search の「インデックス」→「統計」で文書数を確認

```bash
# 検索テスト（Azure CLI）
az search query --service-name qrai-search-dev --index-name qrai-documents-index --search-text "テストキーワード"
```

### 問題4: 文字化けが発生

**症状**: 日本語ドキュメントで文字化け

**原因と対処法**:
- **エンコーディング問題**: UTF-8 エンコーディングを確認
- **アナライザー設定**: インデックスで `ja.microsoft` アナライザーが設定されているか確認
- **ファイル形式**: PDF の場合、テキスト抽出可能な形式か確認

---

## 📊 アップロード後の確認手順

### 1. Blob Storage 確認

```bash
# Azure CLI でファイル一覧確認
az storage blob list --container-name documents --account-name qraistoragedev --output table
```

### 2. AI Search インデックス確認

```bash
# インデックス統計確認
az search index show --service-name qrai-search-dev --index-name qrai-documents-index --query "documentCount"
```

### 3. 検索テスト

```bash
# 基本検索テスト
az search query --service-name qrai-search-dev --index-name qrai-documents-index --search-text "*" --top 5
```

### 4. RAG システム動作確認

1. **フロントエンド** でチャット画面にアクセス
2. アップロードしたドキュメントに関する質問を入力
3. **引用情報** にアップロードファイルが表示されることを確認

---

## 📋 チェックリスト

### アップロード前
- [ ] ファイル形式がサポート対象（PDF, DOCX, TXT, MD）
- [ ] ファイルサイズが制限内（< 100 MB 推奨）
- [ ] Azure Portal アクセス権限確認
- [ ] アップロード先コンテナー確認

### アップロード中
- [ ] 適切なメタデータ設定
- [ ] ファイル名の重複確認
- [ ] アップロード完了確認
- [ ] Blob URL 取得

### インデックス登録
- [ ] JSON フォーマット検証
- [ ] 必須フィールド設定
- [ ] 一意ID生成
- [ ] 登録成功確認

### 動作確認
- [ ] 検索結果表示確認
- [ ] RAG システム応答確認
- [ ] 引用情報表示確認
- [ ] 文字化け・エラーなし

---

## 🔗 関連リンク

- **Azure Portal**: https://portal.azure.com
- **Azure Storage Explorer**: https://azure.microsoft.com/features/storage-explorer/
- **Azure AI Search ドキュメント**: https://docs.microsoft.com/azure/search/
- **CLIアップロードスクリプト**: `scripts/upload_document.py`
- **システム設定**: `docs/environment_setup.md`

---

## 📞 サポート

### 技術的な問題
- **開発チーム**: 内部Slackチャンネル `#qrai-dev`
- **Azure サポート**: Azure Portal の「ヘルプとサポート」

### 緊急時対応
1. **CLIスクリプト使用**: `python scripts/upload_document.py --health-check`
2. **ログ確認**: Azure Portal の「監視」→「ログ」
3. **ロールバック**: 問題のあるドキュメントを削除

---

*最終更新: 2025-06-12*
*作成者: QRAI開発チーム*
*バージョン: 1.0*
