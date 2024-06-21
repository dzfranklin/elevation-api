import rasterio


def lookup(ds: rasterio.DatasetReader, lnglats: list[(float, float)]) -> list[float | None]:
    out: list[float | None] = []
    for n in ds.sample([(lng, lat) for lng, lat in lnglats]):
        if n == ds.nodata:
            out.append(None)
        else:
            out.append(n/10)
    return out
