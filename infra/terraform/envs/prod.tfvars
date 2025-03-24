prefix          = "prod"
location        = "West Europe"
environment     = "prod"
vpc_cidr        = ["10.1.0.0/16"]
aks_subnet_cidr = ["10.1.1.0/24"]
node_count      = 3
node_vm_size    = "Standard_D4s_v3"