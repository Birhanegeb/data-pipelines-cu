# 07 – Chapter 3: Remote State (S3 + DynamoDB)

**Source:** *Terraform: Up and Running*, 3rd Ed., Chapter 3 – How to Manage Terraform State.

## What this script does

- Creates an **S3 bucket** for storing Terraform state files.
- Enables **versioning** and **server-side encryption** on the bucket.
- Blocks **public access** on the bucket.
- Creates a **DynamoDB table** used for **state locking** (so two runs don’t apply at once).

You run this **once** per account/region. Then other Terraform configs can use a **backend "s3"** block pointing at this bucket and table.

## Concepts

| Concept       | Where in the script |
|---------------|----------------------|
| Remote state  | State file is stored in S3 instead of local `terraform.tfstate` |
| Backend       | Other configs use `backend "s3" { bucket = "...", key = "...", dynamodb_table = "..." }` |
| Locking       | DynamoDB table prevents concurrent `terraform apply` |
| Versioning    | S3 versioning allows recovery of previous state |
| Encryption    | SSE-S3 (AES256) for state at rest |

## How to run

```bash
# Pick unique names (bucket must be globally unique)
terraform init
terraform apply -var="bucket_name=mycompany-terraform-state-UNIQUE" -var="table_name=terraform-locks"
```

After apply, the output shows a sample **backend_config** block. Add that (with a `key` path per project) to other Terraform configs, then run `terraform init -migrate-state` to move local state to S3.

## Prerequisites

- Terraform >= 1.0, AWS credentials.
- Choose a globally unique `bucket_name` (e.g. include account id or random suffix).
