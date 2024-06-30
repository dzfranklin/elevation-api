#!/usr/bin/env bash
set -euo pipefail

# Optimize a single tif file

# For example to use on alos data run
# `find . -name '*_DSM.tif' | xargs -n 1 -P 8  ~/projects/elevation-api/tools/optimize.sh`
# and then `gdalbuildvrt aw3d30_gb.vrt optimized/**/*.tif`

if [[ $# == 0 ]]; then
        echo "Usage: optimize.sh orig.tiff"
        exit 1
fi

input=$1
name=$(basename "$input")
output="../optimized/$name"

scratch=$(mktemp -d)

gdal_calc.py --quiet -A "$input" --outfile="$scratch/rounded.tiff" --type=Int16 --calc='numpy.round(A)'

gdal_translate -q "$scratch/rounded.tiff" "$scratch/out.tiff" -co "TILED=YES" -co COMPRESS=ZSTD -co PREDICTOR=2 -co ZSTD_LEVEL=3

mkdir -p "$(dirname "$output")"
cp "$scratch/out.tiff" "$output"

rm -r "$scratch"
