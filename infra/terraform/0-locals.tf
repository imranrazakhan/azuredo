locals {
  env                 = "dev"
  region              = "eastus2"
  resource_group_name = "tutorial"
  common_tags = {
    Environment = var.environment
    Project     = "Terraform-AKS"
  }
}
