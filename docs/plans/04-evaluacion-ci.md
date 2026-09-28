# Evaluación de CI: Actions, Jenkins y Tekton

Evaluación documental del 2026-09-26. Decisión posterior: **GitHub Actions con runners propios para
esta etapa**. La comparación se conserva como fundamento; la prueba del runner está pendiente.
No se midieron consumo, tiempos de build ni esfuerzo de operación.

## Requisitos usados para las tres opciones

- Repos privados de proyectos propios en `blackstorm-dev`; la organización sigue en GitHub Free
  (comprobado con `gh api orgs/blackstorm-dev --jq .plan.name`).
- Builds en infraestructura propia, también si elegimos GitHub Actions.
- Alta de un proyecto sin commits específicos en `blackstorm-infra` ni creación manual de jobs.
- Se acepta un alta inicial de credenciales y repositorios de imágenes por proyecto. Generar el
  token automáticamente no es un requisito; su alcance efectivo lo debe aplicar el registry.
- Proyectos con necesidades diferentes: varios lenguajes, tests de integración, monorepos y varias
  imágenes. El template ofrece una base que el equipo puede adaptar.
- Configuración de plataforma reproducible; secretos de infra con el mecanismo SOPS existente.
- Kargo para promoción y ArgoCD para sincronizar despliegues, con el mismo digest entre entornos.
  Esta capa debe funcionar independientemente de la CI elegida.

## Comparación

| Criterio | Actions + runners propios | Jenkins + agentes propios | Tekton + Pipelines-as-Code |
|---|---|---|---|
| Quién opera el servicio de CI | GitHub; nosotros los runners | Nosotros | Nosotros sobre Kubernetes |
| Entrada habitual del proyecto | `.github/workflows/*.yaml` | `Jenkinsfile` | `.tekton/*.yaml` con PipelineRuns |
| Alta de CI | El workflow ya existe al crear el repo desde el template; requiere acceso a los runners | Organization Folder descubre repos elegibles y crea jobs | GitHub App; auto-configuración opcional de namespace y Repository |
| Reutilización | Workflows reutilizables y acciones | Shared Libraries; también pipeline administrado centralmente con configuración adicional | Tasks y Pipelines compartidos/remotos |
| Adaptar proyectos complejos | Jobs, dependencias, matrices y servicios de test | Etapas, paralelismo, librerías y agentes específicos | DAG de Tasks, parámetros, workspaces y contenedores |
| Qué mantenemos | Runners, imágenes de ejecución, capacidad, acceso, cachés y builder | Lo anterior más controller, plugins, configuración y persistencia de Jenkins | Pipelines, PaC, permisos, espacios de ejecución, almacenamiento y conservación de resultados; Dashboard si queremos panel propio |
| Experiencia del dev | Ejecuciones y logs dentro de GitHub | Jenkins como interfaz de CI, integrado con GitHub | Checks en GitHub y detalles de ejecución en Tekton/CLI/Dashboard |

Las tres pueden cumplir el alta sin un commit por proyecto después de configurar la plataforma.
Eso no implica que las tres aprovisionen automáticamente credenciales del registry o recursos de CD.

