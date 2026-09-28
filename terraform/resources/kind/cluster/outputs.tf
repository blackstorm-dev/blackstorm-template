output "name" {
  value = kind_cluster.this.name
}

output "endpoint" {
  value = kind_cluster.this.endpoint
}

output "kubeconfig" {
  sensitive = true
  value     = kind_cluster.this.kubeconfig
}
