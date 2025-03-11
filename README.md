# Tissue Data Explorer

This project contains the code necessary to create a website that showcases scientific data collected on a tissue sample. Types of data handled by this example include multi-channel image stacks, volumetric map data, and 3D models. This repository includes synthetic data that can be used to stand up a demo website, as well as a configuration portal that can be used to upload project data to the site.

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
The script `run_tests.sh` in the root project folder creates docker containers for the display and configuration apps, fills them with test data, runs the tests for the display app and config app, and then deletes the test containers and test volume.

```
./run_tests.sh
```

## Preparing the production image

1. On a machine with this project's GitHub repo, build the images. You may need to update the platforms specified in `docker-compose.yaml` to fit the platform of your production server. See the Docker Compose [documentation](https://docs.docker.com/reference/compose-file/build/#platforms) for more information.

   ```
   docker compose -f docker-compose.yaml build
   ```

2. Replace the variables in the code snippet below with your username and the appropriate version tag and run the commands to publish the images to Docker Hub

   ```
   docker tag tissue-data-explorer-display {username}/tissue-data-explorer-display:{tag}
   docker push {username}/tissue-data-explorer-display:{tag}
   docker tag tissue-data-explorer-config {username}/tissue-data-explorer-config:{tag}
   docker push {username}/tissue-data-explorer-config:{tag}
   ```

3. On the production server, pull the newly published images from Docker Hub

   ```
   docker pull {username}/tissue-data-explorer-display:{tag}
   docker pull {username}/tissue-data-explorer-config:{tag}
   ```

4. Copy the `docker-compose-prod.yaml` file and your `.env` file for the production configuration app onto the production server. You will need to make the following changes to `docker-compose-prod.yaml`:
   - update the variables in the image names with your username and the version tag
   - for the env_file setting in the config service, update the path of the .env file relative to the compose file. So, if you copied `docker-compose-prod.yaml` and `.env` into the same directory, the path for env_file should be `./.env`.

5. Set up the shared volume. If you are starting from scratch, you can use the data in the `start` folder to see a demo version of the app.

   You can copy the `start` folder onto the production server and make the volume there:

   ```
   docker volume create config-data
   docker run -d --name temp -v config-data:/data busybox sleep infinity
   docker cp ./start/. temp:/data/
   docker stop temp
   docker rm temp
   ```

   Alternatively, you can make the volume on another machine using the above steps, then publish it to Docker Hub and pull it onto the production server.
      1. Export the volume by opening Docker Desktop, opening the volume, clicking on "Quick export", then choosing the "Registry" option under "Local or Hub storage".
      2. On the production server, create the new volume, pull the volume image from Docker Hub, run it, and copy the data into the volume on the production server.
      ```
      docker volume create config-data
      docker pull {username}/config-data:{tag}
      docker run -it --entrypoint /bin/sh --mount source=config-data,target=/config {username}/config-data:{tag}
      cp -r volume-data/* config
      ```

6. Run the image.

   ```
   docker compose -f docker-compose-prod.yaml up
   ```

7. Clean up old images

   ```
   docker image prune -a
   ```

## Preparing assets for display on the website
See the `documentation` folder for more information about how to prepare optical clearing files and 3d model files for display on the website. 

## Log in credentials for configuration site
The configuration app requires a file named `.env` in the root config app folder that contains the app secret and the credentials of authorized configuration portal users. See the file `.env.example` for file syntax and location.

