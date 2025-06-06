# Cross‑Cutting Concerns – QRAI (MVP)

> **目的** — セキュリティ・運用・性能・コストなど、機能横断的（cross‑cutting）な要件と設計方針を 1 か所に集約し、実装者・運用者が抜け漏れなく確認できるハブとする。

---

## 1. 非機能要件一覧 (NFR)

詳細なテスト戦略については **[test_strategy.md](test_strategy.md)** を参照してください。

| カテゴリ       | ID     | 要件                            | 検証方法                                    |
| ---------- | ------ | ----------------------------- | --------------------------------------- |
| **性能**     | NFR‑01 | RAG 応答 p95 < **10 s**         | Locust / JMeter シナリオで 100 RPS 🡒 p95 計測 |
|            | NFR‑02 | Deep Research 完了 < **120 s**  | E2E テスト (`pytest`) でタイマー検証              |
| **可用性**    | NFR‑03 | 99.5 % (dev)                  | Azure Monitor SLO レポート                  |
| **スケール**   | NFR‑04 | Container App HPA: 1–3 レプリカ   | k6 負荷で自動スケール確認                          |
| **セキュリティ** | NFR‑05 | .env／Secrets を Git へ push しない | git‑secrets + CI fail                   |
| **コスト**    | NFR‑06 | 月額 \$5 以内 (dev)               | Azure Cost Mgmt アラート                    |

---

## 2. セキュリティ設計

### 2‑1 認証・認可 (MVP)

* **匿名でも使える**が、Azure AD OIDC トークンを送出可能にし将来 Auth Z 拡張に備える。
* GraphQL resolver で `user_id` をコンテキストへ詰め、セッションを **ユーザー別に分離**。

### 2‑2 機密情報管理

| 種別                  | 保管先                                     | アクセス                 |
| ------------------- | --------------------------------------- | -------------------- |
| OpenAI API Key      | **.env (dev)** / Azure Key Vault (prod) | AAD Managed Identity |
| AI Search Admin Key | KV シークレット                               | Terraform output 参照  |
| Postgres Password   | `.env` (dev)                            | Docker secrets mount |

### 2‑3 通信保護

* **HTTPS/TLS1.2+** で統一。Localhost では `insecureSkipVerify` 可。将来 prod で mTLS。
* LLM 呼び出しは HTTPS のみ。

### 2‑4 脅威モデリング箇条書き (STRIDE)

* **S**poofing → JWT/ADF による署名検証（将来）
* **T**ampering → HTTPS + Cosmos PG 暗号化 at‑rest
* **R**epudiation → Log Analytics + session_id
* **I**nformation Disclosure → 最小権限 (RBP)
* **D**enial of Service → Container App CPU throttle + AI Search QPS 制限
* **E**scalation of Privilege → Pod Security Policy (prod)

---

## 3. 運用 (Ops)

パフォーマンス監視・ログ・トレース・アラートの詳細設定については **[performance_monitoring.md](performance_monitoring.md)** を参照してください。

| 項目         | ツール / 手法                                        | メモ                                        |
| ---------- | ----------------------------------------------- | ----------------------------------------- |
| **監視**     | Azure Monitor (Container Insights, LA Query)    | p95 レイテンシ、CPU/Memory HPA メトリクス            |
| **ロギング**   | `structlog` → stdout → Container Log → LA       | ログタグ: `session_id`, `trace_id`            |
| **分散トレース** | OpenTelemetry SDK → OTLP → LA                   | Span 名: `rag.search`, `openai.completion` |
| **アラート**   | LA Query → Action Group → Email/Teams           | NFR 違反しきい値                                |
| **バックアップ** | `pg_dump` 週次、AI Search インデックス JSON エクスポート       | GH Actions cron                           |
| **CI/CD**  | GitHub Actions (Terraform plan / Bicep what‑if) | main merge で本番環境 apply                 |

---

## 4. スケール戦略

| レイヤ           | 手法                         | 短期 (dev)  | 長期 (prod 想定)                  |
| ------------- | -------------------------- | --------- | ----------------------------- |
| Container App | HPA (CPU>70%), min 0 max 3 | 自動 0→1    | min 3 max 10, zone spread     |
| AI Search     | Free F1                    | Replica 1 | S2, Replica 3, Partition 2    |
| Cosmos PG     | Single Node                | vCore 1   | 3‑node HA, vCore 4            |
| OpenAI        | GPT‑4o mini                | TPU 0.1   | TPU 1–2, Dedicated throughput |

---

## 5. コストガードレール

詳細なコスト管理戦略・予算設定・最適化手法については **[cost_management.md](cost_management.md)** を参照してください。

基本方針：
* **Budget アラート**: `az costmanagement budget create` $5/月 しきい値 80 % で通知。
* Terraform/Bicep 変数 `is_free=true` が false になる PR は CI で失敗させる (`tflint custom rule`).

---

## 6. 継続的改善ログ (KPT)

| Keep                                | Problem                     | Try                        |
| ----------------------------------- | --------------------------- | -------------------------- |
| セッション単位分散キーで JOIN 高速                | 初回 GPT 呼び出しレイテンシが 1.6 s と長め | 温めリクエスト or proxy cache を検証 |
| GitHub Actions `what-if` で差分が分かりやすい | AI Search Free 容量 50 MB が近い | 圧縮 index 分割 / 有料 SKU を検証   |

---

*Last updated: 2025-06-03*
