#!/usr/bin/env bash
set -euo pipefail

# See <https://medium.com/@robsimmon/a-gentle-introduction-to-gdal-part-5-shaded-relief-ec29601db654>

gdalwarp ../aw3d30/aw3d30.vrt -crop_to_cutline \
        -cutline yose.geojson \
        -overwrite yose_dem.tif \
        -ts 5000 0 -r bilinear \
        -wo OPTIMIZE_SIZE=yes

gdaldem hillshade yose_dem.tif yose_hillshade.png -alpha

gdaldem color-relief yose_dem.tif colors.txt yose_color.png -alpha

gdaldem aspect yose_dem.tif yose_aspect.tif
gdaldem color-relief yose_aspect.tif aspect_colors.txt yose_aspect.png -alpha

convert yose_hillshade.png yose_color.png yose_aspect.png -compose blend -composite yose_.png
convert -bordercolor transparent -border 150 yose_.png yose_.png
pngcrush yose_.png yose.png
