output "id" {
  value = module.cluster.id
}

# kubeconfig con la credencial vía doctl, igual al que escribe `doctl kubernetes cluster kubeconfig save`,
# pero con el contexto llamado var.kube_context. Se escribe en .kube/<env> con `make kubeconfig`.
output "kubeconfig" {
  sensitive = true
  value = yamlencode({
    apiVersion = "v1"
    kind       = "Config"
    clusters = [{
      name = var.kube_context
      cluster = {
        server                       = module.cluster.endpoint
        "certificate-authority-data" = module.cluster.cluster_ca_certificate
      }
    }]
    users = [{
      name = var.kube_context
      user = {
        exec = {
          apiVersion      = "client.authentication.k8s.io/v1beta1"
          command         = "doctl"
          args            = ["kubernetes", "cluster", "kubeconfig", "exec-credential", "--version=v1beta1", "--context=default", module.cluster.id]
          interactiveMode = "IfAvailable"
        }
      }
    }]
    contexts = [{
      name    = var.kube_context
      context = { cluster = var.kube_context, user = var.kube_context }
    }]
    "current-context" = var.kube_context
  })
}
