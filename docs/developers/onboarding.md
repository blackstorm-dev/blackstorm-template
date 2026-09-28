# Onboard a repository

You end up with a staging and a production environment that deploy on their own.

## Before you start

| You need | Detail |
|---|---|
| A repository in `blackstorm-dev` | Lowercase letters, digits, and hyphens; starts with a letter; up to 50 characters |
| Read access for the GitOps GitHub App | Ask an operator |
| A private Docker Hub repository | Same name as the GitHub repository |

## Steps

### 1. Create the repository

```bash
gh repo create blackstorm-dev/my-app --private \
  --template blackstorm-dev/project-template --clone
cd my-app
```

### 2. Create your key

```bash
make init # (1)!
```

1.  Creates `age.key`, registers its public part in `.sops.yaml`, and uploads the private part
    to GitHub as `SOPS_AGE_KEY`.

### 3. Add your registry credentials

Three files, all encrypted. See [Secrets](secrets.md).

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

### 6. Turn discovery on

```bash
gh repo edit --add-topic blackstorm-deploy
git push
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
