Steps to Connect Argo Workflows in AKS to Azure PostgreSQL via Managed Identity
1️⃣ Enable Managed Identity for AKS
First, ensure your AKS cluster has a managed identity:

```sh
az aks update -g <RESOURCE_GROUP> -n <AKS_CLUSTER> --enable-managed-identity
```

Find the Managed Identity ID for your AKS cluster:

```sh
az aks show -g <RESOURCE_GROUP> -n <AKS_CLUSTER> --query "identity.principalId" -o tsv
```

Save this IDENTITY_ID for the next step.

2️⃣ Grant AKS Managed Identity Access to Azure PostgreSQL
Now, assign the Managed Identity the Azure PostgreSQL AAD Admin Role.

```sh
az role assignment create \
  --assignee <IDENTITY_ID> \
  --role "Azure Database Administrator Login" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.DBforPostgreSQL/servers/<PG_SERVER>
```

This allows AKS to authenticate to PostgreSQL without a password.

3️⃣ Enable Azure AD Authentication in PostgreSQL
Enable Azure AD Authentication in your Azure PostgreSQL Flexible Server:

```sh
az postgres flexible-server update \
  --resource-group <RESOURCE_GROUP> \
  --name <PG_SERVER> \
  --enable-identity-authentication true
```

Create an AAD User in PostgreSQL for AKS:

```sql
CREATE ROLE aks_etl_user WITH LOGIN INHERIT;
GRANT CONNECT ON DATABASE yourdatabase TO aks_etl_user;
```

