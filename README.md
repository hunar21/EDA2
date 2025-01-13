# Protein Domain Analysis with Python and Distributed Computing

This project is designed to efficiently analyze and summarize protein domain data for human and Ecoli datasets. It automates domain prediction, result summarization, and mean score calculation by combining tailored Python scripts with distributed computing tools like Apache Spark.

The implementation emphasizes scalability, performance, and simplicity, ensuring the system can handle large datasets while minimizing overhead. This streamlined workflow offers a valuable solution for researchers and organizations conducting bioinformatics studies on protein domains.

---

## Prerequisites

Before using this project, ensure the following tools are installed on your system:

### Ansible
Install using Homebrew:
```bash
brew install ansible
```

### Terraform
Install using Homebrew:
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

---

## Usage

### Step 1: Setting Up Virtual Machines with Terraform

Terraform is used to create and configure the required virtual machines (VMs). The process involves two configuration files: `main.tf` and `variables.tf`. Follow these steps:

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Apply the configuration to create the infrastructure:
   ```bash
   terraform apply
   ```

This process creates the following VMs:
- **1 Host VM**
- **3 Worker VMs**
- **1 Storage VM**

These VMs form the foundation for the project's workflow.

---

### Step 2: Configuring the Environment with Ansible

After creating the VMs, run the Ansible playbook `full.yaml` to configure the environment. This playbook combines several smaller playbooks, each handling a specific task:

1. **`add_keys.yaml`**: Adds the public SSH key to the authorized keys of the hosts.
2. **`tools.yaml`**: Installs necessary tools and libraries across all VMs.
3. **`install_pyspark.yaml`**: Installs PySpark for distributed task execution.
4. **`second-disk.yaml`**: Formats the secondary storage disk on the storage VM.
5. **`setup_cluster.yaml`**: Sets up the cluster by:
   - Installing required scripts on the host VM.
   - Mounting shared storage on the host and workers using NFS.
6. **`setup_data.yaml`**: Prepares the required datasets on the storage node and organizes them into the appropriate format.
7. **`execute_scripts.yaml`**: Executes the core Python scripts:
   - `pipeline_script.py`
   - `results_parser.py`
   - Mean calculation scripts for both human and Ecoli datasets.

To run `full.yaml`, execute:
```bash
ansible-playbook -i generate_inventory.py full.yaml
```

> **Note**: The `generate_inventory.py` script creates an inventory file for the host, workers, and storage nodes.

---

### Troubleshooting

If the script fails at any point, try running the failed playbooks individually. If the script runs successfully up to the final step of executing the Python scripts, ensure the following:

1. **On the Host VM**:
   - Scripts should be present at `/data/local/pipeline_scripts`.
   - This directory must contain all required scripts.

2. **On the Storage VM**:
   - `db`, `human`, and `ecoli` directories should be present at `/data/local/extracted`.
   - `.pdb` files should exist inside the `human` and `ecoli` directories.

If these conditions are not met, rerun the `setup_cluster.yaml` playbook and verify again.
> **Note**: change path in setup_cluster where the scripts are present in task- "Copy scripts to all nodes" and make sure all scripts are present at the location specified.
---

### Step 3: Executing Scripts

When `execute_scripts.yaml` runs, the following Python scripts are executed:

1. **`pipeline_script.py`**:
   - **Arguments**: Input directory, Output directory
   - Example:
     ```bash
     spark-submit pipeline_script.py /data/local/extracted/ecoli /data/local/extracted/ecoli/output
     ```

2. **`summarise_results.py`**:
   - **Arguments**: Input directory, Output directory, Name_of_the_file__cath_summary.csv
   - Example:
     ```bash
     python3 summarise_results.py /data/local/extracted/ecoli/output /data/local/extracted/ecoli/summary_file ecoli
     ```

3. **`calculate_mean.py`**:
   - **Arguments**: Input directory, Output directory
   - Example:
     ```bash
     python3 calculate_mean.py /data/local/extracted/ecoli/output /data/local/extracted/ecoli/plDDT_mean
     ```

The system is configured to run these commands in the following order:

1. `spark-submit pipeline_script.py /data/local/extracted/ecoli /data/local/extracted/ecoli/output`
2. `python3 summarise_results.py /data/local/extracted/ecoli/output /data/local/extracted/ecoli/summary_file ecoli`
3. `python3 calculate_mean.py /data/local/extracted/ecoli/output /data/local/extracted/ecoli/plDDT_mean`
4. `spark-submit pipeline_script.py /data/local/extracted/human /data/local/extracted/human/output`
5. `python3 summarise_results.py /data/local/extracted/human/output /data/local/extracted/human/summary_file human`
6. `python3 calculate_mean.py /data/local/extracted/human/output /data/local/extracted/human/plDDT_mean`

---

### Output Files

**For Ecoli:**
- Output files: `/data/local/extracted/ecoli/output`
- Summary CSV: `/data/local/extracted/ecoli/summary_file`
- Mean CSV: `/data/local/extracted/ecoli/plDDT_mean`

**For Human:**
- Output files: `/data/local/extracted/human/output`
- Summary CSV: `/data/local/extracted/human/summary_file`
- Mean CSV: `/data/local/extracted/human/plDDT_mean`

> **Note**: If at any point any of the scripts do not work, navigate to `/data/local/pipeline_scripts` and run the script manually.

---

## To Conclude

Commands to run:
1. `terraform init`
2. `terraform apply`
3. `ansible-playbook -i generate_inventory.py full.yaml`
