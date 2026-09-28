# Kubernetes gestionado de DigitalOcean (DOKS), como lo armamos nosotros:
# control plane sin HA (gratis), parches automáticos los domingos a las 04:00 UTC con surge upgrade.
module "cluster" {
  source = "../../resources/digitalocean/kubernetes-cluster"

  name       = var.name
  region     = var.region
  node_size  = var.node_size
  node_count = var.node_count

  ha                     = false
  auto_upgrade           = true
  surge_upgrade          = true
  maintenance_day        = "sunday"
  maintenance_start_time = "04:00"
}
