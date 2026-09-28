include "root" {
  path = find_in_parent_folders("root.hcl") # el de live/local/terraform/
}

locals {
  config = yamldecode(file("${get_terragrunt_dir()}/../../config/values.yaml"))
}

terraform {
  source = "../../../../terraform//modules/kind"
}

inputs = {
  name           = local.config.cluster.name
  http_port      = local.config.cluster.httpPort  # localhost:8080 → gateway envoy-external (NodePort 30080)
  https_port     = local.config.cluster.httpsPort # localhost:8443 → gateway envoy-external (NodePort 30443)
  kube_context   = local.config.environment       # kubectl --context local (y el actual dentro del repo)
  kubeconfig_dir = "${get_repo_root()}/.kube"
}
