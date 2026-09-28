include "root" {
  path = find_in_parent_folders("root.hcl") # el de live/local/terraform/
}

locals {
  config = yamldecode(file("${get_terragrunt_dir()}/../../config/values.yaml"))
}

terraform {
  source = "../../../../terraform//modules/argocd"
}

inputs = {
  github_owner             = local.config.github.organization
  repository               = local.config.github.infrastructureRepository
  environment              = local.config.environment
  argocd_deploy_key_public = file("${get_terragrunt_dir()}/../../deploy.key.pub") # live/<env>/deploy.key, la genera make
}
