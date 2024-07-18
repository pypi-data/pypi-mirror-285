locals {
  common_vars          = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  account_vars         = read_terragrunt_config(find_in_parent_folders("account.hcl"))
  instance_profile_arn = "arn:aws:iam::467988592857:instance-profile/wiliot-dbc-test-general-instance-profile"

  tags = merge({
    "System" = "Databricks"
  }, local.account_vars.locals.tags)
}
