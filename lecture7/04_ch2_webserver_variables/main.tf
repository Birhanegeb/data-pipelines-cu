# Chapter 2: Getting Started – Web Server with Variables
# Same webserver as 03, but port and names are variables.

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
    nohup python3 -m http.server ${var.server_port} &
    EOF

  user_data_replace_on_change = true

  tags = {
    Name = "lecture7-ch2-webserver-vars"
  }
}

resource "aws_security_group" "instance" {
  name = var.security_group_name

  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "server_port" {
  description = "Port for the HTTP server"
  type        = number
  default     = 8080
}

variable "security_group_name" {
  type    = string
  default = "lecture7-ch2-webserver-sg"
}

output "public_ip" {
  value = aws_instance.example.public_ip
}

output "url" {
  value = "http://${aws_instance.example.public_ip}:${var.server_port}"
}
