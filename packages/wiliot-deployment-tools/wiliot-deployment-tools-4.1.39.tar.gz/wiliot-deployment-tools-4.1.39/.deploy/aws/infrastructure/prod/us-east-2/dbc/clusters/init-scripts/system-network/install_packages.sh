#!/bin/bash
apt-get update && apt-get install curl unzip -y
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws codeartifact login --tool pip --domain wiliot-cloud --domain-owner 096303741971 --repository pypi --region us-east-2

LATEST_VERSION=$(aws codeartifact list-package-versions --package wiliot-deployment-tools --domain wiliot-cloud --domain-owner 096303741971 --repository pypi --region us-east-2 --format pypi --output text --query 'versions[*].[version]' --max-results 1 --sort-by PUBLISHED_TIME)

PACKAGES="wiliot-deployment-tools==${LATEST_VERSION} wiliot-api wiliot-core offline-analytics-common"
OFFLINE_ANALYTICS_DEPS="sqlalchemy python-json-logger rich loguru tqdm"
/databricks/python/bin/pip install --upgrade pip
/databricks/python/bin/pip install --no-cache ${PACKAGES}
/databricks/python/bin/pip install ${OFFLINE_ANALYTICS_DEPS}