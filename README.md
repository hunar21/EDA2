# Srock market prediction with Distributed Computing

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
7. **`shared_venv.yaml`**: Prepares a shared Python environment to be used by workers and hosts.
8. **`setup_airflow.yaml`**: Prepares airflow setup on host.

To run `full.yaml`, execute:
```bash
ansible-playbook -i generate_inventory.py full.yaml
```

> **Note**: The `generate_inventory.py` script creates an inventory file for the host, workers, and storage nodes.

---

### Troubleshooting

If the script fails at any point, try running the failed playbooks individually. If the script runs successfully up to the final step of executing the Python scripts, ensure the following:

1. **On the Host VM**:
   - Script (test.py) should be present at `/data/local/pipeline_scripts`.
   - This directory must contain the pre-trained model as well.

2. **On the Storage VM**:
   - csv files should be present in /data/local/venv/extracted/stock-market-dataset/stocks.

If these conditions are not met, rerun the `setup_cluster.yaml` and `setup_data.yaml`  playbook and verify again.


### Step 3: Working with Airflow
1. Open your browser and navigate to the Airflow web UI at http://<host_ip>:8080.

2. Log in with the default credentials:
Username: admin
Password: admin

3. In the DAGs list, locate stock_prediction_dag.py and click the Trigger button to start the pipeline.

Wait for the DAG to finish executing. You can monitor task status in the UI.

4. Custom CSV Directory (Optional):

   1. In the Airflow UI, go to Admin → Variables.

   2. Add or edit a variable named csv_dir and set its value to the path of your custom CSV directory.

Note: Ensure the CSV files exist in the specified location.

5. Re-trigger stock_prediction_dag.py to use the new directory.





## To Conclude

Commands to run:
1. `terraform init`
2. `terraform apply`
3. `ansible-playbook -i generate_inventory.py full.yaml`
