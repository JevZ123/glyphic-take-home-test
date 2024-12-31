terraform {
  backend "s3" {
    bucket         = "jevz123-terraform-state"
    key            = "glyphic/frontend/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.82.2"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}