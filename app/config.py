import os
# Edit according to your environment variables or defaults
DOCUMENTDB_URI = os.getenv("DOCUMENTDB_URI", "mongodb://your-docdb-endpoint:27017")
DOCUMENTDB_CA_FILE = os.getenv("DOCUMENTDB_CA_FILE", "/path/to/rds-combined-ca-bundle.pem")

S3_BUCKET = os.getenv("S3_BUCKET", "your-bucket-name")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
