# 02 – Chapter 2: One Server

**Source:** *Terraform: Up and Running*, 3rd Ed., Chapter 2 – Getting Started.

## What this script does

- Creates a **single EC2 instance** (t2.micro, Amazon Linux 2).
- No security group, no user_data – the bare minimum to launch a server.

This is the first “real” resource from Chapter 2: one server in AWS.

## Concepts

- **Resource block** – `resource "aws_instance" "example"` defines one EC2 instance.
- **Attributes** – `ami`, `instance_type`, `tags` are passed to the AWS API.
- **Outputs** – Expose `instance_id` and `public_ip` after apply.

## How to run

```bash
terraform init
terraform apply
terraform destroy
```

## Prerequisites

- Terraform >= 1.0, AWS credentials configured.
