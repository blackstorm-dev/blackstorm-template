# Quick start

## Requirements

| Tool | Purpose |
|---|---|
| [mise](https://mise.jdx.dev/) | Installs the pinned versions of every other tool |
| Docker Desktop | Runs the local cluster |
| GitHub CLI, authenticated | Reads repositories and sets secrets |

## Prepare your installation

Clone the template with its sample application:

```bash
git clone --recurse-submodules https://github.com/blackstorm-dev/blackstorm-template.git
cd blackstorm-template
make init
mise exec -- gh auth login
```

Create your own infrastructure repository and point `origin` at it. Configure
`live/<environment>/config/values.yaml` with that repository, your organization, domain,
administrators, and storage. Terraform and Kubernetes use these same values.

`make init` creates `age.key` and configures its public recipient in `.sops.yaml`.
The `*.example` files contain placeholders, not credentials. For each secret required by your
environment, run the command printed at the top of its example, without the `.example` suffix:

```bash
make secrets FILE=live/local/secrets/github-arc.yaml
```

The command opens SOPS with the example's structure. Replace its placeholders and save the encrypted
file. Configure the GitHub Apps and OIDC clients as described in
[Identity and access](architecture/identity.md). Use the same client secret on each side of an
OIDC integration. See [Secrets](architecture/secrets.md) for the file layout.

Commit and push your configuration, `.sops.yaml`, and encrypted secrets to your repository before
creating resources: Argo CD reads the published revision. Never commit `age.key`.

## Create a cluster

=== "Local"

    Start Docker Desktop, then run:

    ```bash
    make cluster ENV=local
    ```

    Creates kind, installs the bootstrap, and waits for the platform. The command prints the Argo CD
    URL as soon as it is reachable and lists the panel URLs when the platform is ready.

=== "Production"

    Configure `live/prod/config/values.yaml` and the secrets under `live/prod/secrets/`, including
    DigitalOcean, Spaces, Cloudflare, and the GitHub Apps. For example:

    ```bash
    make secrets FILE=live/prod/secrets/digitalocean.env
    make secrets FILE=live/prod/secrets/cloudflare.env
    # Commit and push the completed configuration and encrypted secrets.
    make cluster ENV=prod
    ```

=== "Existing installation"

    Use the installation's configured repository and recover its key before running `make init`:

    ```bash
    cp <backup>/age.key .
    make init
    make connect ENV=prod
    ```

    `make connect` writes `.kube/prod`. mise adds it to `KUBECONFIG` inside the repository.

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
