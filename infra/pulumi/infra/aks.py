import pulumi
from pulumi_azure_native import resources, containerservice

class AKSCluster:

    #resource_group = resources.ResourceGroup("rg")

    def __init__(self, name: str, config: dict, resource_group_name: pulumi.Output):
        self.name = name
        self.config = config

        # Create AKS Cluster
        self.cluster = containerservice.ManagedCluster(
            "dev-aks-cluster",
            resource_group_name=resource_group_name,
            location=config["location"],
            dns_prefix=config["dns_prefix"],
            kubernetes_version=config["kubernetes_version"],

            agent_pool_profiles=[containerservice.ManagedClusterAgentPoolProfileArgs(
                name="docnodepool",
                vm_size=config["vm_size"],
                count=config["node_count"],
                mode="System",
            )],


            identity=containerservice.ManagedClusterIdentityArgs(
                type="SystemAssigned"
            ),
            oidc_issuer_profile={
                "enabled": True,
            },
            security_profile={
                "workload_identity": {
                    "enabled": True,
                },
                "image_cleaner": {
                    "enabled": True,
                    "interval_hours": 24,
                },
            },
            tags=config["tags"]
        )