import pulumi
from pulumi_azure_native import resources, containerregistry, authorization, containerservice
from infra.aks import AKSCluster
from pulumi_kubernetes import Provider, helm
import pulumi_kubernetes as k8s
from pulumi_kubernetes.core.v1 import Namespace, Secret
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
    resource_group_name=resource_group.name,
    resource_name=aks_cluster.cluster.name,
    #opts=pulumi.ResourceOptions(depends_on=[aks_cluster.cluster])
)


# Configure Kubernetes Provider using the AKS Kubeconfig
k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=creds.kubeconfigs[0].value.apply(lambda enc: base64.b64decode(enc).decode()),
)


# Deploy ArgoCD using Helm with the argocd_values.yaml file
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

# Fetch the password from environment variables
encoded_url = base64.b64encode( "https://github.com/imranrazakhan/DevOps-Challenge".encode()).decode()
github_username = base64.b64encode( "imranrazakhan".encode()).decode()
github_pat = base64.b64encode( os.environ.get("github_pat").encode()).decode()

argocd_repo_secret = Secret(
 "argocd-repo-doc-github",
 metadata={
     "namespace": "argocd",
     "name": "argocd-repo-doc-github",
     "labels": {
            "argocd.argoproj.io/secret-type": "repository"
     }
 },
 data={
    "url": encoded_url,
    "username": github_username,
    "password": github_pat,
 },
 opts=pulumi.ResourceOptions(provider=k8s_provider)
)

monitoring_namespace = Namespace(
 "monitoring-namespace",
 metadata={ "name": "monitoring"},
 opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Deploy Kafka Strimzi using Helm with the kafka_Strimzi_values.yaml file
strimzi_cluster_operator_helm = helm.v3.Release(
    "strimzi-cluster-operator",
    helm.v3.ReleaseArgs(
        chart="strimzi-kafka-operator",
        version="0.45.0",
        repository_opts=helm.v3.RepositoryOptsArgs(
            repo="https://strimzi.io/charts/",  # The repository URL for ArgoCD's Helm chart
        ),
        namespace="kafka",
        create_namespace=True,
        value_yaml_files=[pulumi.FileAsset("./kafka_strimzi_values.yaml")],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Deploy Kafka Strimzi using Helm with the kafka_Strimzi_values.yaml file
kafka_argocd_apps = helm.v3.Release(
    "kafka-argocd-apps",
    helm.v3.ReleaseArgs(
        name="kafka-app",
        chart="argocd-apps",
        version="2.0.2",
        repository_opts=helm.v3.RepositoryOptsArgs(
            repo="https://argoproj.github.io/argo-helm",
        ),
        namespace="argocd",
        value_yaml_files=[pulumi.FileAsset("./kafka-argocd-app.yaml")],
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[argocd_helm]
    ),
)

# Deploy KEDA using Helm with the kafka_Strimzi_values.yaml file
keda_helm = helm.v3.Release(
    "keda-helm",
    helm.v3.ReleaseArgs(
        chart="keda",
        version="2.16.1",
        repository_opts=helm.v3.RepositoryOptsArgs(
            repo="https://kedacore.github.io/charts",
        ),
        namespace="keda",
        create_namespace=True,
        values={
            "watchNamespace": "",  # Watch all namespaces
            "image": {
                "tag": "2.16.1"  # Ensure compatibility
            }
        }
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Deploy a Kafka ScaledObject for KEDA autoscaling
kafka_scaled_object = k8s.apiextensions.CustomResource(
    "kafka-scaledobject",
    api_version="keda.sh/v1alpha1",
    kind="ScaledObject",
    metadata={
        "name": "kafka-scaledobject",
        "namespace": "keda",
    },
    spec={
        "scaleTargetRef": {
            "name": "my-kafka-consumer",
        },
        "minReplicaCount": 1,
        "maxReplicaCount": 10,
        "pollingInterval": 5,  # Poll Kafka every 5 seconds
        "cooldownPeriod": 30,  # Scale down after 30 seconds of inactivity
        "triggers": [
            {
                "type": "kafka",
                "metadata": {
                    "bootstrapServers": "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092",  # Update with your Kafka service
                    "consumerGroup": "my-consumer-group",  # Replace with your consumer group
                    "topic": "my-topic",  # Replace with the Kafka topic name
                    "lagThreshold": "5",  # Scale when lag > 5 messages
                }
            }
        ]
    },
    opts=pulumi.ResourceOptions(depends_on=[keda_helm])
)


kubeflow_helm = k8s.helm.v3.Chart(
    "kubeflow",
    k8s.helm.v3.ChartOpts(
        chart="kubeflow",
        namespace="kubeflow",
        fetch_opts=k8s.helm.v3.FetchOpts(
            repo="https://charts.kubeflow.org"
        ),
    )
)

# Argo Workflows installation using Helm
argo_chart = k8s.helm.v3.Chart("argo-workflows",
    k8s.helm.v3.ChartOpts(
        chart="argo-workflows",
        version="0.32.3",  # Check for the latest version
        fetch_opts=k8s.helm.v3.FetchOpts(
            repo="https://argoproj.github.io/argo-helm"
        ),
        namespace="argo",
        create_namespace=True,
    )
)

# RBAC setup (optional, needed for workflow permissions)
sa = k8s.core.v1.ServiceAccount("argo-sa",
    metadata={
        "name": "argo-sa",
        "namespace": "argo"
    })

etl_workflow = k8s.core.v1.ConfigMap("etl-workflow",
    metadata={"name": "etl-workflow", "namespace": "argo"},
    data={"workflow.yaml": open("etl-workflow.yaml").read()}
)


# Export AKS Cluster Name and ACR Name
pulumi.export("aks_name", aks_cluster.cluster.name)
pulumi.export("acr_name", acr.name)
