import pulumi
from pulumi_azure_native import resources, containerregistry, authorization, containerservice
from infra.aks import AKSCluster
from pulumi_kubernetes import Provider, helm
#import pulumi_kubernetes.helm.v3 as helm
import os
import base64

# Load Configurations
config = pulumi.Config()

azure_native_config = config.get_object("azure-native") or {}

aks_config = {
    "location": azure_native_config.get("location"),
    "aks_cluster_name": config.require("aks_cluster_name"),
    "resource_group_name": config.require("resource_group_name"),
    "dns_prefix": config.require("dns_prefix"),
    "kubernetes_version": config.require("kubernetes_version"),
    "vm_size": config.require("vm_size"),
    "node_count": config.require_int("node_count"),
    "tags": config.get_object("tags") or {},
    "subscription_id": config.require("subscription_id")
}


# Create Resource Group
resource_group = resources.ResourceGroup(
    "rg",
    resource_group_name=aks_config["resource_group_name"],
    location=aks_config["location"]
)

# Create Azure Container Registry (ACR)
acr = containerregistry.Registry(
    "maniacr",
    resource_group_name=resource_group.name,
    location=aks_config["location"],
    sku={
        "name": containerregistry.SkuName.BASIC,
    },
    # Disable admin user for security
    admin_user_enabled=False,
    tags=aks_config["tags"]
)

# Deploy AKS
aks_cluster = AKSCluster(name=aks_config["aks_cluster_name"], config=aks_config, resource_group_name=resource_group.name)


principal_id = aks_cluster.cluster.identity_profile.apply(
    lambda profile: profile["kubeletidentity"].object_id
)

# Define the ACR Pull Role Assignment
role_definition_id = f"/subscriptions/{aks_config['subscription_id']}/providers/Microsoft.Authorization/roleDefinitions/7f951dda-4ed3-4680-a7ca-43fe172d538d"


# Assign AcrPull Role to AKS
acr_pull_role_assignment = authorization.RoleAssignment(
    "acr-pull",
    principal_id=principal_id,
    role_definition_id=role_definition_id,
    scope=acr.id,  # Ensure `acr` is defined before this
    principal_type="ServicePrincipal",
)

# Get AKS Cluster credentials
creds = containerservice.list_managed_cluster_user_credentials_output(
    resource_group_name=resource_group, resource_name=aks_config["aks_cluster_name"]
)


# Configure Kubernetes Provider using the AKS Kubeconfig
k8s_provider = Provider(
    "k8s-provider",
    kubeconfig=creds.kubeconfigs[0].value.apply(lambda enc: base64.b64decode(enc).decode()),
)


# Deploy ArgoCD using Helm with the values.yaml file
argocd_helm = helm.v3.Release(
    "argocd-helm",
    helm.v3.ReleaseArgs(
        chart="argo-cd",  # The name of the Helm chart to deploy
        version="3.23.0",  # The version of the Helm chart
        repository_opts=helm.v3.RepositoryOptsArgs(
            repo="https://argoproj.github.io/argo-helm",  # The repository URL for ArgoCD's Helm chart
        ),
        namespace="argocd",
        create_namespace=True,
        value_yaml_files=[pulumi.FileAsset("./argocd_values.yaml")],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)


# Export AKS Cluster Name and ACR Name
pulumi.export("aks_name", aks_cluster.cluster.name)
pulumi.export("acr_name", acr.name)
