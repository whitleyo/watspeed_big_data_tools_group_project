#!/bin/bash

# Update system packages
sudo apt-get update -y

# Install Docker
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add the 'ubuntu' user to the docker group so you don't need sudo
sudo usermod -aG docker ubuntu

# Clone your repository
# IMPORTANT: Replace the URL with your actual repository URL
sudo apt-get install -y git
git clone https://github.com/whitleyo/watspeed_big_data_tools_group_project.git /home/ubuntu/app

# Change into the application directory and run Docker Compose
cd /home/ubuntu/app
sudo docker-compose -f docker-compose-aws.yml up -d