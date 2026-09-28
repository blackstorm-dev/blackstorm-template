# GitHub Actions · primer runner propio

Estado: GitHub App registrada e instalada; credencial guardada con SOPS y cargada en `local`.
Manifiestos y workflow preparados para revisión, todavía sin publicar ni ejecutar el job remoto.
Se habilita únicamente en `local`; la capacidad y el builder de prod se diseñan después.
Este primer paso verifica checkout y shell, sin credenciales de Docker Hub.

Setup actual: App `blackstorm-dev-runners`, App ID `5090490`, Installation ID `165281471`.
Una reproducción en otra organización debe usar sus propios IDs y private key.

## Qué se instala

- ARC `0.14.2` en `arc-systems`: administra runners temporales con los charts oficiales de GitHub.
- Un scale set de organización en `arc-runners`, con nombre GitHub `blackstorm-local`.
- De cero a un runner simultáneo, imagen `ghcr.io/actions/actions-runner:2.337.0`.
- El job corre sin token de Kubernetes. La credencial de administración de runners queda fuera del pod del job.

GitHub coordina las ejecuciones y conserva sus logs. ARC recibe trabajo mediante conexiones
salientes: este setup no necesita exponer un webhook del cluster ni un nuevo hostname.
[Funcionamiento de ARC](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller).

## 1. Registrar la GitHub App una vez

Entrar con la cuenta que administra `blackstorm-dev` a
[Settings → Developer settings → GitHub Apps → New GitHub App](https://github.com/organizations/blackstorm-dev/settings/apps/new).

| Campo | Valor |
|---|---|
| Nombre | `blackstorm-dev-runners` (si está ocupado, elegir otro nombre; no afecta los manifests) |
| Homepage URL | `https://github.com/blackstorm-dev/blackstorm-infra` |
| Webhook | Desactivar **Active** |
| Repository permissions | Solo Metadata: Read-only, si aparece; no otorgar acceso a Contents ni Administration |
| Organization permissions | **Self-hosted runners: Read and write** |
| Dónde se puede instalar | Solo esta cuenta/organización |

Crear la App, anotar **App ID**, generar su private key y descargar el `.pem`. En **Install App**,
instalarla en `blackstorm-dev`. Si pide selección de repos, elegir todos los de la organización para
que el alta de repos nuevos no requiera reinstalarla. Anotar el **Installation ID**, visible al final
de la URL `https://github.com/organizations/blackstorm-dev/settings/installations/<id>`.

Es una App de administración de runners. La lectura del código de cada job la realiza el token
de Actions del propio repo. No es la App que definiremos para el descubrimiento de despliegues.
[Permisos oficiales de ARC a nivel organización](https://docs.github.com/en/actions/how-tos/manage-runners/use-actions-runner-controller/authenticate-to-the-api).

## 2. Guardar la credencial cifrada en infra

Desde este repo, con mise activado y `age.key` disponible:

```bash
mkdir -p live/local/secrets
sops live/local/secrets/github-arc.yaml
```

En el editor de SOPS, reemplazar el contenido por este Secret y completar los valores. Mantener los
IDs entre comillas y pegar el contenido completo del `.pem` con la indentación del bloque:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: github-arc
  namespace: arc-runners
type: Opaque
stringData:
  github_app_id: "APP_ID"
  github_app_installation_id: "INSTALLATION_ID"
  github_app_private_key: |
    PEGAR_EL_PEM_COMPLETO_AQUI
```

Al guardar y cerrar, SOPS cifra `stringData` según `.sops.yaml`. El YAML cifrado se versiona en infra;
el `.pem` original y `age.key` no se agregan a Git. Esto usa la misma clave age que el resto de infra.
La App y su clave se crean una vez, no por proyecto.

## 3. Conectar y sincronizar local

Antes de publicar los cambios en infra y en el checkout independiente `projects/project-template/`, revisar ambos
diffs. ArgoCD lee `main` remoto: no ve archivos que solo están en la máquina.

Cargar la credencial desde el archivo cifrado:

```bash
make bootstrap-arc ENV=local
```

El target crea el namespace y descifra el Secret hacia Kubernetes por stdin. `make bootstrap ENV=local`
también lo incluye cuando existe el overlay de runners. No usa ni almacena el token personal de `gh`.
Con los cambios publicados, el ApplicationSet de plataforma descubre las dos carpetas nuevas y
sincroniza ARC. Si todavía no las detectó, esperar su siguiente reconciliación.

```bash
kubectl --context local -n argocd get applications
kubectl --context local -n arc-systems get pods
kubectl --context local -n arc-runners get autoscalingrunnersets,pods
```

Se espera el controller Ready y un listener activo. Con `minRunners: 0`, no debe haber un runner
ocioso permanente. El chart de scale set tiene explícito el ServiceAccount del controller para
poder renderizarse sin consultar un ARC ya instalado. Ambos charts fijan la misma versión.

En GitHub → organización → **Settings → Actions → Runner groups**, comprobar que el grupo usado
por ARC permite los repos privados de la organización. Permitir todos evita una alta por repo;
limitarlo al piloto sirve para una prueba, pero no valida todavía el autoservicio. La política de
acceso a runners es distinta de los permisos de la GitHub App.
Se verificó mediante la App que el grupo `Default` (ID `1`) tiene acceso a todos los repos privados
(`visibility: all`, `allows_public_repositories: false`). No fue necesario ampliar el alcance del
token personal de `gh` ni cambiar esa política.

## 4. Probar el recorrido completo de un job

El checkout independiente contiene `.github/workflows/runner-check.yaml`, de ejecución manual.
Cuando ese archivo esté publicado en el `main` del template:

```bash
cd projects/project-template
gh workflow run runner-check.yaml --ref main
gh run list --workflow runner-check.yaml --limit 5
gh run watch <run-id> --exit-status
```

En otra terminal, desde infra:

```bash
kubectl --context local -n arc-runners get pods --watch
```

Se espera que aparezca un runner, complete checkout y las comprobaciones de shell y se elimine
al terminar. El listener permanece. GitHub muestra el resultado y el resumen del job.
El runner usa la arquitectura del nodo: en la Mac actual, Linux ARM64. Esta prueba no certifica
todavía builds para Linux AMD64 ni disponibilidad de Python o Docker en la imagen del runner.

Si el job queda en cola, comprobar el listener, el acceso del repo al grupo y `runs-on: blackstorm-local`.
Si el listener no aparece o muestra errores 401/403, revisar IDs, instalación y permiso de runners de
la App. La Mac y Docker Desktop deben estar encendidos durante esta prueba local.

## Qué sigue después de este hito

1. Preparar el entorno de tests y el builder; migrar `ci.yaml` a los runners propios. Hoy sigue usando
   `ubuntu-latest`, sin haber cambiado el comportamiento del piloto durante esta preparación.
2. Configurar el token de Docker Hub por proyecto y validar tests → build → imagen por digest.
3. Crear otro repo desde el template y comprobar que no requiere cambios en infra.
4. Conectar promoción con Kargo y despliegue con ArgoCD según el contrato de entornos.

Las versiones de chart e imagen se actualizan mediante cambios revisables en Git. La imagen del
runner debe mantenerse compatible con GitHub Actions; fijarla hace el setup reproducible, no elimina
su mantenimiento. La rotación de la private key se carga editando el Secret con SOPS y repitiendo
`make bootstrap-arc ENV=local`; se verifica la conexión antes de revocar la clave anterior.
