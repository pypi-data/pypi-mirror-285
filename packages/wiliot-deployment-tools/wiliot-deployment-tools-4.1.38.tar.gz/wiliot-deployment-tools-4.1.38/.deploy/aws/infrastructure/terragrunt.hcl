locals {
  # Load common vars
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))

  # Automatically load account-level variables
  account_vars = read_terragrunt_config(find_in_parent_folders("account.hcl"))

  # Automatically load region-level variables
  region_vars = read_terragrunt_config(find_in_parent_folders("region.hcl"))

  name_prefix  = local.common_vars.locals.name_prefix
  account_name = local.account_vars.locals.account_name
  aws_region   = local.region_vars.locals.aws_region
  app_name     = local.common_vars.locals.app_name
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
}
EOF
}

remote_state {
  backend = "s3"
  config = {
    encrypt        = true
    bucket         = "${local.name_prefix}-${local.account_name}-${local.aws_region}-${local.app_name}-tf-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = local.aws_region
    dynamodb_table = "terraform-locks"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

inputs = local.common_vars.locals

terraform_version_constraint  = ">= 1.0.0"
terragrunt_version_constraint = ">= 0.34.0"
