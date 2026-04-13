# Lecture 7: Terraform Assignment – Web Server + n8n

Deploy a **web server** and **n8n** (workflow automation) using Terraform. All **dependencies must run before** n8n (e.g. webserver starts first, then n8n).

You can complete the assignment using **Docker (local)** or **AWS (cloud)** – same submission format as Lecture 6.

## Objectives

1. **Run a web server** – serves a simple page (e.g. landing or info page).
2. **Run n8n** – [n8n](https://n8n.io) workflow automation UI (default port 5678).
3. **Dependency order** – ensure the web server (and any other dependencies) are running **before** n8n starts.

## Two Options: Docker or AWS

| Option | Folder | Prerequisites |
|--------|--------|----------------|
| **Docker** | `assignment/docker/` | Terraform, Docker (local) |
| **AWS** | `assignment/aws/` | Terraform, AWS account & credentials |

### Docker (local)

- Uses Terraform Docker provider.
- **Order**: Terraform creates the webserver container first; n8n container has `depends_on = [webserver]` so it starts after.
- **Outputs**: `webserver_url` (e.g. http://localhost:8080), `n8n_url` (e.g. http://localhost:5678).

### AWS (cloud)

- Uses Terraform AWS provider; one EC2 instance.
- **Order**: `user_data` script (1) installs Docker, (2) runs the webserver container, (3) runs n8n container – so dependencies run before n8n.
- **Outputs**: `webserver_url` (http://&lt;public_ip&gt;:8080), `n8n_url` (http://&lt;public_ip&gt;:5678). Security groups open 8080 and 5678.

## Quick Start

### Docker

```bash
cd lecture7/assignment/docker
terraform init
terraform apply
# Webserver: http://localhost:8080
# n8n:       http://localhost:5678
terraform destroy   # when done
```

### AWS

```bash
cd lecture7/assignment/aws
terraform init
terraform apply
# Use the output URLs (replace <public_ip> with actual IP)
terraform destroy   # when done
```

## How to Submit

Same as Lecture 6 Terraform assignment:

1. **Screenshot** of the web server page in the browser (URL visible).
2. **Screenshot** of n8n UI in the browser (URL visible) or of `terraform output`.
3. Your **Terraform files** (e.g. `main.tf`, any variables/outputs).
4. **Pull Request** with the above.

### PR structure

```
lecture7/
├── assignment/
│   ├── docker/          # if you used Docker
│   │   ├── main.tf
│   │   └── ...
│   └── aws/             # if you used AWS
│       ├── main.tf
│       └── ...
├── LECTURE7_ASSIGNMENT_README.md
├── screenshot_webserver.png
├── screenshot_n8n.png
└── ...
```

### PR title example

```
Lecture 7: Web Server + n8n (Docker) - [Your Name]
```
or
```
Lecture 7: Web Server + n8n (AWS) - [Your Name]
```

## Dependency Order (what “run all dependencies before” means)

- **Docker**: The n8n container must have `depends_on` set to the webserver container (and any other resources that must exist first). Terraform will create/start the webserver first, then n8n.
- **AWS**: In `user_data`, run commands in sequence: install Docker → start webserver container → start n8n container. Do not start n8n before the webserver.

## Reference

- [n8n](https://n8n.io) – workflow automation
- [n8n Docker](https://hub.docker.com/r/n8nio/n8n) – official image
- Lecture 6 Terraform assignment (Docker webserver)
- Lecture 7 examples (Ch 1–3)
