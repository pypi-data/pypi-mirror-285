include {
  path = find_in_parent_folders()
}

terraform {
  source = "git::git@bitbucket.org:wiliot/wiliot-cloud-modules.git//common/databricks/job-clusters"
}

generate "data" {
  path      = "data.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
variable "dbc_mws_secret_arn" {
  type = string
}



data "aws_secretsmanager_secret" "app_secret" {
  arn = var.dbc_mws_secret_arn
}

data "aws_secretsmanager_secret_version" "app_secret" {
  secret_id = data.aws_secretsmanager_secret.app_secret.id
}

locals {
  app_secrets = jsondecode(
    data.aws_secretsmanager_secret_version.app_secret.secret_string
  )
  username = local.app_secrets.username
  password = local.app_secrets.password
}

provider "databricks" {
  host     = "https://wiliot-e2-wiliot-dbc-prod.cloud.databricks.com/"
  username = local.username
  password = local.password
}
EOF
}

locals {
  # Automatically load common variables shared across all accounts
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))

  # Extract the name prefix for easy access
  name_prefix = "${local.common_vars.locals.name_prefix}-${local.common_vars.locals.databricks_prefix}"

  # Automatically load account-level variables
  account_vars = read_terragrunt_config(find_in_parent_folders("account.hcl"))

  # Extract the account_name for easy access
  account_name = local.account_vars.locals.account_name

  # Automatically load region-level variables
  region_vars = read_terragrunt_config(find_in_parent_folders("region.hcl"))

  # Extract the region for easy access
  aws_region = local.region_vars.locals.aws_region

  # Automatically load Databricks variables
  databricks_vars = read_terragrunt_config(find_in_parent_folders("dbc.hcl"))
}

inputs = {
  dbc_mws_secret_arn = local.common_vars.locals.dbc_mws_secret_arn
  environment        = local.account_name
  aws_region         = local.aws_region
  group_name         = "Databricks SystemNetworkProd_nocluster"

  clusters = {
    bridge_modulation = {
      email_notifications = {
        no_alert_for_skipped_runs = false
      },
      max_concurrent_runs = 1,
      tasks = [
        {
          task_key = "bridge_modulation",
          spark_python_task = {
            python_file = "wiliot_deployment_tools/internal/bridges_modulation/bridges_modulation.py"
            source      = "GIT"
          },
          job_cluster_key = "bridge_modulation_cluster",
          timeout_seconds = "0"
        }
      ],
      job_clusters = [
        {
          job_cluster_key = "bridge_modulation_cluster",
          new_cluster = {
            spark_version = "12.2.x-scala2.12",
            policy_id     = "9A644F43BC0001DE",
            spark_conf = {
              "spark.databricks.cluster.profile"          = "singleNode",
              "spark.executor.processTreeMetrics.enabled" = "true",
              "spark.master"                              = "local[*]",
              "spark.ui.prometheus.enabled"               = "true",
              "spark.sql.streaming.metricsEnabled"        = "true"
            },
            aws_attributes = {
              first_on_demand        = 1,
              availability           = "SPOT_WITH_FALLBACK",
              spot_bid_price_percent = 100,
              ebs_volume_count       = 1,
              ebs_volume_size        = 100,
              ebs_volume_type        = "GENERAL_PURPOSE_SSD",
              instance_profile_arn   = "${local.databricks_vars.locals.instance_profile_arn}"
            },
            init_scripts = [
              {
                s3 = {
                  destination = "s3://wiliot-dbc-us-east-2-prod-monitoring-and-logs/monitoring/init-scripts/initialize-metrics.sh",
                  region      = "us-east-2"
                }
              },
              {
                s3 = {
                  destination = "s3://wiliot-dbc-us-east-2-prod-monitoring-and-logs/job-clusters/init-scripts/system-network/install_packages.sh",
                  region      = "us-east-2"
                }
              }
            ],
            node_type_id        = "m5.xlarge",
            driver_node_type_id = "m5.xlarge",
            enable_elastic_disk = true,
            runtime_engine      = "STANDARD",
            num_workers         = 0,
            ResourceClass       = "SingleNode"
          }
        }
      ],
      git_source = {
        url      = "https://bitbucket.org/wiliot/pywiliot-deployment-tools.git",
        provider = "bitbucketCloud",
        branch   = "develop"
      }
    }
  }
}
