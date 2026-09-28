# Uso:
#   make init                                 # preparar la máquina: herramientas, hooks, age.key
#   make connect ENV=prod                     # conectarse a un cluster que ya existe (.kube/<env>)
#   make cluster ENV=local                    # crear un cluster: infra (Terragrunt) + bootstrap (ArgoCD)
#   make bootstrap ENV=local                  # solo el bootstrap, sobre un cluster ya creado
#   make infra-plan  ENV=prod                 # todas las unidades del entorno, en orden de dependencias
#   make infra-plan  ENV=prod UNIT=cluster    # una unidad
#   make infra-apply ENV=prod UNIT=cluster    # aplica y te deja conectado
#   make infra-apply ENV=local                # cluster kind en Docker
#   make infra-destroy ENV=prod UNIT=cluster  # destruir una unidad (o todo el entorno sin UNIT); pide confirmación
#   make bootstrap-arc ENV=local              # cargar la credencial SOPS de la GitHub App de runners
#   make docs-diagram
#   make test-tutorials ENV=local             # los recorridos de tests/tutorials, rápidos y sin filmar
#   make tutorial-videos ENV=local            # los mismos recorridos, filmados: un MP4 por tutorial en var/tutorials/
#   make docs-serve                           # vista previa del sitio de documentación en http://127.0.0.1:8088
#   make docs-build                           # genera el sitio en site/
#
# ENV es obligatorio: el nombre de una carpeta de live/. UNIT es opcional.
# Los comandos se imprimen antes de correr: lo que ves es lo que se ejecuta.

UNIT ?=
CLUSTER_TIMEOUT ?= 1800

TG_DIR := live/$(ENV)/terraform$(if $(UNIT),/$(UNIT),)
TG_ALL := $(if $(UNIT),,run --all)

# Credenciales del entorno: los .env de live/<env>/secrets/, uno por proveedor. make resuelve la lista (puede ser vacía).
SECRETS := $(wildcard live/$(ENV)/secrets/*.env)

# Las descifra en memoria y las exporta al comando que sigue; nada queda en disco. Si un archivo no se puede
# descifrar, corta ahí (set -e). El token de GitHub lo da gh en el momento y no se guarda en ningún lado.
LOAD_SECRETS := set -ae; for f in $(SECRETS); do eval "$$(sops -d $$f)"; done; GITHUB_TOKEN="$$(gh auth token)"; set +ae;

KUBECTL  := kubectl --context $(ENV)
REPO_URL = $(shell uv run --script scripts/cluster-status.py repo-url --env "$(ENV)")

# Entornos con Cloudflare: los que tienen la unidad live/<env>/terraform/cloudflare (prod sí, local no).
CLOUDFLARE := $(wildcard live/$(ENV)/terraform/cloudflare)

# ARC se habilita por entorno agregando su overlay, igual que el resto de componentes.
ARC := $(wildcard live/$(ENV)/kubernetes/arc-runners/*/kustomization.yaml)

