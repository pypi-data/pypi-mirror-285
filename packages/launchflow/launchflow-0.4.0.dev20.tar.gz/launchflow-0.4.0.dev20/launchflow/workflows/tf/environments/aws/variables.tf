
variable "aws_region" {
  type = string
}

variable "launchflow_project" {
  type = string
}

variable "launchflow_environment" {
  type = string
}

variable "aws_account_id" {
  type = string
}

# TODO: add this back once we've ironed out how launchflow
# will get access to the users environment
# variable "launchflow_role_name" {
#   type = string
# }

variable "artifact_bucket_name" {
  type = string
}
