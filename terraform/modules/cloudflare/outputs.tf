output "name_servers" {
  description = "Si el dominio se compró fuera de Cloudflare: pegar estos en el registrador, una vez"
  value       = module.zone.name_servers
}

output "tunnel_hostname" {
  description = "Destino de los registros DNS de las apps (anotación target de la puerta)"
  value       = module.tunnel_record.name
}

# Lo lee make bootstrap para crear el Secret de cloudflared en el cluster.
output "tunnel_token" {
  sensitive = true
  value     = module.tunnel.token
}
