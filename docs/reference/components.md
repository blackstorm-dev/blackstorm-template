# Components

| Purpose | Tools |
|---|---|
| Provisioning | Terraform, Terragrunt, DigitalOcean Kubernetes, kind |
| Bootstrap | Helmfile |
| GitOps and discovery | Argo CD, ApplicationSets |
| CI | GitHub Actions, Actions Runner Controller (ARC) |
| Promotions | Kargo |
| Progressive delivery | Argo Rollouts |
| Registry | Docker Hub |
| Secrets | SOPS, age, sops-secrets-operator |
| Networking | Envoy Gateway, Gateway API, Cloudflare Tunnel and Access |
| DNS and certificates | external-dns, cert-manager |
| Identity and login | Dex, GitHub |
| Metrics and alerts | Prometheus, Grafana, Alertmanager |
| Logs and traces | Alloy, Loki, Tempo |
| Availability | Gatus |
| PostgreSQL | StackGres |
| Kubernetes and volume backups | Velero, Velero UI, DigitalOcean Spaces |
| Configuration reloads | Reloader |
| Tooling and updates | mise, Make, lefthook, Renovate |

Shared definitions live in `kubernetes/apps/`. Each cluster enables the ones it needs under
`live/<cluster>/kubernetes/`.
