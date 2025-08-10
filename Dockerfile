# Use Miniconda base image
FROM continuumio/miniconda3:latest

# Use bash as default shell for proper conda activation
SHELL ["/bin/bash", "-l", "-c"]

# Install mamba without clearing cache
RUN conda install -n base -c conda-forge mamba -y

# Set working directory
WORKDIR /app

# Install system dependencies including MongoDB
RUN apt-get update && \
    apt-get install -y gnupg curl && \
    curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg && \
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org && \
    mkdir -p /data/db

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

# Start MongoDB and Quart app
CMD mongod --fork --logpath /var/log/mongodb.log && \
    conda run --no-capture-output -n watspeed_data_gr_proj hypercorn run:app --bind 0.0.0.0:5000
