#!/usr/bin/env python3
# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generate an OCPI-2.2.1-shaped fixture with controlled report ages.

Used to exercise the rung-1 client end-to-end without network: ages
span fresh (2 min) to stale (88 min) so the decay law has
heterogeneous trust to work on and decision flips must occur.  The
geometry is a 4x6 grid around a city centre, 2 EVSEs per location.
"""

import argparse
import datetime as dt
import json

AGES_MIN = [2, 4, 6, 8, 10, 14, 18, 22, 26, 31, 36, 42, 55, 70, 88]
POWERS = [50, 150, 350]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lat", type=float, default=53.35)
    ap.add_argument("--lon", type=float, default=-6.26)
    args = ap.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    locs = []
    i = 0
    for r in range(4):
        for c in range(6):
            age = AGES_MIN[(r * 6 + c) % len(AGES_MIN)]
            pw = POWERS[(r + c) % 3]
            lat = args.lat + 0.02 * r
            lon = args.lon + 0.03 * c
            ts = (now - dt.timedelta(minutes=age)).isoformat()
            locs.append(dict(
                id=f"FX{i:03d}",
                name=f"fixture {i}",
                coordinates=dict(latitude=lat, longitude=lon),
                evses=[dict(
                    id=f"FX{i:03d}-A", status="AVAILABLE",
                    last_updated=ts,
                    coordinates=dict(latitude=lat, longitude=lon),
                    connectors=[dict(id="1", standard="IEC_62196_T2",
                                     power=pw)]),
                    dict(
                    id=f"FX{i:03d}-B", status="AVAILABLE",
                    last_updated=ts,
                    coordinates=dict(latitude=lat, longitude=lon),
                    connectors=[dict(id="1", standard="CHADEMO",
                                     power=max(50, pw // 2))])]))
            i += 1
    json.dump(locs, open(args.out, "w"), indent=1)
    print(f"wrote {args.out}: {len(locs)} locations, "
          f"ages {min(AGES_MIN)}-{max(AGES_MIN)} min")


if __name__ == "__main__":
    main()
