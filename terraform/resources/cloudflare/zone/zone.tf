# La zona no la crea Terraform: los tokens de API no pueden crear zonas. Se agrega una vez en el panel
# (Add a domain) o nace sola si el dominio se compró en Cloudflare Registrar. Acá se lee por nombre.
data "cloudflare_zone" "this" {
  filter = {
    name = var.name
    account = {
      id = var.account_id
    }
  }
}
