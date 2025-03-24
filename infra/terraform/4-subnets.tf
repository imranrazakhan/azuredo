resource "azurerm_subnet" "aks_subnet1" {
  name                 = "aks-subnet1"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes     = var.aks_subnet_cidr1
}


resource "azurerm_subnet" "aks_subnet2" {
  name                 = "aks-subnet2"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.vpc.name
  address_prefixes     = var.aks_subnet_cidr2
}



# If you want to use existing subnet
# data "azurerm_subnet" "subnet1" {
#   name                 = "subnet1"
#   virtual_network_name = "main"
#   resource_group_name  = "tutorial"
# }

# output "subnet_id" {
#   value = data.azurerm_subnet.subnet1.id
# }
