# Interfaces

## Local

| Interface | Address | Credentials |
|---|---|---|
| Argo CD | <https://argocd.localhost:8443/> | GitHub through Dex |
| Kargo | <https://kargo.localhost:8443/> | GitHub through Dex |
| Grafana | <https://grafana.localhost:8443/> | GitHub through Dex |
| Gatus | <https://gatus.localhost:8443/> | GitHub through Dex |
| Velero UI | <https://velero.localhost:8443/> | GitHub through Dex |
| StackGres | <https://stackgres.localhost:8443/> | GitHub through Dex |

!!! note "The browser warns about the certificate"

    The local certificate is self-signed.

## Production

| Interface | Address | Protected by |
|---|---|---|
| Argo CD | <https://argocd.blackstorm.dev/> | Cloudflare Access, then Argo CD's own login |
