# Chapter 1: Why Terraform – Hello Terraform
# Minimal example: one EC2 instance. Shows provider + resource.

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

# Latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "example" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"

  tags = {
    Name = "lecture7-ch1-hello-terraform"
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

output "instance_id" {
  value       = aws_instance.example.id
  description = "EC2 instance ID"
}

output "public_ip" {
  value       = aws_instance.example.public_ip
  description = "Public IP of the instance"
}
