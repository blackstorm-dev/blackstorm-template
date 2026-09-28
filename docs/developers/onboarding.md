# Onboard a repository

Staging deploys automatically. Production receives the release when you promote it in Kargo.

## Before you start

| You need | Detail |
|---|---|
| A repository in the platform's configured GitHub organization | Lowercase letters, digits, and hyphens; starts with a letter; up to 50 characters |
| Read access for the GitOps GitHub App | Ask an operator |
| A private Docker Hub repository | Same name as the GitHub repository |

## Steps

### 1. Create the repository

```bash
gh repo create YOUR_ORG/my-app --private \
  --template blackstorm-dev/blackstorm-project-template --clone
cd my-app
```

### 2. Create your key

```bash
make init # (1)!
```

1.  Creates `age.key`, registers its public part in `.sops.yaml`, and uploads the private part
    to GitHub as `SOPS_AGE_KEY`.

### 3. Add your registry credentials

Create the CI, promotion, and deployment secrets from their `*.example` files.
Deployment secrets must include the cluster's public age recipient. See [Secrets](secrets.md).

### 4. Declare the contract

```yaml title="deploy/platform.yaml"
releaseFormat: commit-sha # (1)!
images:
  - repository: docker.io/<namespace>/my-app # (2)!
    name: <namespace>/my-app # (3)!
environments:
  staging:
    path: deploy/staging
    promotion: automatic
  production:
    path: deploy/production
    promotion: manual
    from: staging # (4)!
```

1.  How CI names a release. See [Continuous integration](ci.md).
2.  Every image that makes up a release.
3.  The name your manifests use for that image.
4.  Production only receives releases that staging verified.

### 5. Set your hostnames

```yaml title="deploy/staging/kustomization.yaml" hl_lines="11 12"
patches:
  - target:
      kind: HTTPRoute
      name: app
    patch: |-
      apiVersion: gateway.networking.k8s.io/v1
      kind: HTTPRoute
      metadata:
        name: app
      spec:
        hostnames:
          - my-app-staging.localhost
```

Do the same in `deploy/production/kustomization.yaml`.

Use the image name in `deploy/base/deployment.yaml` that matches `deploy/platform.yaml`,
and configure the runner label in `.github/workflows/ci.yaml` for your platform.

### 6. Turn discovery on

Replace `YOUR_DISCOVERY_TOPIC` with `github.discoveryTopic` from the target cluster configuration.

```bash
gh repo edit --add-topic YOUR_DISCOVERY_TOPIC
git add -A && git commit -m "Configure application" && git push
```

## Check it worked

=== "Browser"

    Your project shows up in [Kargo](https://kargo.localhost:8443/) and in
    [Argo CD](https://argocd.localhost:8443/).

=== "Terminal"

    ```bash
    kubectl --context local -n argocd get applications | grep my-app
    ```

    ```text
    my-app-onboarding    Synced   Healthy
    my-app-kargo         Synced   Healthy
    my-app-staging       Synced   Healthy
    my-app-production    Synced   Healthy
    ```
