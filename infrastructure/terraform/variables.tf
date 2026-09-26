variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "clinical-evidence-coordinator"
}

variable "image_identifier" {
  type        = string
  description = "Full ECR image URI including tag."
  default     = ""
}
