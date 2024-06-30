#!/usr/bin/env python3

import argparse
import time
from dataclasses import dataclass

import requests

parser = argparse.ArgumentParser()
parser.add_argument("--endpoint")
args = parser.parse_args()

endpoint = "https://elevation.dfranklin.dev"
if args.endpoint:
    endpoint = args.endpoint
print(f"Using endpoint: {endpoint}")


@dataclass
class Case:
    name: str
    point: tuple[float, float]
    expected: float

    failed = False


cases = [
    Case("GB (Cairn Gorm)", (-3.643455, 57.116658), 1244),
    Case("CONUS (Lake Granby)", (-105.85858, 40.160080), 2518),
    Case("Kathmandu", (85.3240, 27.7172), 1301),
    Case("Everest Summit", (86.925145, 27.988257), 8724),  # significantly below correct elevation
]

start = time.time()
for case in cases:
    response = requests.get(
        f"{endpoint}/api/v1/elevation",
        params={"lng": case.point[0], "lat": case.point[1]},
    )
    response.raise_for_status()
    data = response.json()

    got = data["elevation"][0]
    if got != case.expected:
        case.failed = True
        print(f"FAIL: {case.name}: expected {case.expected}, got {got}")

    if not case.failed:
        print(f"OK: {case.name}")
elapsed = time.time() - start

failed = [case for case in cases if case.failed]
if failed:
    print(f"{len(failed)} cases failed: {', '.join([case.name for case in failed])}")
    exit(1)
else:
    print(f"All cases passed in {elapsed} seconds!")
    exit(0)
