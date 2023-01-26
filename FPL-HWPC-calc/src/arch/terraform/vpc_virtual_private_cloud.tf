resource "aws_internet_gateway" "igw_0603cd74d61b26c3c" {
  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_route_table" "rtb_08f2c098830c97e1f" {
  vpc_id = aws_vpc.hwpc_vpc.id
}

resource "aws_route_table" "rtb_0957192ee51df1349" {
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw_0603cd74d61b26c3c.id
  }

  vpc_id = aws_vpc.vpc_0012250a7646d8885.id
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

  name   = aws_vpc.hwpc_vpc.instance_tenancy
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

resource "aws_security_group" "sg_0523c7ba473645676" {
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

  name   = "default"
  vpc_id = aws_vpc.hwpc_vpc.id
}

resource "aws_security_group" "sg_086431530d4a3804d" {
  description = "Enables Dask and ECS communication between components of HWPC."
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

  name   = "hwpc-dask-sg"
  vpc_id = aws_vpc.hwpc_vpc.id
}

resource "aws_subnet" "hwpc_sbn" {
  tags = {
    Name = "hwpc-sbn"
  }

  tags_all = {
    Name = "hwpc-sbn"
  }

  availability_zone                   = "us-west-2d"
  cidr_block                          = "10.0.0.0/24"
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.hwpc_vpc.id
}

resource "aws_subnet" "subnet_00c7b79155a9bbab8" {
  availability_zone                   = "us-west-2c"
  cidr_block                          = "172.31.0.0/20"
  map_public_ip_on_launch             = true
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_subnet" "subnet_090dfbdf359cf77e7" {
  availability_zone                   = "us-west-2d"
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

resource "aws_subnet" "subnet_0b7d77536c6947df7" {
  availability_zone                   = "us-west-2d"
  cidr_block                          = "111.1.0.0/16"
  map_public_ip_on_launch             = true
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.hwpc_vpc.id
}

resource "aws_subnet" "subnet_0d21162897dfdc2ad" {
  availability_zone_id                = "usw2-az2"
  cidr_block                          = "172.31.32.0/20"
  map_public_ip_on_launch             = true
  private_dns_hostname_type_on_launch = "ip-name"
  vpc_id                              = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_vpc" "hwpc_vpc" {
  tags = {
    Name = "hwpc-vpc"
  }

  tags_all = {
    Name = "hwpc-vpc"
  }

  cidr_block         = "10.0.0.0/24"
  enable_dns_support = true
  instance_tenancy   = "default"
}

resource "aws_vpc" "vpc_0012250a7646d8885" {
  cidr_block           = "172.31.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  instance_tenancy     = "default"
}

