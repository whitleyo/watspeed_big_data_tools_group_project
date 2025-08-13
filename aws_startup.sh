#!/bin/bash

# Update system packages
sudo yum update -y

# Install Docker
sudo amazon-linux-extras enable docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Add the 'ec2-user' to the docker group so you don't need sudo
sudo usermod -aG docker ec2-user

# Install Docker Compose (v2.x binary)
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install -y git

# Clone your repository
git clone https://github.com/whitleyo/watspeed_big_data_tools_group_project.git /home/ec2-user/app

# Change into the application directory and run Docker Compose
cd /home/ec2-user/app
sudo docker-compose -f docker-compose-aws.yml up -d