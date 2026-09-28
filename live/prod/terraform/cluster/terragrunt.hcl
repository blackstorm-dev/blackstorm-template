include "root" {
  path = find_in_parent_folders("root.hcl")
}

locals {
  config = yamldecode(file("${get_terragrunt_dir()}/../../config/values.yaml"))
}

terraform {
  source = "../../../../terraform//modules/doks"
}

inputs = {
  name         = local.config.cluster.name
  region       = local.config.cluster.region
  node_size    = local.config.cluster.nodeSize
  node_count   = local.config.cluster.nodeCount
  kube_context = local.config.environment # kubectl --context prod
}
