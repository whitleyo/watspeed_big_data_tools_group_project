#!/bin/bash
# Start MongoDB in the background, logging to a file.
# The `--fork` flag allows the mongod process to run independently.
/usr/bin/mongod --fork --logpath /var/log/mongodb.log

# Check if mongod started successfully
if [ $? -ne 0 ]; then
  echo "Error: MongoDB failed to start."
  exit 1
fi

# Run the hypercorn server within the specified conda environment.
# `conda run` will activate the environment and execute the command.
conda run --no-capture-output -n watspeed_data_gr_proj hypercorn run:app --bind 0.0.0.0:5000