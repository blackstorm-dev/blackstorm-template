variable "name" {
  type = string
}

variable "node_image" {
  description = "Imagen del nodo (kindest/node:vX.Y.Z). null = la que trae el provider"
  type        = string
}

variable "kubeconfig_path" {
  description = "Archivo donde se escribe (merge) el contexto kind-<name>"
  type        = string
}

variable "node_labels" {
  type = map(string)
}

variable "port_mappings" {
  description = "Puertos del nodo expuestos en el host"
  type = list(object({
    container_port = number
    host_port      = number
  }))
}

variable "wait_for_ready" {
  type = bool
}

variable "kubeadm_config_patches" {
  description = "Patches de kubeadm al crear el cluster; modificarlos requiere recrearlo"
  type        = list(string)
  default     = []
}
