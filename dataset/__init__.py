import logging

import numpy as np
import rasterio

from dataset.source import Source

user_agent = "github.com/dzfranklin/elevation-api"


class Dataset:
    sources: list[Source] = []
    nodata_attribution: str
    l = logging.getLogger("Dataset")

    def __init__(self, sources: list[Source]):
        if len(sources) == 0:
            raise ValueError("No sources provided")

        self.sources = sources
        self.nodata_attribution = sources[-1].id

    def lookup(self, lnglats: list[(float, float)]) -> tuple[list[float], set[str]]:
        out: list[float] = []
        attribs = set[str]()
        for lng, lat in lnglats:
            value, attrib = self._lookup_one(lng, lat)
            out.append(value)
            attribs.add(attrib)
        return out, attribs

    def _lookup_one(self, lng: float, lat: float) -> (float, str):
        for src in self.sources:
            bands: np.ndarray[np.float16]
            try:
                with rasterio.Env(
                        GDAL_HTTP_USERAGENT=user_agent,
                        GDAL_HTTP_TCP_KEEPALIVE=True,
                        GDAL_HTTP_MAX_RETRY=0,
                        GDAL_HTTP_CONNECTTIMEOUT=2,
                        GDAL_HTTP_TIMEOUT=4,
                ):
                    query = src.ds.sample([(lng, lat)])
                    bands: np.ndarray[np.float16] = next(query)
            except rasterio.RasterioIOError as err:
                self.l.error(err)
                continue

            value = bands[0]
            if value != src.ds.nodata:
                scaled_value = float(value) * src.scale_factor
                rounded_value = round(scaled_value, 1)
                return rounded_value, src.id
        return 0.0, self.nodata_attribution
