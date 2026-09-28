variable "github_owner" {
  type = string
}

variable "repository" {
  description = "Repo que ArgoCD va a leer, sin owner"
  type        = string
}

variable "environment" {
  description = "Nombre del cluster/entorno (prod, local); identifica la deploy key en GitHub"
  type        = string
}

variable "argocd_deploy_key_public" {
  description = "Clave pública SSH de la deploy key del entorno (live/<env>/deploy.key.pub)"
  type        = string
}
