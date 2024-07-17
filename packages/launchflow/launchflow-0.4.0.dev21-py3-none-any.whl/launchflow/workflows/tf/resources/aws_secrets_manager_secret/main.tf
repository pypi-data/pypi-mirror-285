provider "aws" {
  allowed_account_ids = [var.aws_account_id]
  region              = var.aws_region
}

resource "aws_secretsmanager_secret" "secret" {
  name                    = var.resource_id
  recovery_window_in_days = var.recovery_window_in_days
  tags = {
    "Project" : var.launchflow_project,
    "Environment" : var.launchflow_environment
  }
}


output "secret_id" {
  value = aws_secretsmanager_secret.secret.id
}


output "aws_arn" {
  value = aws_secretsmanager_secret.secret.arn
}
