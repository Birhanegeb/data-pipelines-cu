# Lecture 8 Hands-on Lab: Baseline Infrastructure for Data Pipelines

Deploy a baseline infrastructure using Terraform: **S3 buckets** (raw, staged, curated) and optionally **RDS PostgreSQL**.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.0
- **AWS account** and credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or `aws configure`)

## What Gets Created

| Resource | Description |
|----------|-------------|
| S3 buckets | `{project}-{env}-raw`, `staged`, `curated` with versioning and encryption |
| RDS PostgreSQL | Optional; set `create_database = true` and provide `db_password` |

## Quick Start (Buckets Only)

```bash
terraform init
terraform plan
terraform apply
```

This creates three S3 buckets. No database is created by default.

## With Database

1. Set `create_database = true` (e.g. in `terraform.tfvars` or via `-var`).
2. Provide the database password:
   ```bash
   export TF_VAR_db_password="your-secure-password"
   terraform apply
   ```
   Or: `terraform apply -var="db_password=your-secure-password"`

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aws_region` | `us-east-1` | AWS region |
| `project` | `data-pipeline` | Project name in resource naming |
| `env` | `dev` | Environment (dev, staging, prod) |
| `bucket_suffixes` | `["raw", "staged", "curated"]` | S3 bucket stage names |
| `create_database` | `false` | Create RDS PostgreSQL |
| `db_password` | (required if DB) | PostgreSQL master password |

## Outputs

- `bucket_ids` — S3 bucket IDs by stage
- `bucket_arns` — S3 bucket ARNs by stage
- `db_endpoint` — RDS endpoint (if `create_database = true`)
- `db_address` — RDS host address (if `create_database = true`)

## Cleanup

```bash
terraform destroy
```

If you created a database, ensure it is fully deleted (may take a few minutes).
