terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.49.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "tfstate-rg-dev"
    storage_account_name = "<storage-account>"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}


module "dev_cluster" {
    source       = "./main"
    env_name     = "dev"
    cluster_name = "imrank8scluster"
}

