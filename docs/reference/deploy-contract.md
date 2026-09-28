# Deployment contract

## Discovery

| Rule | Value |
|---|---|
| Organization | `blackstorm-dev` |
| Topic | `blackstorm-deploy` |
| Default branch | `main` or `master` |
| Access | Readable by the GitOps GitHub App |
| Marker | `deploy/platform.yaml` |
| Name | `^[a-z]([a-z0-9-]{0,48}[a-z0-9])?$` |

## `deploy/platform.yaml`

```yaml
releaseFormat: coordinated-tags
images:
  - docker.io/<namespace>/my-app-server # (1)!
  - repository: docker.io/<namespace>/my-app-backup
    deploy: false # (2)!
environments:
  staging:
    path: deploy/staging
    promotion: automatic
  production:
    path: deploy/production
    promotion: manual
    from: staging
```

1.  Short form: only the repository.
2.  Part of the release, but not pinned in the manifests.

| Field | Required | Values |
|---|---|---|
| `releaseFormat` | No | `coordinated-tags` (default), `commit-sha` |
| `images` | Yes, at least one | A repository, or an object |
| `images[].repository` | Yes | Image repository |
| `images[].name` | No | Name used in the manifests. Defaults to the repository |
| `images[].deploy` | No | `false` leaves the image out of the manifests |
| `environments.staging` | Yes | Receives releases directly; it has no `from` |
| `environments.production` | Yes | `from` must be `staging` |
| `environments.*.path` | Yes | `deploy/<directory>` |
| `environments.*.promotion` | Yes | `automatic`, `manual` |

The schema is `kubernetes/charts/project-delivery/values.schema.json`.

## Files

| Path | Content |
|---|---|
| `deploy/platform.yaml` | The contract |
| `deploy/<environment>/kustomization.yaml` | What the environment deploys |
| `deploy/<environment>/secrets/*.yaml` | Encrypted `SopsSecret` resources |
| `secrets/platform/` | Encrypted credentials for promotion, with a `kustomization.yaml` |
| `secrets/*.env` | Encrypted CI secrets |
| `.sops.yaml` | Encryption rules and recipients |

## Names the platform creates

| Resource | Name |
|---|---|
| Namespaces | `<repo>-staging`, `<repo>-production`, `<repo>` |
| Argo CD Applications | `<repo>-onboarding`, `<repo>-kargo`, `<repo>-staging`, `<repo>-production` |
| Kargo Project | `<repo>` |
| Output branches | `deploy/staging`, `deploy/production` |

## What an environment may deploy

Namespaced resources only.

| Group | Kinds |
|---|---|
| Core | `ConfigMap`, `Secret`, `Service`, `ServiceAccount`, `PersistentVolumeClaim` |
| Workloads | `Deployment`, `StatefulSet`, `Job`, `CronJob` |
| Progressive delivery | `Rollout`, `AnalysisTemplate` |
| Scaling and availability | `HorizontalPodAutoscaler`, `PodDisruptionBudget` |
| Networking | `HTTPRoute`, `NetworkPolicy` |
| Secrets | `SopsSecret` |
| Monitoring | `ServiceMonitor`, `PodMonitor`, `PrometheusRule` |
| PostgreSQL | `SGCluster`, `SGInstanceProfile`, `SGPostgresConfig`, `SGPoolingConfig`, `SGObjectStorage`, `SGBackup`, `SGDbOps`, `SGScript` |

The list is defined in `kubernetes/charts/project-onboarding/templates/resources.yaml`.
