terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ── Provider ────────────────────────────────────────────────────────────────
provider "aws" {
  region = "us-east-1"   # change to your preferred region
}

# ── Data: latest Amazon Linux 2023 AMI ──────────────────────────────────────
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# ── Security Group ───────────────────────────────────────────────────────────
resource "aws_security_group" "web_n8n_sg" {
  name        = "lecture7-web-n8n-sg"
  description = "Allow HTTP traffic for webserver (8080) and n8n (5678)"

  ingress {
    description = "Webserver port"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "n8n port"
    from_port   = 5678
    to_port     = 5678
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # restrict to your IP for production
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lecture7-sg"
  }
}

# ── EC2 Instance ─────────────────────────────────────────────────────────────
resource "aws_instance" "lecture7" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t3.micro"            # free-tier eligible
  vpc_security_group_ids      = [aws_security_group.web_n8n_sg.id]
  associate_public_ip_address = true

  # user_data runs on first boot — ORDER MATTERS:
  # 1. Install Docker
  # 2. Start webserver  ← must come before n8n
  # 3. Start n8n
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # 1 ── Install Docker
    yum update -y
    yum install -y docker
    systemctl enable docker
    systemctl start docker

    # 2 ── Start the webserver (nginx on port 8080)
    docker run -d \
      --name webserver \
      --restart unless-stopped \
      -p 8080:80 \
      nginx:alpine

    # Wait until the webserver container is healthy before continuing
    until docker inspect -f '{{.State.Running}}' webserver 2>/dev/null | grep -q true; do
      echo "Waiting for webserver..."
      sleep 2
    done

    # 3 ── Start n8n (depends on webserver being up first)
    docker run -d \
        --name n8n \
        --restart unless-stopped \
        -p 5678:5678 \
        -e N8N_BASIC_AUTH_ACTIVE=false \
        -e N8N_SECURE_COOKIE=false \
        n8nio/n8n:latest
  EOF

  tags = {
    Name = "lecture7-web-n8n"
  }
}

# ── Outputs ──────────────────────────────────────────────────────────────────
output "webserver_url" {
  description = "URL of the web server"
  value       = "http://${aws_instance.lecture7.public_ip}:8080"
}

output "n8n_url" {
  description = "URL of the n8n workflow automation UI"
  value       = "http://${aws_instance.lecture7.public_ip}:5678"
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.lecture7.public_ip
}