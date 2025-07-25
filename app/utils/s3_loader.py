import boto3
import json
from app.config import S3_BUCKET, AWS_REGION

s3 = boto3.client("s3", region_name=AWS_REGION)

async def load_json_from_s3(key):
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    contents = obj['Body'].read().decode('utf-8')
    return json.loads(contents)
