module "dev_cluster" {
    source       = "./main"
    env_name     = "dev"
    cluster_name = "imrank8scluster"
}
