# El dominio de la plataforma. La zona ya existe en Cloudflare (agregada en el panel o comprada en Registrar): se lee.
module "zone" {
  source = "../../resources/cloudflare/zone"

  account_id = var.account_id
  name       = var.domain
}
