# Secrets

Secrets stay encrypted in your repository. You edit them with one command.

| Kind | Path | Read by |
|---|---|---|
| CI | `secrets/*.env` | GitHub Actions |
| Deployment | `deploy/<environment>/secrets/*.yaml` | Your application |
| Promotion | `secrets/platform/*.yaml` | Kargo, to read your private images |

## Initialize encryption

Run `make init` in your own application repository. It creates an age key, configures `.sops.yaml`,
and uploads the private key to that repository's `SOPS_AGE_KEY` GitHub secret.

Before encrypting files under `deploy/*/secrets/` and `secrets/platform/`, add the cluster's **public**
age recipient to the corresponding `.sops.yaml` rules, alongside your project's recipient.
Obtain it from the platform operator; the cluster needs it to decrypt these files. Keep CI-only
credentials encrypted for the project. Never exchange private age keys.

## Create or edit a secret

```bash
make secrets FILE=<path> # (1)!
```

1.  Creates the encrypted file from its `*.example` if needed, then opens your editor.
    Replace the placeholders and save. Commit the encrypted file; keep the example unchanged.

=== "CI"

    ```bash
    make secrets FILE=secrets/dockerhub.env
    ```

    ```dotenv title="secrets/dockerhub.env"
    DOCKERHUB_USERNAME=…
    DOCKERHUB_TOKEN=…
    ```

=== "Deployment"

    ```bash
    make secrets FILE=deploy/staging/secrets/app.yaml
    ```

    ```yaml title="deploy/staging/secrets/app.yaml"
    apiVersion: isindir.github.com/v1alpha3
    kind: SopsSecret
    metadata:
      name: app
    spec:
      secretTemplates:
        - name: app # (1)!
          stringData:
            DATABASE_PASSWORD: …
    ```

    1.  The name of the `Secret` your application reads.

=== "Promotion"

    ```bash
    make secrets FILE=secrets/platform/dockerhub.yaml
    ```

    ```yaml title="secrets/platform/dockerhub.yaml"
    apiVersion: isindir.github.com/v1alpha3
    kind: SopsSecret
    metadata:
      name: dockerhub
      namespace: my-app
    spec:
      secretTemplates:
        - name: dockerhub
          labels:
            kargo.akuity.io/cred-type: image # (1)!
          stringData:
            repoURL: docker.io/<namespace>/my-app
            username: …
            password: …
    ```

    1.  Tells Kargo this credential is for an image repository.

## Use it in your application

```yaml title="deploy/base/deployment.yaml"
metadata:
  annotations:
    secret.reloader.stakater.com/auto: "true" # (1)!
spec:
  template:
    spec:
      containers:
        - name: app
          envFrom:
            - secretRef:
                name: app
```

1.  The application restarts on its own when the secret changes.

## Rotate a credential

1. Create the new credential at the provider.
2. `make secrets FILE=<path>` and replace the value.
3. Commit and push.
4. Revoke the old credential.

!!! danger "Never commit `age.key`"

    Keep a copy somewhere safe. Without it, your encrypted files cannot be read.
