import os
import random

import dotenv

from dataset import Dataset

SIZE = 1000
COUNT = 10


def main():
    dotenv.load_dotenv(".env")
    src_path = os.path.expanduser(os.getenv("DEM_SOURCE"))
    ds = Dataset(src_path)

    for _ in range(0, COUNT):
        points: list[(float, float)] = []
        for _ in range(0, SIZE):
            lng = random.uniform(-180, 180)
            lat = random.randrange(-90, 90)
            points.append((lng, lat))

        res = ds.lookup(points)
        assert len(res) == len(points)


if __name__ == "__main__":
    main()
