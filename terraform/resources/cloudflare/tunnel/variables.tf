variable "account_id" {
  type = string
}

variable "name" {
  type = string
}

variable "ingress" {
  description = "Reglas del túnel en orden: hostname → service. La última, sin hostname, es el catch-all"
  type = list(object({
    hostname = optional(string)
    service  = string
  }))
}
