# GitHub y template de proyectos

## Repositorio de infraestructura

El template de infraestructura está en `blackstorm-dev/blackstorm-template`. Cada instalación
usa su propio repositorio: configurar `github.organization` y `github.infrastructureRepository`
en `live/<env>/config/values.yaml` y publicar ahí la configuración y los secretos cifrados.

Argo CD accede mediante una deploy key de solo lectura por clúster. Si la organización restringe
las deploy keys, su administrador debe habilitarlas. Terraform crea la llave y registra la pública;
`make bootstrap ENV=<env>` carga la privada en el clúster.

## Template de aplicaciones

`blackstorm-dev/blackstorm-project-template` es un GitHub template y se incluye como submódulo
en `projects/project-template/`. Para descargar la versión fijada por infraestructura:

```bash
git submodule update --init --recursive
```

Para crear una aplicación propia:

```bash
gh repo create YOUR_ORG/my-app --private \
  --template blackstorm-dev/blackstorm-project-template --clone
```

Los cambios del template se commitean dentro del submódulo. Después se actualiza su referencia
en el repositorio de infraestructura. Los demás checkouts bajo `projects/` quedan ignorados.

## Credenciales y CI

Seguir el [README del template](https://github.com/blackstorm-dev/blackstorm-project-template).
`make init` genera la clave age y configura `SOPS_AGE_KEY` en el repositorio nuevo. Docker Hub
se configura con `make secrets FILE=secrets/dockerhub.env` y la variable `DOCKERHUB_NAMESPACE`.
Los archivos `.example` contienen placeholders; los archivos reales se guardan cifrados.

Los pull requests no disparan workflows. Un mantenedor puede ejecutar los checks manualmente;
los pushes a las ramas configuradas ejecutan el flujo de publicación. Los runners y las GitHub Apps
deben tener acceso al repositorio nuevo. La clave pública age del clúster se agrega a las reglas
SOPS de los secretos de despliegue y promoción para que sus controladores puedan descifrarlos.
