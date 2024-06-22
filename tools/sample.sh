#!/usr/bin/env bash
set -euo pipefail

# This is used for generated the files in test_samples

input=$1
if [ -z "$input" ]; then
  echo "Usage: $0 <input>"
  exit 1
fi

input_fname=$(basename "$input")

output="${input_fname%.*}_sample.tif"
output_width=100

gdalwarp -overwrite --config GDAL_CACHEMAX 1000 -ts "$output_width" 0 "$input" "$output"
