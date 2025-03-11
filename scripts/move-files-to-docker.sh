#!/bin/bash

# If your project includes files that are too large to upload via the configuration portal,
# you can use this script to move the files into the docker container. The container must
# be running already for this to work.

declare -a files=("" 
                ""
                ""
                )

from='/source/path/'
to='container-name:/destination/path/'

for i in "${files[@]}"
do
  fname=${i#*/}
  docker cp "${from}${i}/${fname}.czi" "${to}${i}"
done