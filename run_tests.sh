#!/bin/bash

/bin/bash ./build.sh -e test -v config-data-test -n
docker exec tde-dev-display-1 bash -c "python -m pytest"
docker stop tde-dev-display-1
docker rm tde-dev-display-1
docker exec tde-dev-config-1 bash -c "python -m pytest"
docker stop tde-dev-config-1
docker rm tde-dev-config-1
docker volume rm config-data-test

