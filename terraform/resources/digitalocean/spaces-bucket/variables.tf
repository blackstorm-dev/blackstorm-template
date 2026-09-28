variable "name" {
  description = "Nombre del bucket. Es global en Spaces: si está tomado, hay que elegir otro."
  type        = string
}

variable "region" {
  type = string
}

variable "acl" {
  description = "private o public-read"
  type        = string
}

variable "versioning" {
  description = "Guardar versiones anteriores de cada objeto"
  type        = bool
}
