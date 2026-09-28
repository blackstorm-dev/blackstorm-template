# Operations

## Commands

| Command | Effect |
|---|---|
| `make init` | Installs tools and hooks; creates `age.key` if missing |
| `make connect ENV=<env>` | Writes the kubeconfig of an existing cluster |
| `make cluster ENV=<env>` | Provisions and bootstraps |
| `make bootstrap ENV=<env>` | Bootstraps a cluster that already exists |
| `make infra-plan ENV=<env> [UNIT=<unit>]` | Shows what would change |
| `make infra-apply ENV=<env> [UNIT=<unit>]` | Applies, after confirmation |
| `make infra-destroy ENV=<env> [UNIT=<unit>]` | Destroys, after confirmation |

| Variable | Meaning |
|---|---|
| `ENV` | A directory under `live/`. Required. |
| `UNIT` | One Terragrunt unit. Without it, every unit in the environment runs, in dependency order. |

!!! danger "`make infra-destroy ENV=prod UNIT=cluster` destroys the cluster"

!!! info "Make prints each command before running it"

    What you see is what runs. Credentials are decrypted in memory and never written to disk.

## Dependency updates

![Renovate updates, review, and synchronization](../resources/renovate.png){ loading=lazy }

| Change | Applied by |
|---|---|
| Kubernetes components | Argo CD, after the merge |
| Terraform and Terragrunt | `make infra-apply` |
| Tools in `mise.toml` | `mise install` |

Renovate never merges on its own. The workflow renders and validates every manifest before review.

## Documentation

```bash
make docs-diagram      # regenerate the architecture diagrams
make docs-serve        # preview this site at http://127.0.0.1:8088
make docs-build        # build this site into site/
```

```bash
make test-tutorials ENV=local    # run the tutorials as tests
make tutorial-videos ENV=local   # record them
```

!!! warning "Tutorials change the cluster"

    They promote for real. They only run against the local cluster.