Actions permite reutilizar workflows entre repos y pasarles parámetros y secretos. Jenkins ofrece
descubrimiento mediante Organization Folder y agentes temporales en pods. PaC también permite
pipelines remotos y puede crear namespace y Repository para nuevos repos de GitHub; esa opción
no configura Docker Hub, Kargo o los namespaces de despliegue.
[Actions](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows),
[Jenkins: descubrimiento](https://www.jenkins.io/doc/book/pipeline/pipeline-as-code/),
[Jenkins: agentes](https://plugins.jenkins.io/kubernetes/),
[PaC: auto-configuración](https://pipelinesascode.com/docs/api/configmap/),
[PaC: pipelines remotos](https://pipelinesascode.com/docs/guides/pipeline-resolution/remote-pipelines/).

## Un proyecto complejo, bajo el mismo contrato

Caso de comparación: un repo con API y worker, tests que usan PostgreSQL y dos imágenes que deben
avanzar juntas por staging y producción. No se implementó todavía este caso de prueba.

1. El equipo crea el repo desde el template y adapta los tests, dependencias y builds de API/worker.
2. Recibe y configura las credenciales y destinos autorizados del registry una vez.
3. La CI ejecuta los tests y produce las dos imágenes, sus digests y la referencia al código fuente.
4. Kargo debe reconocer una versión elegible con ambas imágenes, promoverla y verificarla.
5. ArgoCD sincroniza el estado deseado del entorno correspondiente.

Con Actions el equipo compone jobs y puede reutilizar nuestro job de publicación; con Jenkins
compone etapas y puede usar nuestra librería; con Tekton compone Tasks/Pipelines. La complejidad
del proyecto no desaparece en ninguna opción. Una pipeline impuesta centralmente traslada parte
de ese trabajo al equipo de plataforma y exige un contrato de extensiones.

La propuesta es estandarizar la **salida de CI** —imágenes por digest, vínculo al commit y criterio
de versión elegible— y proporcionar piezas reutilizables. El piloto de una sola app no debe
convertirse en una obligación de tener un único Dockerfile, una única imagen o un único comando
de tests para todos los proyectos. Kargo admite conjuntos de artefactos en un Freight; queda por
diseñar cómo correlacionar imágenes de la misma versión y evitar promover builds incompletos.
[Modelo de artefactos y promoción de Kargo](https://docs.kargo.io/user-guide/core-concepts).

## Diferencias que afectan a nuestra plataforma

**Actions con runners propios sigue dependiendo del servicio de GitHub.** ARC administra y escala
runners temporales en Kubernetes; GitHub coordina los jobs y recibe estados y logs. No necesitamos
crear un runner por repo: puede haber capacidad compartida a nivel organización, con una política
de acceso que incluya los repos nuevos. Una lista manual de repos permitidos añadiría un paso de alta.
[ARC](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller),
[acceso a runners](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access).

**Jenkins es válido aunque el código esté en GitHub.** Su ventaja para nosotros sería controlar
también el servicio de CI y aprovechar la experiencia previa de Tomás. JCasC permite configuración
como código; el descubrimiento se configura una vez. Aun así, debemos mantener plugins, controller
y respaldos de su estado. Conservar GitHub como origen del código sigue introduciendo dependencia
de GitHub para operaciones como clonar o recibir eventos.
[JCasC](https://www.jenkins.io/doc/book/managing/casc/),
[respaldo de Jenkins](https://www.jenkins.io/doc/book/system-administration/backing-up/).

**Tekton es una alternativa viable.** Tasks, Pipelines y ejecuciones son recursos de Kubernetes;
PaC aporta la integración con GitHub. Las credenciales se proporcionan mediante Secrets y
ServiceAccounts. Si cada repo recibe su propio namespace de CI, hace falta automatizar o documentar
la provisión de esas credenciales y permisos. Para este equipo, aprender ese modelo y operarlo
supone trabajo adicional frente a Actions o al Jenkins que ya conoce Tomás; es una valoración de
encaje, no una limitación de capacidad ni un benchmark.
[Pipelines](https://tekton.dev/docs/pipelines/pipelines/),
[autenticación](https://tekton.dev/docs/pipelines/auth/),
[instalación e integración de PaC](https://pipelinesascode.com/docs/getting-started/).

**Compartir una pipeline no obliga a usarla.** Debemos distinguir una base reutilizable de una
política que el dev no puede eludir. GitHub Free no ofrece protección de ramas en nuestros repos
privados de organización; requiere Team o Enterprise. Tampoco permite consumir secretos de
organización desde repos privados: sí podemos configurar secretos por repo. Un workflow reutilizable
no obtiene automáticamente los secretos del repo donde está definido. Elegir Jenkins o Tekton
tampoco cambia las protecciones del repositorio alojado en GitHub.
[Protecciones](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches),
[secretos](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

**El entorno de build debe probarse.** El workflow actual en `projects/project-template/` usa `ubuntu-latest`, Docker
para construir y ejecutar la imagen, Python y curl. El runner mínimo de ARC no equivale a esa imagen
de GitHub. Hay que preparar herramientas, builder y pruebas de integración. El modo Docker-in-Docker
documentado por ARC requiere privilegios; elegir ese modo afecta dónde aislamos los builds.
Jenkins y Tekton también necesitan resolver el builder. Runners temporales no bastan por sí solos
para aislar proyectos: los builds no deben recibir la clave age general ni permisos de administración.
[Imagen de runner de ARC](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller),
[modos de ejecución](https://docs.github.com/en/actions/how-tos/manage-runners/use-actions-runner-controller/deploy-runner-scale-sets).

El archivo `live/prod/terraform/cluster/terragrunt.hcl` declara un nodo de 1 vCPU y 2 GB. No se comprobó
capacidad libre en vivo. Antes de usarlo para CI hay que medir consumo y decidir capacidad/aislamiento;
no se presupone que alcance para builds y aplicaciones. No se estiman precios ni tiempos sin medir.

## Alta de despliegues: trabajo común pendiente

ApplicationSet puede descubrir repos de una organización con el generador SCM. Se configura una
regla de descubrimiento una vez; no una lista de cada aplicación en infra. Todavía hay que implementar
y validar la plantilla que genera recursos administrativos, permisos de Kargo/ArgoCD y namespaces
desde la declaración del proyecto. Un topic sirve como señal, no como frontera de autorización.
Este trabajo existe con cualquiera de las tres CI. La UI de promociones de Kargo también se conserva
con las tres. [Generador SCM](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-SCM-Provider/).

## Recomendación y criterios para revisarla

**Recomiendo Actions con runners propios**, con workflows adaptables y piezas reutilizables mantenidas
por plataforma. Para Kubernetes, ARC es el candidato a probar. La razón es que ya elegimos GitHub,
aceptamos credenciales por proyecto y queremos permitir pipelines diferentes, mientras Kargo cubre
promoción. Podemos operar los ejecutores sin asumir además todo el servicio de CI.

- **Elegiría Jenkins** si controlar el servicio de CI o ejecutar pipelines administrados fuera del
  repo de la app pesa más que el mantenimiento adicional. La experiencia previa reduce su barrera de entrada.
- **Elegiría Tekton + PaC** si queremos explícitamente que la CI sea una API de Kubernetes, con
  Tasks/Pipelines y políticas integradas en ese modelo, y aceptamos construir esa experiencia de plataforma.
- Proyectos complejos, runners propios, GitOps o alta sin commits por aplicación **no obligan por sí
  solos** a elegir Jenkins o Tekton. Ninguna opción resuelve por sí misma el alcance del token de Docker Hub.

## Prueba que falta para validar la elección

1. Preparar un runner temporal propio y comprobar el workflow existente: tests, build, publicación y
   health check por digest. Documentar herramientas, autenticación, capacidad y limpieza del runner.
2. Crear un segundo repo desde el template y ejecutar la CI sin editar infra ni crear jobs o runners
   por aplicación; solo el alta inicial de credenciales y destinos que acordamos aceptar.
3. Extender ese segundo caso a dos imágenes y tests con un servicio auxiliar, cambiando únicamente
   el proyecto; comprobar reintentos, logs y que un fallo no produce una versión elegible para promover.
4. Validar después Kargo + ArgoCD y el alta de entornos automática como trabajo independiente de CI.

La ejecución de esa prueba sigue pendiente. El primer paso está documentado en
[GitHub Actions: primer runner propio](../architecture/05-github-actions-runners.md).
