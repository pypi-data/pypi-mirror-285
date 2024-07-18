export APP = wiliot-custom-events-svc
export CLOUD ?= aws
export ENV ?= dev
export BITBUCKET_COMMIT ?= local
export BITBUCKET_BUILD_NUMBER ?= local
export BITBUCKET_STEP_TRIGGERER_UUID ?= local
export AWS_REGION ?= us-east-2
export AWS_BUILD_REGION ?= us-east-2
export TERRAGRUNT_IAM_ROLE=$(shell eval echo $$$(shell echo ${ENV} | tr '[:lower:]' '[:upper:]')_TERRAGRUNT_IAM_ROLE)

$(CLOUD).plan.$(ENV):
	@echo 'Run plan on $(ENV)'
	(cd .deploy/$(CLOUD)/infrastructure/$(ENV) && terragrunt run-all plan --terragrunt-non-interactive)

$(CLOUD).apply.$(ENV):
	@echo 'Run apply on $(ENV)'
	(cd .deploy/$(CLOUD)/infrastructure/$(ENV) && terragrunt run-all apply --terragrunt-non-interactive)
