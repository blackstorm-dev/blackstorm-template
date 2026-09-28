variable "account_id" {
  description = "ID de la cuenta de Cloudflare: está en la URL del panel (dash.cloudflare.com/<account_id>/...). No es secreto"
  type        = string
}

variable "domain" {
  description = "Dominio de la plataforma en este entorno (blackstorm.io)"
  type        = string
}

variable "environment" {
  description = "Nombre del entorno; identifica el túnel en Cloudflare"
  type        = string
}

variable "origin" {
  description = "A dónde manda el túnel el tráfico dentro del cluster: el Service de la puerta pública"
  type        = string
}

variable "admin_emails" {
  description = "Quiénes pueden abrir los paneles (Cloudflare Access)"
  type        = list(string)
}

variable "protected_hosts" {
  description = "Subdominios que van detrás de Cloudflare Access (argocd, grafana, ...)"
  type        = list(string)
}
