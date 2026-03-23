# Chapter 2: Getting Started – Web Server Cluster + Load Balancer
# ASG + ALB; cluster serves "Hello, World", ALB on port 80.

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

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Launch configuration for the ASG
resource "aws_launch_configuration" "example" {
  image_id        = data.aws_ami.amazon_linux.id
  instance_type   = "t2.micro"
  security_groups = [aws_security_group.instance.id]

  user_data = <<-EOF
    #!/bin/bash
    echo "Hello, World" > index.html
    nohup python3 -m http.server ${var.server_port} &
    EOF

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "example" {
  launch_configuration = aws_launch_configuration.example.name
  vpc_zone_identifier  = data.aws_subnets.default.ids
  target_group_arns    = [aws_lb_target_group.asg.arn]
  health_check_type   = "ELB"

  min_size = 2
  max_size = 10

  tag {
    key                 = "Name"
    value               = "lecture7-ch2-asg-example"
    propagate_at_launch = true
  }
}

# Security group for instances
resource "aws_security_group" "instance" {
  name = var.instance_sg_name

  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Application Load Balancer
resource "aws_lb" "example" {
  name               = var.alb_name
  load_balancer_type = "application"
  subnets            = data.aws_subnets.default.ids
  security_groups    = [aws_security_group.alb.id]
}

# ALB security group – allow 80 from internet
resource "aws_security_group" "alb" {
  name = var.alb_sg_name

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Target group for ASG
resource "aws_lb_target_group" "asg" {
  name     = var.alb_name
  port     = var.server_port
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 3
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

# Listener – default 404
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.example.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "404: page not found"
      status_code  = 404
    }
  }
}

# Forward all paths to target group
resource "aws_lb_listener_rule" "asg" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  condition {
    path_pattern {
      values = ["*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.asg.arn
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "server_port" {
  type    = number
  default = 8080
}

variable "alb_name" {
  type    = string
  default = "lecture7-ch2-alb"
}

variable "instance_sg_name" {
  type    = string
  default = "lecture7-ch2-instance-sg"
}

variable "alb_sg_name" {
  type    = string
  default = "lecture7-ch2-alb-sg"
}

output "alb_dns_name" {
  value       = aws_lb.example.dns_name
  description = "DNS name of the load balancer; use: http://<this_value>/"
}
