# # Use Miniconda base image
# FROM continuumio/miniconda3:latest

# User Ubuntu as the base image
FROM ubuntu:24.04

# Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/conda/bin:$PATH"

# Install system dependencies and Miniconda
RUN apt-get update && \
    apt-get install -y wget curl gnupg ca-certificates bzip2 && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

# Use bash as default shell for proper conda activation
SHELL ["/bin/bash", "-l", "-c"]

# Force accepting the license agreement
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Install mamba without clearing cache
RUN conda install -n base -c conda-forge mamba -y

# Set working directory
WORKDIR /app

# Install system dependencies including MongoDB
RUN apt-get update && \
    apt-get install -y gnupg curl && \
    curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg && \
    echo "deb [ arch=amd64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org

# Copy environment file
COPY watspeed_data_gr_proj_docker.yml .



# Use BuildKit cache mount to preserve Conda packages
RUN --mount=type=cache,target=/opt/conda/pkgs \
    mamba env create -f watspeed_data_gr_proj_docker.yml

# Set environment path (no need to activate in RUN)
ENV PATH="/opt/conda/envs/watspeed_data_gr_proj/bin:$PATH"

# Install kernel (optional, only needed for Jupyter)
RUN mamba run -n watspeed_data_gr_proj python -m ipykernel install --user --name watspeed_data_gr_proj

# Clean up (optional for production)
RUN conda clean -afy

# Copy project files
COPY . .

RUN mkdir -p /var/log && touch /var/log/mongodb.log && \
    mkdir -p /data/db && chown -R mongodb:mongodb /data/db

CMD ["bash", "-c", "\
  mongod --fork --logpath /var/log/mongodb.log && \
  conda run --no-capture-output -n watspeed_data_gr_proj jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root & \
  conda run --no-capture-output -n watspeed_data_gr_proj hypercorn run:app --bind 0.0.0.0:5000"]
