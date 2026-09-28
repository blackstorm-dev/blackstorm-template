output "id" {
  value = digitalocean_kubernetes_cluster.this.id
}

output "name" {
  value = digitalocean_kubernetes_cluster.this.name
}

output "endpoint" {
  value = digitalocean_kubernetes_cluster.this.endpoint
}

output "cluster_ca_certificate" {
  description = "CA del API server, en base64"
  value       = digitalocean_kubernetes_cluster.this.kube_config[0].cluster_ca_certificate
}
