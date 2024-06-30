dev *args:
  poetry run fastapi dev main.py {{args}}

dev-full *args:
   DEM_SOURCE=~/elevation_data/index.gti.gpkg \
   just dev {{args}}

smoke endpoint:
  poetry run ./tools/smoke.py --endpoint {{endpoint}}
  poetry run ./tools/smoke_large.py --endpoint {{endpoint}}
