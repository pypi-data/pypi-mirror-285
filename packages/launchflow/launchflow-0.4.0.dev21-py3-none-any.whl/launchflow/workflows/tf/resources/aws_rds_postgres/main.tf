provider "aws" {
  allowed_account_ids = [var.aws_account_id]
  region              = var.aws_region
  default_tags {
    tags = {
      Project     = var.launchflow_project
      Environment = var.launchflow_environment
    }
  }
}

data "aws_subnets" "lf_vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
  tags = {
    "Project" : var.launchflow_project,
    "Environment" : var.launchflow_environment
    "Public" : var.publicly_accessible ? "true" : "false"
  }
}

data "aws_subnet" "details" {
  for_each = toset(data.aws_subnets.lf_vpc_subnets.ids)
  id       = each.value
}

resource "aws_db_subnet_group" "default" {
  name        = "${var.launchflow_project}-${var.launchflow_environment}-${var.resource_id}-subnet-group"
  subnet_ids  = data.aws_subnets.lf_vpc_subnets.ids
  description = "Subnet group for ${var.launchflow_project}-${var.launchflow_environment}-${var.resource_id}"
}

# Define a Security Group for public access (only for public instances)
resource "aws_security_group" "rds_sg" {
  count       = var.publicly_accessible ? 1 : 0
  name        = "${var.launchflow_project}-${var.launchflow_environment}-${var.resource_id}-rds-sg"
  description = "Allow inbound traffic"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project     = var.launchflow_project
    Environment = var.launchflow_environment
  }
}

resource "aws_db_instance" "default" {
  identifier_prefix      = substr("${var.resource_id}-${var.launchflow_environment}-", 0, 55)
  allocated_storage      = var.allocated_storage_gb
  db_name                = var.database_name
  engine                 = "postgres"
  instance_class         = "db.t4g.micro"
  username               = "${var.database_name}User"
  password               = random_password.user-password.result
  skip_final_snapshot    = true
  publicly_accessible    = var.publicly_accessible
  vpc_security_group_ids = var.publicly_accessible ? [aws_security_group.rds_sg[0].id] : []
  multi_az               = var.highly_available
  db_subnet_group_name   = aws_db_subnet_group.default.name
}

resource "aws_iam_policy" "policy" {
  name = "${var.launchflow_project}-${var.launchflow_environment}-${var.resource_id}-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "rds:*",
        ]
        Effect = "Allow"
        Resource = [
          local.aws_arn
        ]
      },
    ]
  })
  tags = {
    "Project" : var.launchflow_project,
    "Environment" : var.launchflow_environment
  }
}

resource "random_password" "user-password" {
  length  = 16
  special = false
}

locals {
  endpoint = aws_db_instance.default.endpoint
  username = aws_db_instance.default.username
  password = aws_db_instance.default.password
  port     = aws_db_instance.default.port
  dbname   = aws_db_instance.default.db_name
  aws_arn  = aws_db_instance.default.arn
}


output "endpoint" {
  value = local.endpoint
}

output "username" {
  value = local.username
}

output "password" {
  value     = local.password
  sensitive = true
}

output "port" {
  value = local.port
}

output "dbname" {
  value = local.dbname
}

output "region" {
  value = var.aws_region
}

output "aws_arn" {
  value = local.aws_arn
}
