# GitHub y template de proyectos

## Organización y repo de infraestructura

La instalación actual usa `blackstorm-dev/blackstorm-infra`. Para una instalación nueva, crear la
organización en GitHub con la cuenta que será su owner y autenticar `gh auth login` con esa cuenta.
La creación de la organización es un paso manual en GitHub. Comprobar la membresía:

```bash
gh api user/memberships/orgs/blackstorm-dev --jq '{role,state}'
```

ArgoCD lee este repo con deploy keys de solo lectura, una por cluster. En una organización nueva
pueden estar deshabilitadas aunque las llaves existan. Habilitar y verificar:

```bash
gh api --method PATCH orgs/blackstorm-dev -F deploy_keys_enabled_for_repositories=true \
  --jq '{login,deploy_keys_enabled_for_repositories}'
gh api repos/blackstorm-dev/blackstorm-infra/keys \
  --jq '[.[] | {title,enabled,read_only}]'
```

Esta opción afecta a los repositorios de la organización. Las llaves se crean con el módulo
Terraform de ArgoCD; `make bootstrap ENV=<env>` carga la clave privada en el cluster.

## Trasladar un repo existente: procedimiento opcional

Para trasladar un repositorio desde una cuenta personal a la organización:

1. Verificar permisos de administración del origen, membresía de owner en el destino y nombre libre.
2. Preparar el cambio de owner/URL en `Makefile`, `README.md`, `live/*/terraform/argocd/terragrunt.hcl`
   y `live/*/kubernetes/{appproject,applicationset}.yaml`. Buscar referencias con
   `rg -n 'example-user' Makefile README.md live` (sustituir por el owner anterior).
3. Transferir el repo y comprobar su nuevo `full_name`:

   ```bash
   gh api --method POST repos/example-user/blackstorm-infra/transfer -f new_owner=blackstorm-dev
   gh api repos/blackstorm-dev/blackstorm-infra --jq '{full_name,private,default_branch}'
   git remote set-url origin https://github.com/blackstorm-dev/blackstorm-infra.git
   ```

4. Commitear y subir los cambios de URLs. Habilitar las deploy keys en la org como arriba.
5. Actualizar la URL del Secret existente y los recursos raíz de ArgoCD, para cada cluster activo:

   ```bash
   for cluster_env in local prod; do
     kubectl --context "$cluster_env" -n argocd patch secret repo-blackstorm-infra --type merge \
       -p '{"stringData":{"url":"git@github.com:blackstorm-dev/blackstorm-infra.git"}}'
     kubectl --context "$cluster_env" apply -k "live/$cluster_env/kubernetes"
     kubectl --context "$cluster_env" -n argocd annotate applicationset platform \
       argocd.argoproj.io/application-set-refresh=true --overwrite
   done
   ```

   El patch conserva la deploy key existente. Durante el cambio puede haber errores temporales de
   reconciliación hasta que el ApplicationSet actualice las Applications.
6. Verificar Applications, condiciones del ApplicationSet y planes de las deploy keys:

   ```bash
   kubectl --context prod -n argocd get applications
   kubectl --context local -n argocd get applications
   make infra-plan ENV=prod UNIT=argocd
   make infra-plan ENV=local UNIT=argocd
   ```

   En el traslado actual ambos planes dieron `No changes`; no hubo que recrear las llaves.
   Si aparece `repository not found`, revisar primero `enabled` en las deploy keys y la URL del repo.

## Template y checkout independiente

El repo `blackstorm-dev/project-template` es privado y tiene `is_template: true`. Se creó una vez con:

```bash
gh api --method POST orgs/blackstorm-dev/repos \
  -f name=project-template -F private=true -F is_template=true
```

Para trabajar en él desde una máquina nueva, ejecutar desde la raíz de infraestructura:

```bash
gh repo clone blackstorm-dev/project-template projects/project-template
git check-ignore projects/project-template/
git -C projects/project-template remote -v
```

`projects/` está ignorado por infraestructura y cada checkout contiene su propio `.git`. El primer código se
preparó localmente y se publicó con `git remote add origin` y `git push -u origin main`; una vez
publicado, el clone anterior reproduce el checkout sin reconstruir esos commits.

Los cambios del template se commitean y suben desde `projects/project-template/`. Los cambios de infraestructura se
commitean desde la raíz. Ambos repos tienen su historial y deben quedar publicados para que otra
máquina pueda reproducir el estado documentado.

## Docker Hub y CI

Seguir el [README del template](https://github.com/blackstorm-dev/project-template/blob/main/README.md):
crear el repositorio privado en Docker Hub, generar un PAT Read & Write y cargar manualmente
los dos secrets y la variable en GitHub → Settings → Secrets and variables → Actions.
El README detalla los campos y valores. La configuración se realiza en cada repo creado desde el template.

La CI puede dispararse manualmente después del setup. Prueba la app, publica una imagen, la descarga
por digest y verifica `/healthz`. El README incluye los comandos para observar la ejecución,
probar la imagen localmente y rotar el token. La publicación inicial sigue pendiente hasta cargar
las credenciales de Docker Hub y obtener una ejecución completa exitosa.

## Referencias

- [GitHub: restricciones de deploy keys](https://docs.github.com/en/organizations/managing-organization-settings/restricting-deploy-keys-in-your-organization)
- [GitHub: transferencia de repositorios](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository)
- [Docker: crear repositorios](https://docs.docker.com/docker-hub/repos/create/)
- [Docker: personal access tokens](https://docs.docker.com/security/access-tokens/personal-access-tokens/)
