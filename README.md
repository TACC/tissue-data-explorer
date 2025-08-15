# Tissue Data Explorer

This project contains the code necessary to create a website that showcases scientific data collected on a tissue sample. Types of data handled by this example include multi-channel image stacks, volumetric map data, and 3D models. This repository includes synthetic data that can be used to stand up a demo website, as well as a configuration portal that can be used to upload project data to the site.

## Prerequisites
Docker/ Docker Compose

## Getting Started with Development
1. Clone this repo

   ```
   git clone https://github.com/TACC/tissue-data-explorer.git
   ```

2. Add a `.env` file to the `config_portal` folder. See `.env.example` for format.

3. Create a volume called `config-data-dev`. If you want to use the test data provided with this environment, populate the volume with the data from the `start` folder. Otherwise you can create an empty environment by populating the volume with the data from the `min` folder.

   ```
   docker volume create config-data-dev
   docker run -d --name temp -v config-data-dev:/data busybox sleep infinity
   docker cp ./start/. temp:/data/
   docker stop temp
   docker rm temp
   ```

4. Build the image

   ```
   docker compose -f docker-compose-dev.yaml build
   ```

5. Run the image

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
   docker rm -f $(docker ps -aq --filter "name=tissue-data-explorer")
   docker rmi -f $(docker images -q --filter=reference='tissue-data-explorer*')
   docker volume rm config-data-dev
   docker builder prune
   ```

## Preparing images for display on the website
See `scripts\image_prep.md` folder for more information about how to prepare images for display on the website. 

## Log in credentials for configuration site
The configuration app requires a file named `.env` in the root config app folder that contains the app secret and the credentials of authorized configuration portal users. See the file `.env.example` for file syntax and location.

## Serving custom reports
You can configure a page of links to any websites of your choice by uploading the list of links you want to include to the configuration portal. If you have project results reported in static HTML pages, you can customize the example configuration shown in `nginx/tde.conf` to serve those static HTML pages from certain routes within the app, and list those links on the reports page.

## Uploading large files
File uploads through the configuration portal are capped at 150MB. Larger files can be added to the display app docker container. An example script is at `scripts\move-files-to-docker.sh`.