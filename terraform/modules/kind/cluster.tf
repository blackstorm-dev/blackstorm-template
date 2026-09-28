# Cluster local en Docker, como lo armamos nosotros: 1 nodo, NodePorts del gateway publicados en el host. El kubeconfig usable sale por el output (make kubeconfig), no de ~/.kube/config.
module "cluster" {
  source = "../../resources/kind/cluster"

  name            = var.name
  node_image      = null                                      # la versión de Kubernetes que trae el provider
  kubeconfig_path = "${var.kubeconfig_dir}/.${var.name}.kind" # crudo del provider; no se usa directo
  wait_for_ready  = true

  # Métricas accesibles desde Prometheus, dentro de la red del nodo de Docker.
  kubeadm_config_patches = [
    yamlencode({
      kind = "ClusterConfiguration"
      controllerManager = {
        extraArgs = { "bind-address" = "0.0.0.0" }
      }
      scheduler = {
        extraArgs = { "bind-address" = "0.0.0.0" }
      }
      etcd = {
        local = {
          extraArgs = { "listen-metrics-urls" = "http://0.0.0.0:2381" }
        }
      }
    }),
    yamlencode({
      kind               = "KubeProxyConfiguration"
      metricsBindAddress = "0.0.0.0:10249"
    }),
  ]

  node_labels = {
    "ingress-ready" = "true" # convención de kind para que el gateway se programe en este nodo
  }

  # El gateway (Envoy) escucha en estos NodePorts; kind los publica en el host como http_port/https_port.
  port_mappings = [
    { container_port = 30080, host_port = var.http_port },
    { container_port = 30443, host_port = var.https_port },
  ]
}
