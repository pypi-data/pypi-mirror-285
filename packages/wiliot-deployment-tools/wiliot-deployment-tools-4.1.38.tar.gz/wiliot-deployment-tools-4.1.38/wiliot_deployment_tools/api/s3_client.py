import json
import boto3
from wiliot_deployment_tools.common.analysis_data_bricks import get_secret
from wiliot_deployment_tools.common.debug import is_databricks
bucket_name = 'wiliot-gateway-versions-non-prod'
class S3Client():
    def __init__(self):
        if is_databricks():
            access_key = get_secret('warehouse', 'AWS_ACCESS_KEY_ID')
            secret_key = get_secret('warehouse', 'AWS_SECRET_ACCESS_KEY')
            self.s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        else:
            self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(bucket_name)   
    
    def get_gw_validation_json(self, gw_type, version):
        item = self.s3.Object(bucket_name, f'v2/{gw_type}/validation/gw_validation/{version}.json')
        return json.loads(item.get()['Body'].read().decode('utf-8'))['properties']
        
    def get_brg_validation_json(self, gw_type, version):
        item = self.s3.Object(bucket_name, f'v2/{gw_type}/validation/bridge_validation/{version}.json')
        return json.loads(item.get()['Body'].read().decode('utf-8'))['properties']