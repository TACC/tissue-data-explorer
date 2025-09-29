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

3. Use the script `./build.sh` to build a development environment. If this is your first time building a development environment, you will need to create a new volume for use with the environment by providing the `-n` option to the program. The default behavior is to populate your new volume with some test data: 
   ```
   ./build.sh -n
   ```

   Or, if you would prefer to use a minimum dataset, you can specify that by providing the value `min` to the `-d` option. 
   ```
   ./build.sh -n -d min
   ```

   You can also specify a custom volume name using the `-v` option. 

   Running the script builds the apps and starts the display app at `localhost:8050` and the config app at `localhost:8040`.


## Running tests locally
The script `run_tests.sh` in the root project folder creates docker containers for the display and configuration apps, fills them with test data, runs the tests for the display app and config app, and then deletes the test containers and test volume.

```
./run_tests.sh
```

## Preparing the production image

1. On a machine with this project's GitHub repo, build the images. The build script as currently configured will create the production build for the `linux/amd64` and `linux/arm64` platforms. If neither of those platforms meet your needs, then you will need to update the platforms specified in `docker-compose.yaml` to fit the platform of your production server. See the Docker Compose [documentation](https://docs.docker.com/reference/compose-file/build/#platforms) for more information.

   Providing the value `prod` to the `-d` option of the build script will trigger a production build. You can specify a custom volume using the `-v` option as well.

   ```
   ./build.sh -e prod
   ```

2. Replace the variables in the code snippet below with your username and the appropriate version tag and run the commands to publish the images to Docker Hub

   ```
   docker tag tde-prod-display {username}/tissue-data-explorer-display:{tag}
   docker push {username}/tissue-data-explorer-display:{tag}
   docker tag tde-prod-config {username}/tissue-data-explorer-config:{tag}
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

5. Set up the shared volume. You can use the `./build/create_volume.sh` script to do this. If you are starting from scratch, you can use the data in the `data/start` folder to see a demo version of the app.

   You can copy the `data/start` folder and the `./build/create_volume.sh` script onto the production server and make the volume there. You must provide the name of the volume you want to create as well as the path to the source dataset as inputs to `./build/create_volume.sh` in that order:

   ```
   ./build/create_volume.sh config-data-prod ./data/start
   ```

   Alternatively, if the volume is not too large, you can make the volume on another machine using the above steps, then publish it to Docker Hub and pull it onto the production server.
      1. Export the volume by opening Docker Desktop, opening the volume, clicking on "Quick export", then choosing the "Registry" option under "Local or Hub storage".
      2. On the production server, create the new volume, pull the volume image from Docker Hub, run it, and copy the data into the volume on the production server.
      ```
      docker volume create config-data
      docker pull {username}/config-data:{tag}
      docker run -it --entrypoint /bin/sh --mount source=config-data,target=/config {username}/config-data:{tag}
      cp -r volume-data/* config
      ```

6. Run the image. The production containers should restart automatically if the server reboots due to the Docker restart policy.

   ```
   USERID=${UID} GROUPID=${GID} docker compose -f docker-compose-prod.yaml up
   ```

7. Clean up old images by running the `./build/clean_images.sh` script. This script will remove all containers and images with "tde-" in the name, then clean the Docker build cache.

## Preparing images for display on the website
See `scripts\image_prep.md` folder for more information about how to prepare images for display on the website. 

## Log in credentials for configuration site
The configuration app requires a file named `.env` in the root config app folder that contains the app secret and the credentials of authorized configuration portal users. See the file `.env.example` for file syntax and location.

## Serving custom reports
You can configure a page of links to any websites of your choice by uploading the list of links you want to include to the configuration portal. If you have project results reported in static HTML pages, you can customize the example configuration shown in `nginx/tde.conf` to serve those static HTML pages from certain routes within the app, and list those links on the reports page.

## Uploading large files
File uploads through the configuration portal are capped at 150MB. Larger files can be added to the display app docker container. An example script is at `scripts\move-files-to-docker.sh`.