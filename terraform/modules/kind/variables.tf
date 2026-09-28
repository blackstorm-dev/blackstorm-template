variable "name" {
  type = string
}

variable "http_port" {
  description = "Puerto del host que se mapea al 80 del nodo"
  type        = number
}

variable "https_port" {
  description = "Puerto del host que se mapea al 443 del nodo"
  type        = number
}

variable "kube_context" {
  description = "Nombre del contexto en el kubeconfig generado (kubectl --context <este>)"
  type        = string
}

variable "kubeconfig_dir" {
  description = "Carpeta donde el provider deja su kubeconfig crudo (.kube/ del repo, ignorada por git)"
  type        = string
}
