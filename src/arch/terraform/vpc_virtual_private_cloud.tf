resource "aws_internet_gateway" "igw_0603cd74d61b26c3c" {
  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_route_table" "rtb_0957192ee51df1349" {
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw_0603cd74d61b26c3c.id
  }

  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_route_table" "rtb_0f6a29fa46fae7700" {
  vpc_id = aws_vpc.ecs_hwpc_web_cluster___vpc.id
}

resource "aws_security_group" "sg_0022db799b846e775" {
  description = "2022-10-06T18:35:16.972Z"
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  ingress {
    cidr_blocks      = ["0.0.0.0/0"]
    from_port        = 80
    ipv6_cidr_blocks = ["::/0"]
    protocol         = "tcp"
    to_port          = 80
  }

  ingress {
    cidr_blocks      = ["0.0.0.0/0"]
    from_port        = 443
    ipv6_cidr_blocks = ["::/0"]
    protocol         = "tcp"
    to_port          = 443
  }

  name   = "hwpc-web-security-group"
  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_security_group" "sg_004619e45649b9a84" {
  description = "default VPC security group"
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  ingress {
    from_port = 0
    protocol  = "-1"
    self      = true
    to_port   = 0
  }

  name   = aws_vpc.ecs_hwpc_web_cluster___vpc.instance_tenancy
  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_security_group" "sg_013bca134dc371041" {
  description = "2022-10-21T19:10:46.108Z"
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    protocol    = "tcp"
    to_port     = 80
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 443
    protocol    = "tcp"
    to_port     = 443
  }

  name   = "hwpc-calc-security-grp"
  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_security_group" "sg_0356d5f4aa0d5fbe8" {
  description = "Allow communication between tasks using an existing cluster."
  egress {
    cidr_blocks      = ["0.0.0.0/0"]
    from_port        = 0
    ipv6_cidr_blocks = ["::/0"]
    protocol         = "-1"
    to_port          = 0
  }

  ingress {
    cidr_blocks      = ["0.0.0.0/0"]
    from_port        = 8786
    ipv6_cidr_blocks = ["::/0"]
    protocol         = "tcp"
    to_port          = 8787
  }

  ingress {
    from_port = 0
    protocol  = "-1"
    self      = true
    to_port   = 0
  }

  name   = "hwpc-calc-fargate-sg"
  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_security_group" "sg_0d9a8b466f28c7f25" {
  description = "default VPC security group"
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  ingress {
    from_port = 0
    protocol  = "-1"
    self      = true
    to_port   = 0
  }

  name   = aws_vpc.ecs_hwpc_web_cluster___vpc.instance_tenancy
  vpc_id = "vpc-0da0dfeb6795dec34"
}

resource "aws_subnet" "subnet_00c7b79155a9bbab8" {
  availability_zone_id                = "usw2-az3"
  cidr_block                          = "172.31.0.0/20"
  map_public_ip_on_launch             = true
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_subnet" "subnet_090dfbdf359cf77e7" {
  availability_zone_id                = "usw2-az4"
  cidr_block                          = "172.31.48.0/20"
  map_public_ip_on_launch             = true
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_subnet" "subnet_0a67a553e8d4a6e46" {
  availability_zone_id                = "usw2-az1"
  cidr_block                          = "172.31.16.0/20"
  map_public_ip_on_launch             = true
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_subnet" "subnet_0d21162897dfdc2ad" {
  availability_zone_id                = "usw2-az2"
  cidr_block                          = "172.31.32.0/20"
  map_public_ip_on_launch             = true
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_vpc" "ecs_hwpc_web_cluster___vpc" {
  tags = {
    Description = "Created for ECS cluster hwpc-web-cluster"
    Name        = "ECS hwpc-web-cluster - VPC"
  }

  tags_all = {
    Description = "Created for ECS cluster hwpc-web-cluster"
    Name        = "ECS hwpc-web-cluster - VPC"
  }

  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  instance_tenancy     = "default"
}

resource "aws_vpc" "vpc_0012250a7646d8885" {
  cidr_block           = "172.31.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  instance_tenancy     = "default"
}

