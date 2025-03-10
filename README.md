# Tissue Data Explorer

This project contains the code necessary to create a website that showcases scientific data collected on a tissue sample. Types of data handled by this example include multi-channel image stacks, volumetric map data, and 3D models. This repository includes synthetic data that can be used to stand up a demo website, as well as a configuration portal that can be used to upload actual project data to the site.

## Prerequisites
Docker/ Docker Compose

## Getting Started with Development
1. Clone this repo

   ```
   git clone https://github.com/TACC/tissue-data-explorer.git
   ```

2. Build the image

   ```
   cd app
   docker compose -f docker-compose-dev.yaml build
   ```

3. Run the image

   ```
   docker compose -f docker-compose-dev.yaml up
   ```

   Running the image starts the display app at `localhost:8050` and the config app at `localhost:8040`.


## Running tests locally
The script `run_tests.sh` in the root project folder creates docker containers for the display and configuration apps, fills them with test data, runs the tests, and then deletes the test containers and test volume.

```
./run_tests.sh
```

## Preparing the production image

1. On your machine, build the image, the password .env for config will not be included

   ```
   docker compose -f docker-compose.yaml build
   ```

2. Publish the image to Docker Hub

   ```
   docker tag hubmap-pancreas-data-explorer-dash-app jlabyer/hubmap-pancreas-data-explorer:{tag}
   docker push jlabyer/hubmap-pancreas-data-explorer:{tag}
   ```

3. On the production server, pull the newly published image from Docker Hub

   ```
   docker pull jlabyer/hubmap-pancreas-data-explorer:{tag}
   ```

4. Set up the blank shared volume 

5. Run the image and put in the .env

   ```
   docker run -p 127.0.0.1:8050:8050 jlabyer/hubmap-pancreas-data-explorer:{tag}
   ```
docker cp ./config_portal/.env tissue-data-explorer-config-1:app


6. Clean up old images

   ```
   docker system prune -a --volumes
   ```

7. You can back up a copy of the shared volume and put it on Docker Hub

## Preparing assets for display on the website
See the `documentation` folder for more information about how to prepare optical clearing files and 3d model files for display on the website. 

## Log in credentials for configuration site
The configuration app requires a file named `.env` in the root config app folder that contains the app secret and the credentials of authorized configuration portal users. See the file `.env.example` for file syntax and location.

