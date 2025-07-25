# Use Miniconda for Conda environment support
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment and install
COPY watspeed_data_gr_proj.yml .
RUN conda env create -f watspeed_data_gr_proj.yml

# Activate environment
ENV PATH /opt/conda/envs/watspeed_data_gr_proj/bin:$PATH

# Copy app code
COPY . .

# Expose Quart app via Hypercorn
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "watspeed_data_gr_proj", "hypercorn", "run:app", "--bind", "0.0.0.0:5000"]
