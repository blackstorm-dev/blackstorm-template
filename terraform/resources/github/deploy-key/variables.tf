variable "repository" {
  description = "Nombre del repo, sin owner (el owner lo define el provider)"
  type        = string
}

variable "title" {
  type = string
}

variable "public_key" {
  description = "Clave pública SSH (ssh-ed25519 AAAA...)"
  type        = string
}

variable "read_only" {
  type = bool
}
