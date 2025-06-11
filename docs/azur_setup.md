# Azure 手動セットアップ手順

以下は、Terraform（または Bicep）を使って自動化できない、あるいは最初に手動で準備しておく必要がある最低限の Azure 側作業をまとめた手順です。それ以外のリソース（Key Vault／Cosmos DB／AI Search／OpenAI など）は、Terraform コードの実行で一括プロビジョニングします。

---

## 1. Azure アカウント作成
1. ブラウザで [Azure 無料アカウント](https://azure.microsoft.com/free) にアクセスし、「無料アカウントを作成」をクリック。
2. Microsoft アカウントでサインインし、住所・氏名など必要事項を入力。
3. クレジットカード情報を登録（課金保護機能あり）。
4. 本人確認が完了すると、Free サブスクリプション（US\$200 クレジット＋無料サービス）が利用可能になる。

> **備考**: 学生の場合は「Azure for Students」を申し込むと、クレジットカード不要で US\$100 のクレジットが得られます。

---

## 2. Azure CLI のインストールとログイン
### 2-1. インストール
- **Windows（PowerShell）**
  ```powershell
  winget install --exact --id Microsoft.AzureCLI

- **macOS（Homebrew）**

brew update
brew install azure-cli


- **Linux (Ubuntu/Debian)**

sudo apt-get update
sudo apt-get install ca-certificates curl apt-transport-https lsb-release gnupg
curl -sL https://packages.microsoft.com/keys/microsoft.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/azure-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/azure-archive-keyring.gpg] \
  https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/azure-cli.list
sudo apt-get update
sudo apt-get install azure-cli



2-2. 動作確認とログイン

az version
az login

	•	az version：バージョン情報が表示されれば OK。
	•	az login：ブラウザが起動し、サインイン。CLI 上にアカウント情報が JSON 形式で返る。

⸻

3. サブスクリプション確認・設定

az account show

	•	"isDefault": true がアクティブサブスクリプション。
	•	特定のサブスクリプションを選びたい場合は以下を実行：

az account set --subscription "<サブスクリプションID>"



⸻

4. リソースグループ作成
	1.	好きな名前（例: qrai-rg）とリージョン（例: westus2）を決定。
	2.	以下コマンドで作成：

az group create \
  --name qrai-rg \
  --location westus2


	3.	出力例：

{
  "id": "/subscriptions/XXXXXX/resourceGroups/qrai-rg",
  "location": "westus2",
  "name": "qrai-rg",
  "properties": {
    "provisioningState": "Succeeded"
  },
  ...
}



備考: リソースグループは Terraform backend や他リソースを一元管理するための親フォルダとして利用します。

⸻

5. Terraform Backend 用ストレージアカウント準備

Terraform state を Azure Blob Storage に置く場合、以下は手動作成が推奨されます。

5-1. ストレージアカウント作成

az storage account create \
  --name qraitfstg \
  --resource-group qrai-rg \
  --location westus2 \
  --sku Standard_LRS

5-2. ストレージコンテナ作成

az storage container create \
  --account-name qraitfstg \
  --name tfstate \
  --public-access off

	•	--public-access off で非公開コンテナを作成。

5-3. アクセスキー取得

az storage account keys list \
  --resource-group qrai-rg \
  --account-name qraitfstg \
  --query "[0].value" -o tsv

	•	取得したキーは Terraform の backend 設定で使うため、後ほど .tf ファイルの環境変数またはシークレットに設定してください。

備考: この作業は一度だけ行い、以降は Terraform から自動的に state を保存・更新できます。

⸻

6. サービスプリンシパル (CI/CD 用) の作成（任意）

GitHub Actions 等から Terraform 実行する際には、個人アカウントではなくサービスプリンシパル（SP）を使うと安全です。

6-1. SP 作成

az ad sp create-for-rbac \
  --name qrai-ci-sp \
  --role Contributor \
  --scopes /subscriptions/<サブスクリプションID>/resourceGroups/qrai-rg

	•	出力例：

{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "displayName": "qrai-ci-sp",
  "name": "...",
  "password": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
  "tenant": "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
}


	•	appId と password（クライアントシークレット）および tenant を GitHub Secrets や Azure Key Vault に保存。

6-2. Key Vault アクセス許可（必要に応じて）

az keyvault set-policy \
  --name qrai-kv \
  --spn <サービスプリンシパルのAppId> \
  --secret-permissions get list

	•	SP が Key Vault のシークレットを取得できるようにポリシーを付与。

備考: 6番以降の作業は、CI/CD で Azure リソースを作成する場合にのみ必要です。MVP 段階では手動での Terraform 実行を想定して省略しても問題ありません。

⸻

7. 手動セットアップまとめ

手順	内容	必要性
1	Azure 無料アカウント作成	必須（CLI 利用の前提）
2	Azure CLI インストール & az login	必須（Terraform 実行前提）
3	リソースグループ作成 (qrai-rg)	必須（リソース配置先）
4	ストレージアカウント作成 (qraitfstg)	Terraform backend 用：必須
5	ストレージコンテナ作成 (tfstate)	Terraform backend 用：必須
6	SP 作成（qrai-ci-sp）	任意（CI/CD 用途）
7	Key Vault ポリシー設定	任意（アプリから Key Vault 利用が必要な場合）


⸻

この手順を済ませたら、以下のように Terraform コードを使ってリソースを一括プロビジョニングできます：

# Terraform backend の初期化（ストレージアカウント情報は環境変数や Secret から読み込む）
terraform init \
  -backend-config="storage_account_name=qraitfstg" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=terraform.tfstate" \
  -backend-config="access_key=<ストレージキー>"

# リソースのプロビジョニング（Key Vault／Cosmos DB／AI Search／OpenAI など）
terraform apply -auto-approve

これで、手動作業は最小限にとどめつつ、Terraform による完全自動化がスタートできる状態になります。
