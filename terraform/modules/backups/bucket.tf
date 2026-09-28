# Bucket de backups: repo kopia (Kopiur) y base backups + WAL de Postgres (CNPG).
# Privado, sin versionado (kopia y barman ya versionan por su cuenta).
module "bucket" {
  source = "../../resources/digitalocean/spaces-bucket"

  name   = var.name
  region = var.region

  acl        = "private"
  versioning = false
}
