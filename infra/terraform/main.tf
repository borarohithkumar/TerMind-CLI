terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region for the temporary TerMind demo deployment."
  type        = string
  default     = "ap-south-1"
}

variable "ssh_cidr" {
  description = "Your current public IPv4 address with /32, e.g. 203.0.113.5/32. SSH is not exposed to the whole internet."
  type        = string
  validation {
    condition     = can(cidrhost(var.ssh_cidr, 0)) && can(regex("^[0-9.]+/[0-9]+$", var.ssh_cidr))
    error_message = "Provide your public IPv4 CIDR with /32, for example 203.0.113.5/32."
  }
}

variable "public_key_path" {
  description = "Path to the public half of the SSH key pair, on this machine."
  type        = string
  default     = "~/.ssh/termind-demo.pub"
}

variable "deployment_suffix" {
  description = "Short suffix for the Terraform-managed AWS resource names. Change this if these names already exist."
  type        = string
  default     = "demo-20261022"
}

variable "instance_type" {
  description = "8 GiB RAM instance chosen to give the ML API comfortable headroom for a short demo."
  type        = string
  default     = "t3.large"
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

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_key_pair" "termind" {
  key_name   = "termind-${var.deployment_suffix}-key"
  public_key = file(pathexpand(var.public_key_path))
}

resource "aws_security_group" "termind" {
  name        = "termind-${var.deployment_suffix}-sg"
  description = "Temporary TerMind demo: web ports public, SSH restricted to current IPv4."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH only from the configured current public IPv4 address"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  ingress {
    description = "HTTP for Nginx and ACME certificate validation"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS for the TerMind API"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound package downloads, model/API-related traffic, and updates"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "termind-${var.deployment_suffix}-sg"
    Project = "TerMind"
  }
}

resource "aws_instance" "termind" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = sort(data.aws_subnets.default.ids)[0]
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.termind.id]
  key_name                    = aws_key_pair.termind.key_name

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }

  user_data_replace_on_change = true
  user_data                   = <<-USERDATA
    #!/bin/bash
    set -euxo pipefail
    export DEBIAN_FRONTEND=noninteractive

    apt-get update
    apt-get install -y docker.io nginx certbot python3-certbot-nginx curl
    systemctl enable --now docker

    docker pull borarohithkumar/termind-api:v2.0
    docker run -d --name termind-api --restart unless-stopped \
      -p 127.0.0.1:8000:8000 borarohithkumar/termind-api:v2.0

    cat > /etc/nginx/sites-available/termind-api <<'NGINX'
    server {
      listen 80 default_server;
      listen [::]:80 default_server;
      server_name api.rbkreator.me;

      location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 120s;
      }
    }
    NGINX

    rm -f /etc/nginx/sites-enabled/default
    ln -sfn /etc/nginx/sites-available/termind-api /etc/nginx/sites-enabled/termind-api
    nginx -t
    systemctl enable --now nginx
  USERDATA

  tags = {
    Name    = "termind-${var.deployment_suffix}"
    Project = "TerMind"
    Purpose = "Temporary demo deployment; destroy when finished if you do not want ongoing charges"
  }
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.termind.id
}

output "public_ip" {
  description = "Public IPv4 address to set on the Namecheap api A record"
  value       = aws_instance.termind.public_ip
}

output "instance_type" {
  value = aws_instance.termind.instance_type
}