DOCS_DIR    := docs/resources
DIAGRAMS    := $(filter-out docs/diagrams/_common.py,$(wildcard docs/diagrams/*.py))

# Credenciales de los recorridos: se leen de los Secrets del cluster al correr y viajan por el entorno del
# proceso; lo que se imprime es el comando que las lee, nunca el valor.
TUTORIAL_ENV = KARGO_ADMIN_PASSWORD="$$($(KUBECTL) -n kargo get secret kargo-admin -o jsonpath='{.data.ADMIN_ACCOUNT_PASSWORD}' | base64 -d)"
TESTS ?= tutorials

.PHONY: init secrets connect cluster cluster-wait bootstrap bootstrap-cloudflare bootstrap-arc infra-plan infra-apply infra-destroy docs-diagram test-tutorials tutorial-videos docs-videos docs-serve docs-build

# Preparar la máquina: herramientas, hooks, y la clave de sops si no existe (age.key, ignorada por git).
init:
	@for tool in mise git ssh-keygen bash; do \
		command -v "$$tool" >/dev/null 2>&1 || { echo "Falta $$tool. Revisá los prerrequisitos de Quick start en README.md." >&2; exit 1; }; \
	done
	mise trust mise.toml
	mise install
	mise exec -- lefthook install
	mise exec -- bash scripts/init-sops
	@echo "⚠️  Hacé backup de age.key: sin ella no se puede descifrar nada de live/*/secrets/"

secrets:
	@test -n "$(FILE)" || { echo "Usage: make secrets FILE=path/to/secret"; exit 1; }
	mise exec -- bash scripts/edit-secret "$(FILE)"

# Deploy key del entorno: llave SSH con la que el cluster de ese entorno lee este repo (ignorada por git).
# Se genera la primera vez que se corre plan/apply del entorno; Terraform sube la pública a GitHub.
live/%/deploy.key:
	ssh-keygen -t ed25519 -N "" -C argocd-$* -f $@

# Muestra qué cambiaría. No toca nada.
infra-plan: live/$(ENV)/deploy.key
	$(LOAD_SECRETS) terragrunt $(TG_ALL) plan --working-dir $(TG_DIR)

# Aplica. Con UNIT, Terraform pide "yes"; sin UNIT, Terragrunt pide confirmación una vez por el grupo.
infra-apply: live/$(ENV)/deploy.key
	$(LOAD_SECRETS) terragrunt $(TG_ALL) apply --working-dir $(TG_DIR)
	$(MAKE) connect ENV=$(ENV)

# Destruye. Con UNIT, Terraform pide "yes"; sin UNIT, Terragrunt pide confirmación por el grupo. El state queda en el bucket.
infra-destroy: live/$(ENV)/deploy.key
	$(LOAD_SECRETS) terragrunt $(TG_ALL) destroy --working-dir $(TG_DIR)

# Conectarse a un cluster que ya existe: escribe .kube/<env> desde el state. mise lo pone en KUBECONFIG dentro del repo.
connect:
	mkdir -p .kube
	$(LOAD_SECRETS) terragrunt output -raw kubeconfig --working-dir live/$(ENV)/terraform/cluster > .kube/$(ENV)

# Secuencial incluso con make -j: validar → crear → bootstrap → esperar la plataforma.
cluster:
	uv run --script scripts/cluster-status.py check --env "$(ENV)"
	@echo "Creando infraestructura..."
	$(MAKE) infra-apply ENV=$(ENV) UNIT=
	@echo "Infraestructura lista. Instalando bootstrap..."
	$(MAKE) bootstrap ENV=$(ENV)
	$(MAKE) cluster-wait ENV=$(ENV)

# Retomar el seguimiento sin volver a ejecutar Terraform ni el bootstrap.
cluster-wait:
	uv run --script scripts/cluster-status.py wait --env "$(ENV)" --timeout "$(CLUSTER_TIMEOUT)"

# Lo mínimo que se instala a mano, una vez, para que el cluster se administre solo desde git:
#   1. la clave de sops, para que el operador de secretos descifre lo que ArgoCD le aplique
#   2. la deploy key del entorno, para que ArgoCD pueda leer este repo
#   3. ArgoCD y el operador, con los values de kubernetes/apps/ (helmfile; --wait: pods Ready antes de seguir)
#   4. el AppProject y el ApplicationSet de live/<env>/kubernetes/: desde acá ArgoCD sincroniza solo
# Si el entorno tiene Cloudflare, antes carga sus credenciales (bootstrap-cloudflare).
# Cada paso es idempotente (create --dry-run | apply).
bootstrap: $(if $(CLOUDFLARE),bootstrap-cloudflare) $(if $(ARC),bootstrap-arc)
	$(KUBECTL) create namespace argocd --dry-run=client -o yaml | $(KUBECTL) apply -f -
	$(KUBECTL) create namespace sops-secrets-operator --dry-run=client -o yaml | $(KUBECTL) apply -f -
	$(KUBECTL) -n sops-secrets-operator create secret generic sops-age --from-file=age.key --dry-run=client -o yaml | $(KUBECTL) apply -f -
	$(KUBECTL) -n argocd create secret generic repo-blackstorm-infra --from-literal=type=git --from-literal=url=$(REPO_URL) --from-file=sshPrivateKey=live/$(ENV)/deploy.key --dry-run=client -o yaml | $(KUBECTL) label --local -f - argocd.argoproj.io/secret-type=repository -o yaml | $(KUBECTL) apply -f -
	helmfile -f bootstrap/helmfile.yaml --kube-context $(ENV) sync --wait
	kubectl kustomize --enable-helm live/$(ENV)/kubernetes | $(KUBECTL) apply -f -

# Credenciales de Cloudflare al cluster: el token de API (cert-manager emite certificados, external-dns crea
# registros) y el token del túnel (cloudflared). Los valores van por stdin, nunca en la línea de comando.
bootstrap-cloudflare:
	$(KUBECTL) create namespace network --dry-run=client -o yaml | $(KUBECTL) apply -f -
	$(KUBECTL) create namespace cert-manager --dry-run=client -o yaml | $(KUBECTL) apply -f -
	$(LOAD_SECRETS) for ns in network cert-manager; do printf '%s' "$$CLOUDFLARE_API_TOKEN" | $(KUBECTL) -n $$ns create secret generic cloudflare-api-token --from-file=api-token=/dev/stdin --dry-run=client -o yaml | $(KUBECTL) apply -f -; done
	$(LOAD_SECRETS) terragrunt output -raw tunnel_token --working-dir live/$(ENV)/terraform/cloudflare | $(KUBECTL) -n network create secret generic cloudflared-token --from-file=token=/dev/stdin --dry-run=client -o yaml | $(KUBECTL) apply -f -

# El YAML contiene un Secret de Kubernetes, cifrado por .sops.yaml. Solo viaja descifrado por stdin.
# La GitHub App administra runners; esta credencial nunca se monta en los pods que ejecutan jobs.
bootstrap-arc:
	@test -n "$(ARC)" || { echo "ARC no está habilitado en live/$(ENV)/kubernetes/arc-runners/"; exit 1; }
	@test -f live/$(ENV)/secrets/github-arc.yaml || { echo "Falta live/$(ENV)/secrets/github-arc.yaml; ver docs/architecture/05-github-actions-runners.md"; exit 1; }
	$(KUBECTL) create namespace arc-runners --dry-run=client -o yaml | $(KUBECTL) apply -f -
	sops -d live/$(ENV)/secrets/github-arc.yaml | $(KUBECTL) apply -f -

# Genera los PNG de docs/diagrams/: Graphviz para grafos y librsvg para layouts explícitos con los mismos iconos.
docs-diagram:
	@command -v rsvg-convert >/dev/null || { echo "Falta librsvg: brew install librsvg"; exit 1; }
	@command -v dot >/dev/null || { echo "Falta Graphviz: brew install graphviz"; exit 1; }
	@for d in $(DIAGRAMS); do \
		PYTHONDONTWRITEBYTECODE=1 uvx --with diagrams python $$d && echo "$(DOCS_DIR)/$$(basename $${d%.py}).png"; \
	done

# Los recorridos de tests/tutorials como tests: manejan las interfaces del cluster por el navegador y validan
# el proceso que enseñan. Cambian el cluster de verdad (el de Kargo promueve a production): solo corren en local.
#   make test-tutorials ENV=local TESTS=tutorials/test_kargo_promote.py
test-tutorials:
	@command -v uv >/dev/null || { echo "Falta uv: brew install uv"; exit 1; }
	cd tests && $(TUTORIAL_ENV) uv run pytest $(TESTS) --headless -v

# Los mismos recorridos en modo demo, contra un Chrome en Docker que se filma (tests/docker-compose.yml).
# Un MP4 1920x1080 por tutorial en var/tutorials/, recortado donde el test marca inicio y fin.
#   make tutorial-videos ENV=local VIDEO=0    # en demo y con el navegador a la vista, sin filmar
tutorial-videos:
	@command -v uv >/dev/null || { echo "Falta uv: brew install uv"; exit 1; }
	$(TUTORIAL_ENV) TESTS='$(TESTS)' VIDEO='$(VIDEO)' tests/tutorial-videos

# Sitio de documentación: MkDocs Material sobre docs/ (mkdocs.yml). Los videos no están en git:
# se copian de var/tutorials/ a docs/videos/ antes de servir o generar, cada uno con su miniatura
# (un cuadro al 40 % de la duración).
# Versiones acotadas: MkDocs 2.0 rompe temas y plugins, y Material 9 es la última línea del tema.
DOCS_SITE := uvx --from 'mkdocs<2' --with 'mkdocs-material<10' --with mkdocs-glightbox mkdocs
DOCS_ADDR ?= 127.0.0.1:8088

docs-videos:
	@mkdir -p docs/videos
	@for v in var/tutorials/*.mp4; do \
		[ -f "$$v" ] || continue; \
		command -v ffmpeg >/dev/null || { echo "Falta ffmpeg: brew install ffmpeg"; exit 1; }; \
		cp "$$v" docs/videos/; \
		at=$$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$$v" | LC_ALL=C awk '{ printf "%.1f", $$1 * 0.4 }'); \
		ffmpeg -nostdin -v error -y -ss "$$at" -i "$$v" -frames:v 1 -vf scale=960:-1 -q:v 3 "docs/videos/$$(basename "$${v%.mp4}").jpg"; \
	done

docs-serve: docs-videos
	$(DOCS_SITE) serve --dev-addr $(DOCS_ADDR)

docs-build: docs-videos
	$(DOCS_SITE) build --strict
