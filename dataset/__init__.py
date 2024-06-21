import rasterio

from dataset.lookup import lookup


class Dataset:

    merit: rasterio.DatasetReader

    def __init__(self, merit_dem_fixed1: str):
        """Dataset for elevation lookups.

        Args:
            merit_dem_fixed1 (str): Path to vrt file of MERIT DEM tiles converted per tools/convert.sh
        """

        self.merit = rasterio.open(merit_dem_fixed1)

    def lookup(self, lnglats: list[(float, float)]) -> list[float | None]:
        return lookup(self.merit, lnglats)
