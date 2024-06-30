#!/usr/bin/env bash
set -euo pipefail

if [[ $# == 0 ]]; then
        echo "Usage: index.sh <input>"
        exit 1
fi

rm index_new.* || true

gdaltindex \
  -recursive \
  -lyr_name elevation \
  -gti_filename index_new.gti index_new.gti.gpkg \
  --optfile order.txt
