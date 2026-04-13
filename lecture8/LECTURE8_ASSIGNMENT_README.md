# Lecture 8: Terraform Assignment – Baseline Infrastructure for Data Pipelines

Deploy a **baseline infrastructure** (storage buckets + database) using Terraform. You must use **modules** and **for_each** (or `count`) to demonstrate Lecture 8 concepts.

You can complete the assignment using **Docker (local)** or **AWS (cloud)** – same submission format as Lecture 7.

## Objectives

1. **Deploy storage** – At least two storage locations (e.g. raw, staged buckets or equivalent).
2. **Deploy a database** – PostgreSQL (or equivalent) for pipeline metadata.
3. **Use a module** – Create a reusable module (e.g. for S3 buckets or Docker services) and call it from your root config.
4. **Use for_each or count** – Create multiple resources (buckets, containers) using a loop.
5. **Variables and outputs** – Use variables for configuration; output connection info (URLs, endpoints, bucket names).

## Two Options: Docker or AWS

| Option | Folder | Prerequisites |
|--------|--------|---------------|
| **Docker** | `assignment/docker/` | Terraform, Docker (local) |
| **AWS** | `assignment/aws/` | Terraform, AWS account & credentials |

### Docker (local)

- Uses Terraform Docker provider.
- Deploy **MinIO** (S3-compatible object storage) and **PostgreSQL** containers.
- Use a **module** for at least one component (e.g. `modules/storage` or `modules/database`).
- Use **for_each** or **count** for multiple services or config.
- **Outputs**: MinIO console URL (http://localhost:9001), PostgreSQL connection string (host:port).

### AWS (cloud)

- Uses Terraform AWS provider.
- Deploy **S3 buckets** (e.g. raw, staged, curated) with versioning and encryption.
- Deploy **RDS PostgreSQL** (or DynamoDB for simpler option).
- Use a **module** for the S3 bucket pattern (reusable across buckets).
- Use **for_each** for the bucket suffixes (raw, staged, curated).
- **Outputs**: Bucket IDs/ARNs, RDS endpoint (or DynamoDB table name).

## Quick Start

### Docker

```bash
cd lecture8/assignment/docker
terraform init
terraform apply
# MinIO console: http://localhost:9001 (default: minioadmin/minioadmin)
# PostgreSQL: localhost:5432
terraform destroy   # when done
```

### AWS

```bash
cd lecture8/assignment/aws
terraform init
terraform plan
terraform apply
# If using RDS, set: export TF_VAR_db_password="your-password"
terraform destroy   # when done
```

## How to Submit

Same as Lecture 7:

1. **Screenshot** of the deployed infrastructure (e.g. MinIO UI, AWS S3 console, or `terraform output`).
2. **Screenshot** of `terraform output` showing bucket names, endpoints, or URLs.
3. Your **Terraform files** (main.tf, variables.tf, outputs.tf, and your `modules/` folder).
4. **Pull Request** with the above.

### PR structure

```
lecture8/
├── assignment/
│   ├── docker/          # if you used Docker
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── modules/
│   │       └── ...
│   └── aws/             # if you used AWS
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── modules/
│           └── ...
├── LECTURE8_ASSIGNMENT_README.md
├── screenshot_infra.png
├── screenshot_output.png
└── ...
```

### PR title example

```
Lecture 8: Baseline Infrastructure (Docker) - [Your Name]
```
or
```
Lecture 8: Baseline Infrastructure (AWS) - [Your Name]
```

## Requirements Checklist

- [ ] At least 2 storage locations (buckets or equivalent)
- [ ] 1 database (PostgreSQL or equivalent)
- [ ] 1 reusable module (used in root config)
- [ ] for_each or count for multiple resources
- [ ] Variables for config (project name, env, etc.)
- [ ] Outputs for connection info

## Reference

- Lecture 8 slides (Ch 4: Modules, Ch 5: Loops)
- Lecture 8 hands-on-lab (Example AWS baseline)
- [MinIO](https://min.io/) – S3-compatible object storage
- [MinIO Docker](https://hub.docker.com/r/minio/minio)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
