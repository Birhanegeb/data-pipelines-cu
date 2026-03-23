# 03 – Chapter 2: One Web Server

**Source:** *Terraform: Up and Running*, 3rd Ed., Chapter 2 – Getting Started.

## What this script does

- Creates an **EC2 instance** with **user_data** that starts a simple HTTP server on port 8080 serving "Hello, World".
- Attaches a **security group** that allows inbound TCP 8080 from anywhere (`0.0.0.0/0`).

After apply, you can open `http://<public_ip>:8080` in a browser.

## Concepts

| Concept         | Where in the script |
|----------------|---------------------|
| Security group | `aws_security_group.instance` – firewall for the instance |
| Reference      | `vpc_security_group_ids = [aws_security_group.instance.id]` – link instance to SG |
| user_data      | Script run at first boot – writes index.html and starts Python http.server |
| user_data_replace_on_change | Re-run user_data when it changes (recreate instance) |

## How to run

```bash
terraform init
terraform apply
# Then: curl http://$(terraform output -raw public_ip):8080
terraform destroy
```

## Prerequisites

- Terraform >= 1.0, AWS credentials.
