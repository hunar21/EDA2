#!/usr/bin/env python3

import json
import subprocess
import sys

try:
    # Fetch Terraform outputs directly
    output = subprocess.check_output(["terraform", "output", "-json"], text=True)
    terraform_outputs = json.loads(output)

    # Extract IPs for each group
    host_ips = terraform_outputs.get("host_ips", {}).get("value", [])
    worker_ips = terraform_outputs.get("worker_ips", {}).get("value", [])
    storage_ips = terraform_outputs.get("storage_ips", {}).get("value", [])

    # Create inventory structure
    inventory = {
        "all": {
            "children": ["hosts", "workers", "storage"]
        },
        "hosts": {
            "hosts": host_ips
        },
        "workers": {
            "hosts": worker_ips
        },
        "storage": {
            "hosts": storage_ips
        }
    }

    # Output inventory as JSON
    print(json.dumps(inventory, indent=2))
except subprocess.CalledProcessError as e:
    print("Error running Terraform command:", e, file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print("Error decoding JSON from Terraform output:", e, file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print("An unexpected error occurred:", e, file=sys.stderr)
    sys.exit(1)
