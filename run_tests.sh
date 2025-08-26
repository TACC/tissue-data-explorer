#!/bin/bash

USERID=$(id -u)
GROUPID=$(id -g)

docker volume create config-data-test
docker run -d --name temp -v config-data-test:/data busybox sleep infinity
docker cp ./start/. temp:/data/
docker stop temp
USERID=$USERID GROUPID=$GROUPID docker compose -f docker-compose-test.yaml build &> build.log
USERID=$USERID GROUPID=$GROUPID docker compose -f docker-compose-test.yaml up --detach
docker exec tissue-data-explorer-display-1 bash -c "python -m pytest"
docker stop tissue-data-explorer-display-1
docker rm tissue-data-explorer-display-1
docker exec tissue-data-explorer-config-1 bash -c "python -m pytest"
docker stop tissue-data-explorer-config-1
docker rm tissue-data-explorer-config-1
docker rm temp
docker volume rm config-data-test

