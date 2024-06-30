#!/usr/bin/env python3

import argparse
import time

import requests

parser = argparse.ArgumentParser()
parser.add_argument("--endpoint")
parser.add_argument("-n", type=int, default=100)
args = parser.parse_args()

endpoint = "https://elevation.dfranklin.dev"
if args.endpoint:
    endpoint = args.endpoint
print(f"Using endpoint: {endpoint}")

lat = 0
start_lng = 50
end_lng = 150

points = []
for i in range(args.n):
    p = (start_lng + (end_lng - start_lng) * i / args.n, lat)
    points.append(p)

start = time.time()
response = requests.post(
    f"{endpoint}/api/v1/elevation",
    json={"coordinates": points},
)
elapsed = time.time() - start
response.raise_for_status()

assert len(response.json()["elevation"]) == args.n
print(f"OK: {args.n} points")

print(f"Passed in {elapsed:.2f} seconds!")
