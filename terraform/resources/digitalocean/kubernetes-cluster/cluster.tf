data "digitalocean_kubernetes_versions" "current" {}

resource "digitalocean_kubernetes_cluster" "this" {
  name    = var.name
  region  = var.region
  version = data.digitalocean_kubernetes_versions.current.latest_version
  ha      = var.ha

  auto_upgrade  = var.auto_upgrade
  surge_upgrade = var.surge_upgrade

  maintenance_policy {
    day        = var.maintenance_day
    start_time = var.maintenance_start_time
  }

  node_pool {
    name       = "default"
    size       = var.node_size
    node_count = var.node_count
  }

  lifecycle {
    # auto_upgrade cambia la versión por fuera de Terraform.
    ignore_changes = [version]
  }
}
