from diagrams import Diagram, Cluster
from diagrams.onprem.iac import Terraform
from diagrams.azure.general import Resourcegroups
from diagrams.azure.compute import KubernetesServices
from diagrams.onprem.queue import Kafka
from diagrams.k8s.compute import Deployment
from diagrams.onprem.gitops import Argocd
from diagrams.k8s.podconfig import Secret
from diagrams.k8s.ecosystem import Helm

with Diagram("Terraform AKS Deployment with ArgoCD and Kafka", show=False, direction="TB"):
    # Terraform initiation
    tf_apply = Terraform("terraform apply")

    # Azure Infrastructure
    with Cluster("Azure Cloud"):
        resource_group = Resourcegroups("Resource Group")
        aks = KubernetesServices("AKS Cluster")
        tf_apply >> resource_group >> aks

    # Strimzi Operator Bootstrap
    with Cluster("Kafka Namespace"):
        strimzi_helm = Helm("Strimzi Operator")
        kafka = Kafka("Kafka Cluster")
        tf_apply >> strimzi_helm  # Terraform deploys Strimzi
        strimzi_helm >> kafka  # Initial deployment

    # ArgoCD GitOps Management
    with Cluster("ArgoCD Namespace"):
        argocd = Argocd("ArgoCD")
        repo_secret = Secret("Helm Repo Creds")
        kafka_helm = Helm("Kafka Helm")

        tf_apply >> argocd  # Terraform deploys ArgoCD
        argocd >> repo_secret >> kafka_helm  # Ongoing updates
        kafka_helm >> kafka  # Helm-based management

    # Microservices
    with Cluster("App Namespace"):
        producer = Deployment("Producer")
        consumer = Deployment("Consumer")
        argocd >> producer  # App deployment
        argocd >> consumer

    # Cross-component connections
    producer >> kafka
    consumer >> kafka
    aks << argocd  # AKS hosts ArgoCD