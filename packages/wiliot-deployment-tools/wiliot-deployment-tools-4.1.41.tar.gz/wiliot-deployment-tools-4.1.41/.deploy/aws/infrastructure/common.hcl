# Common variables for all AWS accounts.
locals {
  # Prefix for the resource naming
  name_prefix = "wiliot"

  # Global domain
  global_domain = "wiliot.cloud"

  # Terraform label name for the resource tagging
  terraform_fingerprint = "terraform"

  # All the AWS account IDs.
  accounts = {
    dev   = "134407943939",
    test  = "467988592857",
    prod  = "398723525701",
    infra = "096303741971"
  }

  # Team responsible for the service
  team = "SRE"

  default_region = "us-east-2"

  app_name = "pywiliot-deployment-tools"

  #  # Istio gateways
  #  istio_mqtt_gateway    = "istio-system/public-mqtt-gw"
  #  istio_public_gateway  = "istio-system/public-gw"
  #  istio_private_gateway = "istio-system/private-gw"

  # Common tags set
  tags = {
    "Owner" = local.terraform_fingerprint
    "App"   = local.app_name
    "Team"  = local.team
  }

  # Databriks root secret
  dbc_mws_secret_arn = "arn:aws:secretsmanager:us-east-2:096303741971:secret:databriks-YzKQgO"

  # Prefix for the databricks resources
  databricks_prefix = "dbc"
}
