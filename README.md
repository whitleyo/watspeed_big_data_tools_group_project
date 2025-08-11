# watspeed_big_data_tools_group_project

## To Run (testing purposes):

Note: For development and testing. Not safe for deployment as traffic not encrypted.

### Docker

1. build (build.sh) or download image
2. run container: ``` sudo docker_run.sh ```. MongoDB will be started up on the app, as will jupyterlab and the quart server.
3. (optional) You can access jupyterlab through localhost:8888, with the appropriate auth token indicated in terminal. You will likely see something like this:
    To access the server, open this file in a browser:
        file:///root/.local/share/jupyter/runtime/jpserver-79-open.html
    Or copy and paste one of these URLs:
        http://f6b04ccd6509:8888/lab?token=90fea9382b284e057ad66555932e6574b0194c4ee756b253
        http://127.0.0.1:8888/lab?token=90fea9382b284e057ad66555932e6574b0194c4ee756b253
4. Wait for MongoDB to be populated. It should take about 2-5 minutes. Once this is done, you will see something like: 

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

TODO. But will use docker-compose.yml on EC2 instance. We have some local ssl certificates for testing purposes
but will have to figure out the CA certificates or other methods for basic security for EC2 deployment.
