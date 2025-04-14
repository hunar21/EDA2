# Common Variables
variable namespace {
  type    = string
  default = "ucabhga-comp0235-ns"
}

variable keyname {
  type    = string
  default = "ssh1"
}

variable keyfile {
  type    = string
  default = "/home/almalinux/.ssh/id_rsa.pub"
}

variable img_display_name {
  type    = string
  default = "almalinux-9.4-20240805"
}

variable network_name {
  type    = string
  default = "ucabhga-comp0235-ns/ds4eng"
}

variable username {
  type    = string
  default = "machine"
}

variable vm_count {
  type    = number
  default = 4 # 1 host + 3 workers
}
variable host_vm_count {
  type    = number
  default = 1 
}
variable worker_vm_count {
  type    = number
  default = 3 
}

# Host Node Configurations
variable host_cpu {
  type    = number
  default = 2
}

variable host_memory {
  type    = string
  default = "4Gi"
}

variable host_hdd1 {
  type    = string
  default = "10Gi"
}

# Worker Node Configurations
variable worker_cpu {
  type    = number
  default = 4
}

variable worker_memory {
  type    = string
  default = "32Gi"
}

variable worker_hdd1 {
  type    = string
  default = "25Gi"
}

# Storage Node Configurations
variable storage_cpu {
  type    = number
  default = 4
}

variable storage_memory {
  type    = string
  default = "8Gi"
}

variable storage_hdd1 {
  type    = string
  default = "10Gi"
}

variable storage_hdd2 {
  type    = string
  default = "200Gi"
}

variable storage_count {
  type    = number
  default = 1 # Number of storage VMs
}

# New Variables for Airflow Tagging
variable airflow_ingress_hostname {
  type    = string
  default = "airflow-machine"  # change as needed
}

variable airflow_ingress_port {
  type    = string
  default = "8085"
}

variable airflow_api_hostname {
  type    = string
  default = "airflow-api-machine"  # change as needed
}

variable airflow_api_port {
  type    = string
  default = "8086"
}