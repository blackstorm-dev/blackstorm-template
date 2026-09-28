# Identity

![Dashboard login through Dex and GitHub](../../resources/identity.png){ loading=lazy }

Every dashboard delegates login to Dex, and Dex asks GitHub.

## Who gets in

| Check | Decided by |
|---|---|
| Member of the GitHub organization | `orgs` in the Dex connector |
| Role inside the dashboard | Each dashboard's own mapping |

| Dashboard | Role mapping |
|---|---|
| Argo CD | `policy.csv` in `argocd/argocd/rbac.yaml` |
| Kargo | `rbac.kargo.akuity.io/claims` in `kargo/kargo/oidc.yaml` |
| Grafana | `GF_AUTH_GENERIC_OAUTH_ROLE_ATTRIBUTE_PATH` in `o11y/kube-prometheus-stack/oidc.yaml` |
| Gatus | `allowed-subjects` in `o11y/gatus/security.yaml` |
| Velero UI | `velero/velero-ui/policies.csv` |
| StackGres | `ClusterRoleBinding` in `stackgres/stackgres/oidc-rbac.yaml` |

Paths are relative to `live/<cluster>/kubernetes/`.

## Where it is configured

| What | Where |
|---|---|
| Connector and clients | `live/<cluster>/kubernetes/identity/dex/config.yaml` |
| Client secrets | `live/<cluster>/secrets/dex/` and one directory per dashboard |
| Callback allowed in the GitHub OAuth App | `https://dex.<domain>/callback` |

## Inspect

| Question | Command |
|---|---|
| Is Dex running? | `kubectl -n identity get pods` |
| Why was a login rejected? | `kubectl -n identity logs deploy/dex` |
