# 04 – Chapter 2: Web Server with Variables

**Source:** *Terraform: Up and Running*, 3rd Ed., Chapter 2 – Getting Started.

## What this script does

- Same pattern as **03_ch2_one_webserver**: one EC2 + security group, HTTP server on a configurable port.
- **Variables** are used for:
  - `server_port` (number) – port for the HTTP server (default 8080).
  - `security_group_name` (string).
  - `aws_region` (string).
- **Interpolation** – `${var.server_port}` in user_data and in the `url` output.

You can override at apply time: `terraform apply -var="server_port=9000"`.

## Concepts

| Concept   | Where in the script |
|----------|----------------------|
| Variable | `variable "server_port" { type = number, default = 8080 }` |
| Reference | `${var.server_port}` in user_data and output |
| Types    | `string`, `number`, `list(string)`, `map(string)` (see variables.tf) |

## How to run

```bash
terraform init
terraform apply
# Optional: terraform apply -var="server_port=9000"
terraform destroy
```

## Prerequisites

- Terraform >= 1.0, AWS credentials.
