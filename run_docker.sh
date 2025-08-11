#!/bin/bash

# Run Docker container with environment variables and port mappings
# Port mappings:
# - 5000: Quart app
# - 8888: Jupyter Lab
# - 27018: MongoDB (mapped to 27017 inside the container)
docker run \
  -e AWS_ACCESS_KEY_ID=$(cat ./env/AWS_S3_access_key.txt) \
  -e AWS_SECRET_ACCESS_KEY=$(cat ./env/AWS_S3_secret_key.txt) \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e RUN_BACKGROUND_TASKS=true \
  -p 5000:5000 \
  -p 8888:8888 \
  -p 27018:27017 \
  watspeed-data-gr-proj-app
