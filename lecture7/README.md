# Lecture 7: Terraform – Chapters 1, 2, 3

Based on **Terraform: Up and Running, 3rd Edition** by Yevgeniy Brikman (O’Reilly).

This folder contains Terraform script examples from **Chapter 1 (Why Terraform)**, **Chapter 2 (Getting Started with Terraform)**, and **Chapter 3 (How to Manage Terraform State)**.

## Chapter 1: Why Terraform

- **IaC** – Define infrastructure in code; deploy with `terraform apply`.
- **Providers** – AWS, Azure, GCP, etc. Terraform talks to APIs and creates resources.
- **01_ch1_hello_terraform** – Minimal example: one EC2 instance.

## Chapter 2: Getting Started with Terraform

- **Syntax** – `terraform` block, `provider`, `resource`, `variable`, `output`.
- **CLI** – `terraform init`, `plan`, `apply`, `destroy`.
- **02_ch2_one_server** – Single EC2 instance.
- **03_ch2_one_webserver** – EC2 + security group, serves "Hello, World" on port 8080.
- **04_ch2_webserver_variables** – Same webserver with variables (port, types).
- **05_ch2_webserver_cluster** – Auto Scaling Group + Application Load Balancer.

## Chapter 3: How to Manage Terraform State

- **State** – Terraform stores resource IDs and attributes in `terraform.tfstate`.
- **Remote state** – Store state in S3 (and optional DynamoDB lock).
- **Workspaces** – Multiple state environments (e.g. dev/stage/prod) in one config.
- **06_ch3_workspaces** – Instance type depends on `terraform.workspace`.
- **07_ch3_remote_state** – S3 bucket + DynamoDB table for backend.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.0
- **AWS account** and credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or `aws configure`)

## Running an Example

```bash
cd lecture7/01_ch1_hello_terraform   # or any example folder
terraform init
terraform plan
terraform apply
# when done:
terraform destroy
```

Each example has its own **README.md** explaining the script and how to run it.

## Assignment: Web Server + n8n

Deploy a **web server** and **n8n** with dependencies running first (same style as Lecture 6). Supports **Docker (local)** or **AWS (cloud)**.

- **assignment/docker/** – Docker provider: webserver container, then n8n container (`depends_on`).
- **assignment/aws/** – One EC2; `user_data` installs Docker, runs webserver, then n8n.

See **LECTURE7_ASSIGNMENT_README.md** for objectives, how to run, and submission.

## Reference

- Book: *Terraform: Up and Running*, 3rd Ed. – Chapters 1, 2, 3  
- Companion code: `terraform-up-and-running-code/code/terraform/`
