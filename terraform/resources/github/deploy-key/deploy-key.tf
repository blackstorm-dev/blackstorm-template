resource "github_repository_deploy_key" "this" {
  repository = var.repository
  title      = var.title
  key        = var.public_key
  read_only  = var.read_only
}
