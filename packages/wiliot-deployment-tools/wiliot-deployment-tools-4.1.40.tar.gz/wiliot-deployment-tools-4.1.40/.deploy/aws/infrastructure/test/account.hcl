# Set account variables
locals {
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))

  account_name     = "test"
  account_domain   = "${local.account_name}.${local.common_vars.locals.global_domain}"
  eks_cluster_name = "${local.common_vars.locals.name_prefix}-${local.account_name}"

  # Set the account-wide tags
  tags = merge({
    "Environment" = local.account_name
  }, local.common_vars.locals.tags)
}
