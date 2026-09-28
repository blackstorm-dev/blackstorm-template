# Architecture

![Production architecture](../../resources/overview.png){ loading=lazy }

| Area | How it works | Details |
|---|---|---|
| GitOps | One shared base per component, one overlay per cluster | [GitOps](gitops.md) |
| Networking | Outbound-only ingress through Cloudflare Tunnel | [Networking](networking.md) |
| Identity | Dashboards log in with GitHub through Dex | [Identity](identity.md) |
| Secrets | Encrypted in Git, decrypted inside the cluster | [Secrets](secrets.md) |
| Delivery | CI on ephemeral runners, promotion generated from each application's contract | [Delivery](delivery.md) |
| Observability | Metrics, logs, and traces in Grafana | [Observability](observability.md) |
| Recovery | Velero for resources and volumes, StackGres for PostgreSQL | [Recovery](../recovery.md) |

!!! info "What each cluster runs"

    | Component group | Local | Production |
    |---|---|---|
    | Argo CD, cert-manager, networking, secrets operator | :material-check: | :material-check: |
    | Kargo, Argo Rollouts, ARC runners | :material-check: | :material-close: |
    | Observability | :material-check: | :material-close: |
    | Velero, StackGres | :material-check: | :material-close: |
    | Reloader | :material-check: | :material-close: |

    A component runs in a cluster when it has a directory under `live/<cluster>/kubernetes/`.
