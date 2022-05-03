terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.49.0"
    }
  }
  backend "azurerm" {
      resource_group_name  = "tfstate-rg-dev"
      storage_account_name = "<storage_acct_name>"
      container_name       = "tfstate"
      key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = "ikk***********823"
}

resource "azurerm_resource_group" "rg" {
  name     = "imranrg-${var.env_name}"
  location = "West US 2"
  tags     = {
         "Environment" = "Terraform Getting Started"
         "Team"        = "DevOps"
        }

}

resource "azurerm_container_registry" "acr" {
  name                = "acr${var.env_name}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_kubernetes_cluster" "cluster" {
  name                = "${var.cluster_name}-${var.env_name}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "imrank8scluster-${var.env_name}"

  default_node_pool {
    name       = "default"
    node_count = "1"
    vm_size    = var.instance_type
    enable_auto_scaling = false
  }

  identity {
    type = "SystemAssigned"
  }
}
