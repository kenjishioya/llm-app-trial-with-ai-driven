# 🔐 セキュリティガイドライン - QRAI Project

> **目的** — QRAI プロジェクトにおけるセキュリティベストプラクティス、個人情報保護、IaC セキュリティを体系化し、安全な開発・運用を確保する。

---

## 1. 個人識別情報（PII）保護

### 1.1 Git リポジトリに含めてはいけない情報

**絶対禁止項目**:
- ✗ Azure AD オブジェクトID（ユーザー識別子）
- ✗ メールアドレス（個人・組織問わず）
- ✗ API キー・パスワード・接続文字列
- ✗ 証明書・秘密鍵
- ✗ 個人名・社内ID

**制限項目**:
- ⚠️ 個人GitHubリポジトリURL（パラメータ化推奨）
- ⚠️ 組織ドメイン名（サンプル値に置換推奨）

### 1.2 セキュアな代替手法

| 情報種別 | 従来方法 | セキュア手法 |
|---------|---------|-------------|
| **Azure ADオブジェクトID** | `param objectId = '16f78429-...'` | `$(az ad signed-in-user show --query id -o tsv)` |
| **API キー** | 直接出力 | Key Vault経由参照 |
| **個人GitHubリポジトリ** | ハードコード | パラメータ化 |
| **環境固有設定** | プレーンテキスト | 環境変数・シークレット管理 |

---

## 2. Key Vault セキュリティ戦略

### 2.1 シークレット管理原則

**基本方針**:
1. **すべてのAPIキーはKey Vaultに保存**
2. **Terraformには参照情報のみ渡す**
3. **平文でのシークレット出力禁止**
4. **最小権限アクセス制御**

### 2.2 実装パターン

```bicep
// ✅ 正しい実装: Key Vaultに保存
resource openaiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'openai-api-key'
  properties: {
    value: openaiAccount.listKeys().key1
    contentType: 'Azure OpenAI API Key'
  }
}

// ✅ 出力はKey Vault参照のみ
output bicepOutputs object = {
  keyVaultName: keyVault.name
  openaiKeySecretName: openaiKeySecret.name
  // ❌ 直接出力は禁止: openaiApiKey: openaiAccount.listKeys().key1
}
```

```terraform
// ✅ Terraformでの安全な参照
data "azurerm_key_vault_secret" "openai_key" {
  name         = var.bicep_openai_key_secret_name
  key_vault_id = data.azurerm_key_vault.bicep_kv.id
}

// ✅ 環境変数として安全に利用
resource "null_resource" "app_config" {
  provisioner "local-exec" {
    environment = {
      AZURE_OPENAI_KEY = data.azurerm_key_vault_secret.openai_key.value
    }
    command = "echo 'Configuration applied'"
  }
}
```

### 2.3 アクセス制御設定

```bicep
// 最小権限のアクセスポリシー
accessPolicies: [
  {
    tenantId: tenant().tenantId
    objectId: keyVaultAccessObjectId  // 動的取得
    permissions: {
      secrets: ['get', 'list']  // 読み取り専用
      keys: ['get']
      certificates: ['get']
    }
  }
]
```

---

## 3. CI/CD セキュリティ

### 3.1 自動セキュリティスキャン

GitHub Actions で以下を自動実行:

```yaml
- name: Security Scan - Personal Information
  run: |
    # UUID/GUID パターン検出
    if grep -r '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' \
       --include="*.bicep" --include="*.tf" .; then
      echo "❌ ハードコードされたUUID検出"
      exit 1
    fi

    # メールアドレス検出
    if grep -r '[a-zA-Z0-9._%+-]\+@[a-zA-Z0-9.-]\+\.[a-zA-Z]\{2,\}' \
       --include="*.bicep" --include="*.tf" .; then
      echo "❌ メールアドレス検出"
      exit 1
    fi
```

### 3.2 デプロイメント保護

```yaml
environment: development  # Manual approval required
```

**保護レベル**:
- **Development**: 手動承認必須
- **Staging**: レビュー + 承認
- **Production**: 複数人承認 + 変更管理

---

## 4. インフラセキュリティ

### 4.1 ネットワークセキュリティ

```bicep
// 開発環境での制限付きアクセス
networkAcls: {
  defaultAction: 'Allow'  // 開発環境のみ
  ipRules: [
    {
      value: '0.0.0.0/0'  // 本番では特定IPに限定
    }
  ]
}
```

### 4.2 リソース分離

| 環境 | リソースグループ | Key Vault | アクセス制御 |
|------|-----------------|-----------|-------------|
| **Development** | `qrai-dev-rg` | `qrai-dev-kv-*` | 個人アカウント |
| **Staging** | `qrai-stg-rg` | `qrai-stg-kv-*` | チーム共有 |
| **Production** | `qrai-prd-rg` | `qrai-prd-kv-*` | 運用チームのみ |

---

## 5. 運用セキュリティ

### 5.1 ログ・監視

```bash
# Key Vault アクセスログ監視
az monitor log-analytics query \
  --workspace qrai-dev-logs \
  --analytics-query "
    KeyVaultData
    | where TimeGenerated > ago(24h)
    | where OperationName == 'SecretGet'
    | project TimeGenerated, CallerIPAddress, OperationName, RequestUri_s
  "
```

### 5.2 定期セキュリティチェック

**週次**:
- [ ] Key Vault アクセスログレビュー
- [ ] 不要なシークレット削除
- [ ] アクセス権限監査

**月次**:
- [ ] リポジトリスキャン実行
- [ ] Key Vault バックアップ確認
- [ ] セキュリティポリシー更新

---

## 6. インシデント対応

### 6.1 個人情報漏洩時の対応

**即座実行**:
1. 該当コミットの特定
2. Git履歴からの完全削除
3. 影響範囲の調査
4. キーローテーション実行

```bash
# 緊急時のKey Vault無効化
az keyvault update --name qrai-dev-kv-xxxxx --enabled-for-deployment false

# 新しいシークレット生成
az cognitiveservices account keys regenerate \
  --name qrai-dev-openai \
  --resource-group qrai-dev-rg \
  --key-name key1
```

### 6.2 復旧手順

1. **新しいAPIキー生成**
2. **Key Vaultシークレット更新**
3. **アプリケーション再起動**
4. **動作確認**

---

## 7. チェックリスト

### コミット前チェック
- [ ] UUID/GUIDがハードコードされていない
- [ ] メールアドレス・個人名が含まれていない
- [ ] APIキー・パスワードが平文で含まれていない
- [ ] `.env` ファイルが `.gitignore` に追加されている

### PR レビューチェック
- [ ] セキュリティスキャンが成功している
- [ ] Key Vault経由でシークレット管理されている
- [ ] 個人識別情報が削除されている
- [ ] アクセス制御が適切に設定されている

### デプロイ前チェック
- [ ] Azure CLI ログイン確認
- [ ] 必要な権限が付与されている
- [ ] バックアップが取得されている
- [ ] ロールバック手順が準備されている

---

## 8. 参考資料

- **[Azure Key Vault Security Best Practices](https://docs.microsoft.com/en-us/azure/key-vault/general/security-recommendations)**
- **[GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)**
- **[OWASP Infrastructure Security](https://owasp.org/www-project-infrastructure-security/)**
- **[Azure Security Baseline](https://docs.microsoft.com/en-us/security/benchmark/azure/)**
