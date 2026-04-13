# 05 – Chapter 2: Web Server Cluster + Load Balancer

**Source:** *Terraform: Up and Running*, 3rd Ed., Chapter 2 – Getting Started.

## What this script does

- **Launch configuration** – same “Hello, World” HTTP server on a configurable port (default 8080).
- **Auto Scaling Group (ASG)** – 2–10 instances in the default VPC subnets.
- **Application Load Balancer (ALB)** – listens on port 80, forwards to the ASG.
- **Target group** – health checks on `/`; only healthy instances receive traffic.
- **Security groups** – one for instances (app port), one for ALB (port 80).

After apply, use the ALB DNS name: `http://<alb_dns_name>/` to see "Hello, World".

## Concepts

| Concept    | Where in the script |
|-----------|----------------------|
| Data sources | `aws_vpc`, `aws_subnets` – use default VPC/subnets |
| Launch config | `aws_launch_configuration` – template for each instance |
| ASG       | `aws_autoscaling_group` – min/max size, links to LC and target group |
| ALB       | `aws_lb` – application load balancer |
| Listener  | `aws_lb_listener` – port 80, default 404 |
| Listener rule | Forward `*` to target group |
| Lifecycle | `create_before_destroy` on launch config – required when ASG uses it |

## How to run

```bash
terraform init
terraform apply
# Test: curl http://$(terraform output -raw alb_dns_name)/
terraform destroy
```

## Prerequisites

- Terraform >= 1.0, AWS credentials, default VPC in the chosen region.
