# El túnel: cloudflared, dentro del cluster, abre una conexión saliente hacia Cloudflare y por ahí entra
# todo el tráfico público. No hay Load Balancer ni IP pública. Todo *.dominio va a la puerta envoy-external.
module "tunnel" {
  source = "../../resources/cloudflare/tunnel"

  account_id = var.account_id
  name       = "blackstorm-${var.environment}"
  ingress = [
    { hostname = "*.${var.domain}", service = var.origin },
    { service = "http_status:404" },
  ]
}

# Nombre estable del túnel dentro del dominio. external-dns apunta acá los registros de cada HTTPRoute
# (anotación external-dns.kubernetes.io/target en la puerta), así el ID del túnel no aparece en git.
module "tunnel_record" {
  source = "../../resources/cloudflare/dns-record"

  zone_id = module.zone.id
  name    = "tunnel.${var.domain}"
  type    = "CNAME"
  content = module.tunnel.cname
  proxied = true
}
