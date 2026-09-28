output "id" {
  value = cloudflare_zero_trust_tunnel_cloudflared.this.id
}

output "cname" {
  description = "Destino al que apuntan los registros DNS que entran por este túnel"
  value       = "${cloudflare_zero_trust_tunnel_cloudflared.this.id}.cfargotunnel.com"
}

output "token" {
  sensitive = true
  value     = data.cloudflare_zero_trust_tunnel_cloudflared_token.this.token
}
