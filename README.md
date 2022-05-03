# Getting started with Terraform and Kubernetes on Azure AKS

There are few prerequisites needed to be done, before proceeding for coding

- Install Azure CLI
- Install Terraform
- Terraform uses a different set of credentials to provision the infrastructure, so you should create those first.
  - ```az login```
  - In case you’d like to work with multiple subscriptions, you can set a specific subscription - which will receive the Terraform commands - by using following Azure CLI command:
    -   ```az account set --subscription "<your subscription id>"```
  - Terraform needs a Service Principal to create resources on your behalf.
    - You will first need to get your subscription ID. (Make a note of your subscription id.)
      - ```az account list |  grep -oP '(?<="id": ")[^"]*'```
    - You can create the Service Principal with:
      - ```az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/SUBSCRIPTION_ID" ```
    - The previous command should print a JSON payload like this:
      ```
      {
        "appId": "00000000-0000-0000-0000-000000000000",
        "displayName": "azure-cli-2021-02-13-20-01-37",
        "name": "http://azure-cli-2021-02-13-20-01-37",
        "password": "0000-0000-0000-0000-000000000000",
        "tenant": "00000000-0000-0000-0000-000000000000"
      }
      ```
      
    - Export the following environment variables:
        ```
        export ARM_CLIENT_ID=<insert the appId from above>
        export ARM_SUBSCRIPTION_ID=<insert your subscription id>
        export ARM_TENANT_ID=<insert the tenant from above>
        export ARM_CLIENT_SECRET=<insert the password from above>
        ```
 - Create directory like aks-cluster, copy terraform code in it.
 -  ```terraform init```
 -  ```terraform plan```
 -  ```terraform apply```



