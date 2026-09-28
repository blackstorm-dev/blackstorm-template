variable "account_id" {
  type = string
}

variable "name" {
  type = string
}

variable "domain" {
  description = "Hostname que protege (argocd.blackstorm.io)"
  type        = string
}

variable "allowed_emails" {
  description = "Quiénes pueden entrar (login por email con código, sin proveedor de identidad)"
  type        = list(string)
}

variable "session_duration" {
  type = string
}
