# Quick start

## Requirements

| Tool | Purpose |
|---|---|
| [mise](https://mise.jdx.dev/) | Installs the pinned versions of every other tool |
| Docker Desktop | Runs the local cluster |
| GitHub CLI, authenticated | Reads repositories and sets secrets |

## Create a cluster

=== "Local"

    ```bash
    git clone git@github.com:blackstorm-dev/blackstorm-infra.git
    cd blackstorm-infra
    make init # (1)!
    make cluster ENV=local # (2)!
    ```

    1.  Installs tools and hooks, and creates `age.key` if it is missing.
    2.  Creates kind in Docker, then runs the bootstrap.

=== "Production"

    ```bash
    make init
    sops live/prod/secrets/digitalocean.env # (1)!
    sops live/prod/secrets/cloudflare.env
    make cluster ENV=prod
    ```

    1.  Production needs DigitalOcean, Spaces, and Cloudflare credentials, and a domain
        configured in Cloudflare.

=== "Existing installation"

    ```bash
    cp <backup>/age.key . # (1)!
    make init
    make connect ENV=prod # (2)!
    ```

    1.  Recover the key before `make init`, or a new one is generated.
    2.  Writes `.kube/prod`. mise adds it to `KUBECONFIG` inside the repository.

!!! danger "Back up `age.key`"

    Without it, nothing under `live/*/secrets/` can be decrypted. A lost key means new
    credentials and re-encrypting every secret.

## What `make init` does

![What make init prepares on the operator's machine](../resources/init.png){ loading=lazy }

## What the bootstrap does

![Provisioning and bootstrap of the local and production clusters](../resources/bootstrap.png){ loading=lazy }

| Step | Action |
|---|---|
| 1 | Loads the SOPS key, so the operator can decrypt what Argo CD applies |
| 2 | Loads the environment deploy key, so Argo CD can read this repository |
| 3 | Installs Argo CD and the secrets operator with Helmfile |
| 4 | Applies the `AppProject` and the `ApplicationSet` |

From there, Argo CD manages everything from Git, including itself. Every step can be run again.

## Check it

```bash
kubectl --context local get nodes
kubectl --context local -n argocd get applications
```

Then open the [interfaces](../reference/interfaces.md).
