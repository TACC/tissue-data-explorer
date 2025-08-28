#!/bin/bash

docker rm -f $(docker ps -aq --filter "name=tde-")
docker rmi -f $(docker images -q --filter=reference='tde-*')
docker builder prune