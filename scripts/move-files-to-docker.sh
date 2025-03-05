#!/bin/bash

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