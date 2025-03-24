resource "azurerm_virtual_network" "vpc" {
  name                = "${var.prefix}-vpc"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = var.vpc_cidr
  tags               = local.common_tags
}
