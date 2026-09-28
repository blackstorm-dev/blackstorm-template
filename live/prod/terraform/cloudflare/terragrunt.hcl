include "root" {
  path = find_in_parent_folders("root.hcl")
}

locals {
  config = yamldecode(file("${get_terragrunt_dir()}/../../config/values.yaml"))
}

terraform {
  source = "../../../../terraform//modules/cloudflare"
}

# CLOUDFLARE_API_TOKEN entra por el entorno: live/prod/secrets/cloudflare.env
inputs = {
  account_id  = local.config.cloudflare.accountId # está en la URL del panel; no es secreto
  domain      = local.config.domain
  environment = local.config.environment

  # A dónde entrega el túnel el tráfico: la puerta pública, por su Service (nombre fijo en el EnvoyProxy de prod)
  origin = local.config.cloudflare.origin

  # Los paneles autentican con Dex/GitHub. El túnel no agrega otro login.
  protected_hosts = local.config.cloudflare.protectedHosts
  admin_emails    = local.config.cloudflare.adminEmails
}
