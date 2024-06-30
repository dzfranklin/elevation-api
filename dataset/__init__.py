import logging
from typing import Generator

import numpy as np
import prometheus_client as prom
import rasterio

from dataset.source import Source

LOOKUP_TIME = prom.Summary("lookup_secs", "Time spent looking up points in seconds")


class Dataset:
    r: rasterio.DatasetReader
    l = logging.getLogger("Dataset")

    def __init__(self, path: str):
        self.r = rasterio.open(path)

    @LOOKUP_TIME.time()
    def lookup(self, lnglats: list[(float, float)]) -> list[int]:
        samples: Generator[np.ma.masked_array[np.float16], None, None] = self.r.sample(lnglats, masked=True)
        out: list[int] = []
        for bands in samples:
            value = bands[0]
            mask = bands.mask[0]
            if mask:
                out.append(0)
            else:
                out.append(int(np.round(value)))
        return out
