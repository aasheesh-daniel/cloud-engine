terraform {
  required_version = ">= 1.5.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

resource "local_file" "day1_test" {
  content  = "Autonomous Cloud Elasticity Engine - Day 1 Setup Successful!"
  filename = "${path.module}/day1_output.txt"
}