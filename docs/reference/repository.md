# Repository structure

```text
terraform/
├── resources/<provider>/       # parameterized resources
└── modules/                    # infrastructure composition
live/
├── root.hcl                    # shared Terragrunt configuration
└── <environment>/
    ├── terraform/              # infrastructure units and state
    ├── kubernetes/             # enabled components and cluster configuration
    └── secrets/                # encrypted credentials
kubernetes/
├── apps/                       # shared charts, values, and resources
└── charts/project-onboarding/  # namespaces and permissions per discovered repository
bootstrap/helmfile.yaml         # initial installation
docs/                           # this site, diagrams, and plans
tests/                          # tutorials: browser tests that are also recorded
projects/                       # independent local checkouts, ignored by Git
Makefile · mise.toml · mkdocs.yml · .sops.yaml · .lefthook.toml · renovate.json
```

| Question | Look in |
|---|---|
| How is this component configured everywhere? | `kubernetes/apps/<namespace>/<app>/` |
| Does this component run in this cluster? | `live/<cluster>/kubernetes/<namespace>/<app>/` |
| What infrastructure does this environment have? | `live/<environment>/terraform/` |
| Which version of a tool is pinned? | `mise.toml` |
