resource "azurerm_kubernetes_cluster" "aks" {
  name                          = var.aks_cluster_name
  location                      = var.location
  resource_group_name           = var.resource_group_name
  dns_prefix                    = var.dns_prefix
  kubernetes_version            = var.kubernetes_version
  image_cleaner_enabled         = true
  image_cleaner_interval_hours  = 24
  oidc_issuer_enabled           = true
  workload_identity_enabled     = true

  default_node_pool {
    name       = "docnodepool"
    node_count = 3
    vm_size    = var.vm_size
    #zones   = ["1", "2", "3"]
  }

  identity {
    type = "SystemAssigned"
  }

  # For production change to "Standard"
  sku_tier = "Free"

  tags = var.tags

}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = var.acr_id
  role_definition_name = "AcrPull" # Allows AKS to pull images
  #principal_id         = azurerm_kubernetes_cluster.aks.identity[0].principal_id
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}


