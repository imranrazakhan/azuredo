resource "azurerm_kubernetes_cluster_node_pool" "worker_pool" {
  name                  = "workerpool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = "Standard_D2s_v3"
  node_count            = 2
  vnet_subnet_id        = azurerm_subnet.aks_subnet.id
}
