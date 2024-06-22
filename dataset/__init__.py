import numpy as np
import rasterio as rio


class Dataset:
    sources: list[tuple[str, rio.DatasetReader]] = []
    nodata_attribution: str
    base_attribution: list[str]

    def __init__(self, sources: list[tuple[str, str]], base_attribution: list[str]):
        if len(sources) == 0:
            raise ValueError("No sources provided")

        self.base_attribution = base_attribution
        self.nodata_attribution = sources[-1][0]

        for name, path in sources:
            ds = rio.open(path)
            self.sources.append((name, ds))

    def lookup(self, lnglats: list[(float, float)]) -> tuple[list[float], set[str]]:
        out: list[float] = []
        attribs = set(self.base_attribution)
        for lng, lat in lnglats:
            value, attrib = self._lookup_one(lng, lat)
            out.append(value)
            attribs.add(attrib)
        return out, attribs

    def _lookup_one(self, lng: float, lat: float) -> (float, str):
        for name, ds in self.sources:
            query = ds.sample([(lng, lat)])
            bands: np.ndarray[np.float16] = next(query)
            value = bands[0]
            if value != ds.nodata:
                return float(value / 10.0), name
        return 0.0, self.nodata_attribution
