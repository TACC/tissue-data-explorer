#!/bin/bash

# Get user ID and group ID
USERID=$(id -u)
GROUPID=$(id -g)

# Default settings will create a development environment with the start dataset
Env="dev"
Vol="config-data-dev"
Dataset="start"
Newvol="False"
Platform=""
Dtarget="dev-display"
Ctarget="dev-config"
Composefile="docker-compose-dev.yaml"

# Display help
Help()
{
  echo "Build the Docker containers for this project for use in development, testing, or production"
  echo
  echo "Syntax: build.sh [-e|v|d|n|h]"
  echo "options:"
  echo "e     The type of environment to build. Can be one of dev, test, or prod."
  echo "v     Specify the volume to use with the build."
  echo "d     Specify the dataset to use to create a new volume. Can be one of start or min."
  echo "n     Create a new volume."
  echo "h     Print this Help."
  echo
}

# Get input parameters
# options: dev, test, prod
while getopts "e:v:d:nh" option; do
  case $option in
    h) # display Help
      Help
      exit;;
    e) # Specify env
      Env=$OPTARG;;
    d) # which dataset to use for new volume
      Dataset=$OPTARG;;
    v) # Set volume to use
      Vol=$OPTARG;;
    n) # Create a new volume
      Newvol="True";;
    \?) # Invalid option
      exit;;
  esac
done

if [[ "$Newvol" == "True" ]]; then
  /bin/bash ./build/create_volume.sh $Vol ./data/$Dataset
fi

if [ "$Env" != "dev" ] && [ "$Env" != "test" ] && [ "$Env" != "prod" ]; then
  echo "Invalid environment choice. Environment can be one of dev, test, or prod."
  exit
elif [ "$Env" == "test" ] && [ "$Vol" == "config-data-dev" ]; then
  # default volume should be different for test
  Vol=config-data-test
elif [ "$Env" == "prod" ]; then
  # yes extra platform, no bind mounts
  if [ "$Vol" == "config-data-dev" ]; then
    Vol=config-data-prod
  fi
  Platform="linux/amd64"
  Dtarget=prod-display
  Ctarget=prod-config
  Composefile=docker-compose.yaml
fi

VOLUME=${Vol} PLATFORM=${Platform} DTARGET=${Dtarget} CTARGET=${Ctarget} USERID=$USERID GROUPID=$GROUPID docker compose -f ${Composefile} build &> ./build/build.log
VOLUME=${Vol} DTARGET=${Dtarget} CTARGET=${Ctarget} USERID=$USERID GROUPID=$GROUPID docker compose -f ${Composefile} up --detach


