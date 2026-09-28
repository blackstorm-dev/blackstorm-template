# Cloudflare Access agrega autenticación delante de los paneles seleccionados, antes
# de dejar pasar la request al túnel. Login por email con código, sin proveedor de identidad.
module "access" {
  source   = "../../resources/cloudflare/access-application"
  for_each = toset(var.protected_hosts)

  account_id       = var.account_id
  name             = "${each.key} (${var.environment})"
  domain           = "${each.key}.${var.domain}"
  allowed_emails   = var.admin_emails
  session_duration = "24h"
}
