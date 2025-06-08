terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Azure Blob Storage backend (後でuncomment)
  # backend "azurerm" {
  #   resource_group_name  = "qrai-tfstate-rg"
  #   storage_account_name = "qraitfstate"
  #   container_name      = "tfstate"
  #   key                 = "dev.terraform.tfstate"
  # }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "azuread" {
  # テナントIDは自動取得
}

provider "random" {
  # デフォルト設定
}
