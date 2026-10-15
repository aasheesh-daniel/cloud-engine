terraform {
  required_version = ">= 1.5.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

variable "environment" {
  type    = string
  default = "development"
}

resource "local_file" "engine_config" {
  content  = "PROJECT: Autonomous Cloud Elasticity Engine\nENV: ${var.environment}"
  filename = "${path.module}/config.env"
}