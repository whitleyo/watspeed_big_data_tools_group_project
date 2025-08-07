# Use Miniconda base image
FROM continuumio/miniconda3:latest

# Use bash as default shell for proper conda activation
SHELL ["/bin/bash", "-l", "-c"]

# Install mamba without clearing cache
RUN conda install -n base -c conda-forge mamba -y

# Set working directory
WORKDIR /app

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

# Entrypoint using conda run
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "watspeed_data_gr_proj", "hypercorn", "run:app", "--bind", "0.0.0.0:5000"]
