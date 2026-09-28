# GITHUB_TOKEN viene del entorno: lo pone make con `gh auth token`.
provider "github" {
  owner = var.github_owner
}
