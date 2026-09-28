# Lo que ArgoCD necesita fuera del cluster. Hoy: una llave de solo lectura para leer este repo.
# El par lo genera make (live/<env>/deploy.key, gitignored); la privada entra al cluster en el bootstrap.
module "deploy_key" {
  source = "../../resources/github/deploy-key"

  repository = var.repository
  title      = "argocd-${var.environment}"
  public_key = var.argocd_deploy_key_public
  read_only  = true
}
