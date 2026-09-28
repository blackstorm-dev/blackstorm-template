# Networking

![Public ingress, DNS, and certificates](../../resources/network.png){ loading=lazy }

Solid lines are traffic. Dotted lines are DNS resolution and route configuration.

## Path of a request

=== "Production"

    | Fact | Consequence |
    |---|---|
    | `cloudflared` opens the connections outwards | No public IP, no inbound ports, no LoadBalancer |
    | Cloudflare terminates TLS | Traffic inside the cluster is plain HTTP |
    | The hostname decides at both ends | Cloudflare applies Access; Envoy picks the Service |

=== "Local"

    ```text
    Browser → localhost:8443 → NodePort 30443 → Envoy → Service → Pod
    ```

    | Fact | Consequence |
    |---|---|
    | No tunnel and no Access | Every route is reachable from the machine |
    | Envoy terminates TLS | The certificate is self-signed; the browser warns |

## Who creates what

| Resource | Created by |
|---|---|
| Tunnel, `tunnel.<domain>` record, Access applications | Terraform, `make infra-apply` |
| Cloudflare credentials in the cluster | `make bootstrap` |
| One DNS record per public `HTTPRoute` | external-dns |
| Gateway certificate | cert-manager |

| Environment | Certificate |
|---|---|
| Local | Self-signed, `*.localhost` |
| Production | Let's Encrypt through Cloudflare DNS-01, `*.blackstorm.dev` |

## Recipes

| Goal | Change |
|---|---|
| Publish an application | An `HTTPRoute` that points to `envoy-external` |
| Keep a route internal | An `HTTPRoute` that points to `envoy-internal` |
| Protect a host | Add it to `protected_hosts` |
| Let someone into a protected host | Add their email to `admin_emails` |

```hcl title="live/prod/terraform/cloudflare/terragrunt.hcl"
inputs = {
  protected_hosts = ["argocd"] # (1)!
  admin_emails    = ["you@example.com"]
}
```

1.  Apply with `make infra-apply ENV=prod UNIT=cloudflare`.

## Inspect

| Question | Command |
|---|---|
| Is the tunnel connected? | `kubectl --context prod -n network logs deploy/cloudflared` |
| Which DNS records were created? | `kubectl --context prod -n network logs deploy/external-dns` |
| Is the certificate ready? | `kubectl --context prod -n network get certificate` |
