import pulumi
from pulumi_azure_native import resources, containerservice
from pulumi_kubernetes import Provider
from pulumi import Output

class AKSCluster(pulumi.ComponentResource):
    def __init__(self, name, args, opts=None):
        super().__init__('pkg:index:AKSCluster', name, args, opts)

        # Resource Group creation
        self.resource_group = resources.ResourceGroup(
            "aks-resource-group",
            opts=pulumi.ResourceOptions(parent=self)
        )

        # AKS Cluster setup
        self.aks_cluster = containerservice.ManagedCluster(
            "aks-cluster",
            resource_group_name=self.resource_group.name,
            location=self.resource_group.location,
            linux_profile=containerservice.ContainerServiceLinuxProfileArgs(
                admin_username="azureuser",
                ssh_config=containerservice.ContainerServiceSshConfigurationArgs(
                    public_keys=[
                        containerservice.ContainerServiceSshPublicKeyArgs(
                            key_data="ssh-rsa ..."
                        )
                    ]
                )
            ),
            agent_pool_profiles=[containerservice.ManagedClusterAgentPoolProfileArgs(
                name="agentpool",
                count=3,
                vm_size="Standard_DS2_v2",
                os_type="Linux",
                mode="System"
            )],
            enable_rbac=True,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Set the Kubernetes provider for subsequent Kubernetes resources
        self.kubeconfig = Output.all(self.aks_cluster.kube_config_raw).apply(lambda kubeconfig: kubeconfig)
        self.k8s_provider = Provider("k8s-provider", kubeconfig=self.kubeconfig)

        # Export the kubeconfig for use in other modules
        pulumi.export("kubeconfig", self.kubeconfig)