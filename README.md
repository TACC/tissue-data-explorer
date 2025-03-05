# HuBMAP Pancreas Data Explorer

This site visualizes pancreas data collected as part of the HuBMAP project, which aims to collect cell-level data for every organ in the human body.

## Prerequisites
Docker/ Docker Compose

## Getting Started with development
1. Clone this repo

   ```
   git clone https://github.com/james-labyer/HuBMAP-pancreas-data-explorer.git
   ```

2. Some of the files in this project are too large to check into GitHub. The GitHub repo includes representative examples that use smaller files. If you want to view the larger files, download them and move them into the appropriate subfolders in:

   ```
   app/assets/optical-clearing-czi
   ```

3. Build the image

   ```
   cd app
   docker compose -f docker-compose-dev.yaml build
   ```

4. Run the image

   ```
   docker compose -f docker-compose-dev.yaml up
   ```

   Running the image starts the app at localhost:8050. Hot reloading within the Docker container does not work currently, but since the dev image uses a mount, you can see the changes by starting and stopping the container without rebuilding it.


## Running tests locally
Run pytest within a development container:
```
docker exec {container_name} pytest --cov-report term-missing --cov
```

## Preparing the production image

1. On your machine, build the image

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

4. Run the image and test it

   ```
   docker run -p 127.0.0.1:8050:8050 jlabyer/hubmap-pancreas-data-explorer:{tag}
   ```

5. Clean up old images

   ```
   docker system prune -a --volumes
   ```

## Preparing assets for display on the website
See the `documentation` folder for more information about how to prepare optical clearing files and 3d model files for display on the website. 