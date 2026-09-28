output "endpoint" {
  value = module.cluster.endpoint
}

# El kubeconfig del provider, con el contexto renombrado a var.kube_context.
# Se escribe en .kube/<env> con `make kubeconfig`.
locals {
  raw = yamldecode(module.cluster.kubeconfig)
  kubeconfig = merge(local.raw, {
    contexts          = [for c in local.raw.contexts : merge(c, { name = var.kube_context })]
    "current-context" = var.kube_context
  })
}

output "kubeconfig" {
  sensitive = true
  value     = yamlencode(local.kubeconfig)
}
