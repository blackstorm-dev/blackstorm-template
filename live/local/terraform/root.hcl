# Entorno local: pisa al live/root.hcl (Terragrunt usa el más cercano a la unidad).
# State en disco. Los providers los declara cada módulo en su providers.tf.

remote_state {
  backend = "local"

  generate = {
    path      = "backend.tf"
    if_exists = "overwrite"
  }

  config = {
    path = "${get_terragrunt_dir()}/terraform.tfstate" # al lado del terragrunt.hcl, no en el cache
  }
}
