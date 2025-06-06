# 0001 – RAG パターン採用

*Status*: **Accepted**
*Date*: 2025‑06‑03

## 背景

* 社員からの質問に対し、**引用付きで正確な回答** を返すことがプロダクト価値の中心。
* GPT‑4o のみの生成では “幻覚 (Hallucination)” が発生しやすく、資料ソースの提示も困難。
* ナレッジは常に更新されるため、LLM のファインチューニングを頻繁に行うのはコスト・運用負荷ともに高い。

## 決定

* **Retrieval‑Augmented Generation (RAG)** をコアアーキテクチャとして採用し、質問ごとに以下フローで応答する。

  1. Azure AI Search でドキュメントをトップ *k* (既定 3) 取得
  2. スニペットをプロンプトへ注入し GPT‑4o へ送信
  3. 回答に引用番号／リンクを付与

## 根拠・代替案

| 代替                            | 理由      | 却下理由                            |
| ----------------------------- | ------- | ------------------------------- |
| **LLM 単独生成**                  | 実装が最も簡単 | 引用なし・幻覚リスク高、コンプラ要件を満たさない        |
| **GPT ファインチューニング**            | 回答品質が安定 | ドキュメント更新のたび再学習が必要、無料枠外コスト大      |
| **外部 Web 検索 (SerpAPI) + LLM** | 最新情報反映  | 社内クローズドドキュメントには不向き、セキュリティ考慮が増える |

RAG は **動的ドキュメント追加** に強く、Microsoft Learn や LangChain OSS が充実していて実装負荷が低い。 ([learn.microsoft.com](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview))

## 影響範囲

* **アーキテクチャ**: RagService コンポーネントを追加、AI Search インデックス構築が前提。
* **データモデル**: ドキュメント & ベクトルストア用テーブル (AI Search) が必要。
* **コスト**: AI Search Free F1 を使用、GPT トークン数はスニペット分増加する。

## フォローアップ

* `top_k` の最適値チューニング → p95 応答時間と回答精度のバランス測定。
* 引用形式 (脚注 vs インライン) の UX A/B テスト。
* 評価指標 (F1 / faithfulness) を自動 QA に組み込む。
