resource "cloudflare_dns_record" "this" {
  zone_id = var.zone_id
  name    = var.name
  type    = var.type
  content = var.content
  proxied = var.proxied
  ttl     = 1 # automático (obligatorio cuando proxied)
}
