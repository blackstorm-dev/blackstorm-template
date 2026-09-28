variable "name" {
  description = "Nombre del cluster"
  type        = string
}

variable "region" {
  description = "Región de DigitalOcean"
  type        = string
}

variable "node_size" {
  description = "Tamaño de cada nodo"
  type        = string
}

variable "node_count" {
  description = "Cantidad de nodos"
  type        = number
}

variable "kube_context" {
  description = "Nombre del contexto en el kubeconfig generado (kubectl --context <este>)"
  type        = string
}
