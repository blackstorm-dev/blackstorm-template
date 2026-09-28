# Configuración común a todas las unidades de live/<env>/terraform/. Cada una la hereda con `include "root"`.
# Los providers los declara cada módulo en su providers.tf; las credenciales vienen del entorno (live/<env>/secrets/*.env).

# State remoto en Spaces (API compatible con S3). Un state por unidad: <env>/terraform/<unidad>/terraform.tfstate
# El bucket se crea una vez con: terragrunt backend bootstrap --working-dir live/<env>/terraform/<unidad>
locals {
  config = yamldecode(file(find_in_parent_folders("config/values.yaml")))
}

remote_state {
  backend = "s3"

  generate = {
    path      = "backend.tf"
    if_exists = "overwrite"
  }

  config = {
    bucket = local.config.state.bucket
    key    = "${path_relative_to_include()}/terraform.tfstate"
    # Valor requerido por el backend S3; la ubicación real de Spaces la determina state.endpoint en config/values.yaml.
    region    = "us-east-1"
    endpoints = { s3 = local.config.state.endpoint }

    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true

    # Terragrunt administra el bucket como si fuera AWS. En Spaces solo aplica el versionado.
    skip_bucket_ssencryption           = true
    skip_bucket_root_access            = true
    skip_bucket_enforced_tls           = true
    skip_bucket_public_access_blocking = true
    disable_bucket_update              = true
  }
}
