# 01 – Chapter 1: Hello Terraform

**Source:** *Terraform: Up and Running*, 3rd Ed., Chapter 1 – Why Terraform.

## What this script does

- Declares the **AWS provider** and one **resource**: a single EC2 instance.
- Uses a **data source** to resolve the latest Amazon Linux 2 AMI (no hardcoded AMI id).
- **Outputs** the instance ID and public IP after `terraform apply`.

This is the minimal “Hello, World” style example: infrastructure as code in a few lines.

## Concepts

| Concept    | Where in the script                          |
|-----------|-----------------------------------------------|
| Provider  | `provider "aws"` – talks to AWS API           |
| Resource  | `resource "aws_instance" "example"` – one EC2 |
| Data source | `data "aws_ami"` – read-only lookup        |
| Variable  | `variable "aws_region"` – configurable input  |
| Output    | `output "instance_id"` – values after apply  |

## How to run

```bash
terraform init
terraform plan
terraform apply
```

After apply, note the `public_ip` output. Clean up with:

```bash
terraform destroy
```

## Prerequisites

- Terraform >= 1.0
- AWS credentials (`export AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, or `aws configure`)
