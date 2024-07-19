# Common variables for region
locals {
  # Automatically load account-level variables
  account_vars = read_terragrunt_config(find_in_parent_folders("account.hcl"))

  aws_region = "us-east-2"

  region_domain = "${local.aws_region}.${local.account_vars.locals.account_domain}"

  s3_kms_encryption_key_arn = "arn:aws:kms:us-east-2:134407943939:key/4e78b0bf-910c-4cc6-9019-c1408e6c4613"
}
