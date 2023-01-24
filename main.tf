terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version= ">= 1.2.0"
  backend "s3" {
    bucket = "hwpc-test-bucket"
    key    = "terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
    region = "us-west-2"
    access_key = "AKIATNIWM26NFV4GY5UV"
    secret_key = "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"
}

module "terraform" {
    source = "/hwpc-calc/src/arch/terraform"
    
}