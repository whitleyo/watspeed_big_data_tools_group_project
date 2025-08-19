# biorxiv demo app

## Done:

* Route for basic abstract query service using embeddings + llama 8B instruct
* Data ingestion/load service (dump to S3, load to MongoDB)
* Local prototyping
* Successful deployment of app's data ingestion/load service on AWS with Docker

## TODO:

* Route for general summary
* Logic for running general summarization in background
* Separation of data service and front-facing app, clean up startup to give user more info on time to completion for startup tasks.
* See about using higher EC2 instances with half decent GPUs for compute (16 GB VRAM is probably a good start). Will necessitate a separation of compute, front-facing app, and DB.
* Public deployment.

## To Run (testing purposes):

Note: For development and testing. Not safe for deployment as traffic not encrypted.

### Docker

1. build (build.sh) or download image
2. run container: ``` sudo docker_run.sh ```. MongoDB will be started up on the app, as will jupyterlab and the quart server.
3. Wait for MongoDB to be populated. It should take about 2-5 minutes. Once this is done, you will see something like: 

```[2025-08-11 01:42:45 +0000] [82] [INFO] Running on http://0.0.0.0:5000 (CTRL + C to quit)```. 

This means you will be able to access the server at http://localhost:5000
5. click on the links on the landing page
6. localhost:5000/log will give you the most recent server logfile output

### Local

1. Install local MongoDB (see dockerfile for example installation)
2. Install anaconda/mamba
3. install environment: ``` mamba env create -f watspeed_data_gr_proj_docker.yml ```
4. Activate environment: ``` conda activate watspeed_data_gr_proj ```

## To Run production:

TODO.
