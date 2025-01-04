# Fetch the content of the public key file
data "local_file" "new_public_key" {
  filename = var.keyfile
}

# Create an SSH key in Harvester
resource "harvester_ssh_key" "new_key" {
  name       = var.keyname
  namespace  = var.namespace
  public_key = data.local_file.new_public_key.content
}

# Fetch the image for the virtual machine
data "harvester_image" "img" {
  display_name = var.img_display_name
  namespace    = "harvester-public"
}

# Generate a unique ID for the cloud-init secret and VM names
resource "random_id" "secret" {
  byte_length = 5
}

# Create a cloud-init secret for VM configuration (host)
resource "harvester_cloudinit_secret" "cloud-config-host" {
  count     = var.host_vm_count
  name      = "cloud-config-host-${random_id.secret.hex}-${count.index}"
  namespace = var.namespace
  user_data = templatefile("cloud-init.tmpl.yml", {
    public_key_openssh = harvester_ssh_key.new_key.public_key # add public key here
  })
}

# Create a cloud-init secret for VM configuration (worker)
resource "harvester_cloudinit_secret" "cloud-config-worker" {
  count     = var.worker_vm_count
  name      = "cloud-config-worker-${random_id.secret.hex}-${count.index}"
  namespace = var.namespace
  user_data = templatefile("cloud-init.tmpl.yml", {
    public_key_openssh = harvester_ssh_key.new_key.public_key
  })
}

# Create host virtual machines
resource "harvester_virtualmachine" "host" {
  count = var.host_vm_count

  name                 = "host-${count.index + 1}-${random_id.secret.hex}"
  namespace            = var.namespace
  restart_after_update = true

  description = "Host Node"

  cpu    = var.host_cpu
  memory = var.host_memory

  efi          = true
  secure_boot  = true
  run_strategy = "RerunOnFailure"
  hostname     = "host-${count.index + 1}-${random_id.secret.hex}"

  # Network interface
  network_interface {
    name           = "nic-host-${count.index + 1}"
    wait_for_lease = true
    type           = "bridge"
    network_name   = var.network_name
  }

  # Disk configuration
  disk {
    name       = "disk1"
    type       = "disk"
    size       = var.host_hdd1
    bus        = "virtio"
    boot_order = 1

    image       = data.harvester_image.img.id
    auto_delete = true
  }

  # Cloud-init configuration
  cloudinit {
    user_data_secret_name = harvester_cloudinit_secret.cloud-config-host[count.index].name
  }

  # Dependencies
  depends_on = [harvester_cloudinit_secret.cloud-config-host]
}

# Create worker virtual machines
resource "harvester_virtualmachine" "worker" {
  count = var.worker_vm_count

  name                 = "worker-${format("%02d", count.index + 1)}-${random_id.secret.hex}"
  namespace            = var.namespace
  restart_after_update = true

  description = "Worker Node"

  cpu    = var.worker_cpu
  memory = var.worker_memory

  efi          = true
  secure_boot  = true
  run_strategy = "RerunOnFailure"
  hostname     = "worker-${format("%02d", count.index + 1)}-${random_id.secret.hex}"

  # Network interface
  network_interface {
    name           = "nic-worker-${count.index + 1}"
    wait_for_lease = true
    type           = "bridge"
    network_name   = var.network_name
  }

  # Disk configuration
  disk {
    name       = "disk1"
    type       = "disk"
    size       = var.worker_hdd1
    bus        = "virtio"
    boot_order = 1

    image       = data.harvester_image.img.id
    auto_delete = true
  }

  # Cloud-init configuration
  cloudinit {
    user_data_secret_name = harvester_cloudinit_secret.cloud-config-worker[count.index].name
  }

  # Dependencies
  depends_on = [harvester_cloudinit_secret.cloud-config-worker]
}

# Create storage machines
resource "harvester_virtualmachine" "storage_vm" {
  count = var.storage_count

  name                 = "storage-${format("%02d", count.index + 1)}-${random_id.secret.hex}"
  namespace            = var.namespace
  restart_after_update = true

  description = "Storage Node"

  cpu    = var.storage_cpu
  memory = var.storage_memory

  efi          = true
  secure_boot  = true
  run_strategy = "RerunOnFailure"
  hostname     = "storage-${format("%02d", count.index + 1)}-${random_id.secret.hex}"

  # Network interface
  network_interface {
    name           = "nic-storage-${count.index + 1}"
    wait_for_lease = true
    type           = "bridge"
    network_name   = var.network_name
  }

  # Disk 1 configuration
  disk {
    name       = "disk1"
    type       = "disk"
    size       = var.storage_hdd1
    bus        = "virtio"
    boot_order = 1

    image       = data.harvester_image.img.id
    auto_delete = true
  }

  # Disk 2 configuration
  disk {
    name       = "disk2"
    type       = "disk"
    size       = var.storage_hdd2
    bus        = "virtio"
    auto_delete = true
  }

  # Cloud-init configuration
  cloudinit {
    user_data_secret_name = harvester_cloudinit_secret.cloud-config-worker[count.index].name
  }

  # Dependencies
  depends_on = [harvester_cloudinit_secret.cloud-config-worker]
}
