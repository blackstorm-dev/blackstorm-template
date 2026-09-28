include "root" {
  path = find_in_parent_folders("root.hcl")
}

# "terraform//modules/backups": Terragrunt copia todo terraform/ a su cache y trabaja en modules/backups,
# así los `source = "../../resources/..."` del módulo siguen resolviendo.
locals {
  config = yamldecode(file("${get_terragrunt_dir()}/../../config/values.yaml"))
}

terraform {
  source = "../../../../terraform//modules/backups"
}

inputs = {
  name   = local.config.backups.bucket
  region = local.config.backups.region
}
