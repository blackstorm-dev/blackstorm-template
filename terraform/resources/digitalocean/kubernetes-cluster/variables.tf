variable "name" {
  type = string
}

variable "region" {
  type = string
}

variable "node_size" {
  type = string
}

variable "node_count" {
  type = number
}

variable "ha" {
  description = "Control plane con alta disponibilidad"
  type        = bool
}

variable "auto_upgrade" {
  description = "DO aplica parches de Kubernetes en la ventana de mantenimiento"
  type        = bool
}

variable "surge_upgrade" {
  description = "Crea nodos nuevos antes de bajar los viejos durante un upgrade"
  type        = bool
}

variable "maintenance_day" {
  description = "Día de la ventana de mantenimiento (monday..sunday, any)"
  type        = string
}

variable "maintenance_start_time" {
  description = "Hora UTC de inicio de la ventana (HH:MM)"
  type        = string
}
