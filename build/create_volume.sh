#!/bin/bash

docker volume create $1
docker run -d --name temp -v $1:/data busybox sleep infinity
docker cp $2/. temp:/data/
docker stop temp
docker rm temp