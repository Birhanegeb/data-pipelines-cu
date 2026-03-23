# Chapter 2: Getting Started – One Web Server
# EC2 + security group; serves "Hello, World" on port 8080.

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "example" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data = <<-EOF
    #!/bin/bash
    echo "Hello, World" > index.html
    nohup python3 -m http.server 8080 &
    EOF

  user_data_replace_on_change = true

  tags = {
    Name = "lecture7-ch2-one-webserver"
  }
}

resource "aws_security_group" "instance" {
  name = var.security_group_name

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "security_group_name" {
  type    = string
  default = "lecture7-ch2-webserver-sg"
}

output "public_ip" {
  value       = aws_instance.example.public_ip
  description = "Public IP; open http://<this_ip>:8080"
}
