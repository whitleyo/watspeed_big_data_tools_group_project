from dotenv import load_dotenv, find_dotenv
import os
import boto3

def get_boto3_client(service_name, dotenv_path='env/.env'):
    # Try to find and load .env
    dotenv_path = find_dotenv(dotenv_path)
    if dotenv_path:
        load_dotenv(dotenv_path)
        print("Loaded .env — assuming local environment")
        return boto3.client(
            service_name,
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        )
    else:
        print("No .env found — assuming EC2/IAM environment")
        return boto3.client(service_name)