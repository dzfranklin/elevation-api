#!/usr/bin/env bash
set -euo pipefail

if [[ $# == 0 ]]; then
        echo "Usage: convert.sh orig.tif"
        exit 1
fi

input=$1
input_fname_with_ext=$(basename "$input")
input_fname_no_ext="${input_fname_with_ext%.*}"
input_ext="${input_fname_with_ext##*.}"

if [[ "$input_ext" != tif ]]; then
        echo "Expected a .tif file"
        exit 1
fi

scratch=$(mktemp -d)

echo "Rounding"
gdal_calc.py -A "$input" --outfile="$scratch/rounded.tif" --type=Int16 --calc='numpy.round(10.0*A)'

echo "Compressing"
gdal_translate "$scratch/rounded.tif" "$scratch/out.tif" -co "TILED=YES" -co COMPRESS=ZSTD -co PREDICTOR=2 -co ZSTD_LEVEL=3

output="$input_fname_no_ext"_fixed1.tif
cp "$scratch/out.tif" "$output"
echo "Wrote $output"

rm -r "$scratch"
