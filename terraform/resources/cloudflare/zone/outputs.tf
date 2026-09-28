output "id" {
  value = data.cloudflare_zone.this.id
}

output "name" {
  value = data.cloudflare_zone.this.name
}

output "name_servers" {
  description = "Los nameservers que hay que poner en el registrador (si el dominio no se compró en Cloudflare)"
  value       = data.cloudflare_zone.this.name_servers
}
