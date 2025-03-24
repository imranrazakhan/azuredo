resource "random_integer" "this" {
  min = 10000
  max = 5000000
}

resource "azurerm_storage_account" "storage" {
  name                     = "${var.prefix}storage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "this" {
  name                  = "test"
  storage_account_id    = azurerm_storage_account.this.id  # ✅ Correct
  container_access_type = "private"
}

resource "azurerm_role_assignment" "dev_test" {
  scope                = azurerm_storage_account.this.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.dev_test.principal_id
}
