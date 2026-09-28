# Operators

This repository manages the platform. Applications live in their own repositories.

```mermaid
flowchart LR
  M[Make] --> T[Terraform provisions]
  T --> H[Helmfile installs Argo CD and SOPS]
  H --> A[Argo CD manages the cluster from Git]
```

<div class="grid cards" markdown>

-   :material-flash:{ .lg .middle } [Quick start](quick-start.md)

    ---

    From a clean machine to a running cluster.

-   :material-sitemap:{ .lg .middle } [Architecture](architecture/index.md)

    ---

    GitOps, networking, and secrets.

-   :material-wrench:{ .lg .middle } [Operations](operations.md)

    ---

    Commands, components, and dependency updates.

-   :material-backup-restore:{ .lg .middle } [Recovery](recovery.md)

    ---

    What is backed up, where, and how to check it.

</div>
