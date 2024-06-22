import rasterio


class Source:
    id: str
    path: str
    scale_factor: float
    ds: rasterio.DatasetReader

    def __init__(self, id_: str, path: str, scale_factor: float = 1.0):
        self.id = id_
        self.path = path
        self.scale_factor = scale_factor

        self.ds = rasterio.open(path)
