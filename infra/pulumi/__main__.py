"""An Azure RM Python Pulumi program"""

import pulumi
import pulumi_azure_native as azure

# Configurations
config = pulumi.Config()
resource_group_name = config.get("resource_group_name", "pulumi-aks-rg")
location = config.get("location", "East US")
cluster_name = config.get("cluster_name", "pulumi-aks-cluster")
node_count = config.get_int("node_count") or 2
vm_size = config.get("vm_size", "Standard_D2_v2")


# Create a Resource Group
resource_group = azure.resources.ResourceGroup(
    "rg",
    resource_group_name=resource_group_name,
    location=location
)

# Export outputs
pulumi.export("resource_group", resource_group.name)
