# 0002 – Dev 環境は Azure 無料枠 (Free Tier) 限定

*Status*: **Accepted**
*Date*: 2025-06-03

## 背景

* 個人開発・PoC フェーズではコストを最小化し、**クレジット消費ゼロ** で継続開発できることが重要。
* チームメンバーが自分のサブスクリプションでも同じ手順で環境を再現できるようにしたい。
* Azure の Free SKU には AI Search F1、Static Web Apps Free、Cosmos DB Single Node Basic など主要サービスが揃っており、機能検証に十分。

## 決定

* **開発用サブスクリプションでは “無料枠のみ” を IaC 変数で強制** する。

  * `is_free = true` のときは各リソースの SKU／プロパティを Free 相当に固定。
  * CI で `is_free` が `false` に変わる PR は失敗させる。
* 有料 SKU が必要な検証は **別サブスクリプション（prod / premium）** で行う。

## 根拠・代替案

| 代替                              | 理由               | 却下理由                               |
| ------------------------------- | ---------------- | ---------------------------------- |
| **従量課金 (Pay‑As‑You‑Go) を許可**    | 柔軟に試せる           | ランダム課金で月数十ドル超のリスク、学習目的を外れる         |
| **Azure Sponsorship クレジット**     | コストゼロで Free 制限なし | 有効期限・残高に依存、全メンバーが取得できない            |
| **ローカルエミュレータ (Azurite, pg) 使用** | 完全オフライン          | OpenAI・AI Search など SaaS はエミュレータ無し |

## 影響範囲

* **IaC**: Terraform/Bicep で `sku = "free"` 条件分岐、OpenAI は `gpt-4o-mini`。
* **コード**: トークン・インデックスサイズを Free 制限 (50 MB) 内に収めるロジック。
* **CI**: `terraform plan` で課金 SKU が出たらエラー exit。

## フォローアップ

* Free 制限に近づいたら GitHub Cost Export でレポート。
* データ量 > 50 MB になったらドキュメント分割・古いセッション TTL 区切り。
* Premium 版検証 ADR (0003) 作成予定。
