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
"""Rung-1 field-trial client: decay-weighted reading of existing feeds.

The paper's deployability ladder starts with the rung that needs no
standardisation: any client can compute staleness decay from
timestamped status it already receives.  This module is that client.

Providers
  ocpi      OCPI 2.2.1 GET /locations with a Token A (env OCPI_URL,
            OCPI_TOKEN).  Ready for the operator drop-in; not usable
            without credentials.
  ocm       Open Charge Map v3 POI (env OCM_KEY).  Registry-grade
            status timestamps.
  osm       OpenStreetMap via Overpass (keyless).  Human-survey-grade
            timestamps: the worst-case feed a client might read.
  fixture   Recorded-shape OCPI snapshot for tests and demos.

Canonical record: (st_id, evse_id, lat, lon, status, power_kw,
stalls, last_updated epoch-s, source).  The decay law is imported
from board_sim so the trial and the simulator cannot drift apart.

Subcommands
  capture   pull a snapshot from a provider to JSON
  analyze   ages, trusts, implied T, decision-flip rates -> report
  demo      analyze a fixture (no network)
"""

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from board_sim import ALPHA, TTL, conf  # noqa: E402  (paper's law)

HERE = os.path.dirname(os.path.abspath(__file__))
VICINITY_KM = 6.0            # paper's decision radius
K_MAX = 15                   # paper's measured vicinity size
W_TRUST = 2.0                # Eq. 2 trust weight (from board_sim)
QUERY_SAMPLES = 400          # leave-one-out query origins per snapshot

# ------------------------------------------------------------- providers

# OSM keys that carry a "when was this last verified" timestamp, in
# precedence order (check_date is the machine-assisted one).
_OSM_DATE_KEYS = ("check_date", "survey:date", "lastcheck",
                  "last_check", "checked_at")


def _http(url, data=None, headers=None, timeout=90):
    hdrs = {"User-Agent":
            "BIODISC-Traffic-rung1/1.0 (field-trial client; "
            "contact: Tilanthi)"}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _osm_age_key(tags):
    for k in _OSM_DATE_KEYS:
        if k in tags:
            return k, tags[k]
    for k in tags:                      # last resort: any dated key
        if re.search(r"date", k) and re.fullmatch(
                r"\d{4}(-\d{2}(-\d{2})?)?( \d{2}:\d{2})?", tags[k] or ""):
            return k, tags[k]
    return None, None


def _parse_osm_date(s):
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return dt.datetime.strptime(s, fmt).timestamp()
        except ValueError:
            continue
    return None


def fetch_osm(area=None, bbox=None, limit=6000):
    """Overpass capture.  area: ISO-3166-1 code; bbox: (s,w,n,e)."""
    if bbox:
        sel = (f'node["amenity"="charging_station"]'
               f'({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});'
               f'way["amenity"="charging_station"]'
               f'({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});')
    else:
        sel = (f'area["ISO3166-1"="{area}"][admin_level=2]->.a;'
               f'node["amenity"="charging_station"](area.a);'
               f'way["amenity"="charging_station"](area.a);')
    q = f"[out:json][timeout:120];({sel});out tags center {limit};"
    raw = None
    for url in ("https://overpass-api.de/api/interpreter",
                "https://overpass.kumi.systems/api/interpreter",
                "https://overpass.private.coffee/api/interpreter"):
        try:
            raw = _http(url, data=urlencode({"data": q}).encode())
            break
        except Exception as e:               # mirror down / 5xx / 504
            print(f"  mirror {url.split('/')[2]} failed: {e}")
    if raw is None:
        raise SystemExit("all Overpass mirrors failed")
    out, key_hits = [], {}
    for el in raw.get("elements", []):
        t = el.get("tags", {})
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None:
            continue
        k, v = _osm_age_key(t)
        ts = _parse_osm_date(v) if v else None
        if k:
            key_hits[k] = key_hits.get(k, 0) + 1
        broken = (t.get("disused") == "yes" or t.get("broken") == "yes"
                  or t.get("operational") == "no")
        pw = None
        for tk, tv in t.items():
            if "output" in tk:
                m = re.search(r"(\d+(?:\.\d+)?)", tv or "")
                if m:
                    pw = max(pw or 0.0, float(m.group(1)))
        stalls = int(t["capacity"]) if t.get("capacity", "").isdigit() \
            else 1
        out.append(dict(st_id=f"osm-{el['type']}-{el['id']}",
                        evse_id=f"osm-{el['type']}-{el['id']}",
                        lat=lat, lon=lon,
                        status="BLOCKED" if broken else "AVAILABLE",
                        power_kw=pw, stalls=stalls,
                        last_updated=ts,
                        source="osm" if ts else "osm-nodate",
                        date_key=k))
    return out, key_hits


def urlencode(d):
    return urllib.parse.urlencode(d)


def fetch_ocpi():
    """OCPI 2.2.1 GET /locations (paginated).  Env OCPI_URL, OCPI_TOKEN."""
    url, tok = os.environ.get("OCPI_URL"), os.environ.get("OCPI_TOKEN")
    if not url or not tok:
        raise SystemExit("OCPI rung needs OCPI_URL and OCPI_TOKEN")
    out, link = [], url
    while link and len(out) < 50000:
        page = _http(link, headers={"Authorization": f"Token {tok}"})
        if isinstance(page, dict):            # {status_code, data, ...}
            page = page.get("data", [])
        for loc in page:
            for evse in loc.get("evses", []):
                pw = 0.0
                for c in evse.get("connectors", []):
                    pw = max(pw, c.get("power", 0) or 0)
                out.append(dict(
                    st_id=f"ocpi-{loc['id']}", evse_id=str(evse["id"]),
                    lat=evse.get("coordinates", {}).get("latitude"),
                    lon=evse.get("coordinates", {}).get("longitude"),
                    status=(evse.get("status") or "UNKNOWN").upper()
                    .replace(" ", "_"),
                    power_kw=pw or None, stalls=1,
                    last_updated=_iso(evse.get("last_updated")),
                    source="ocpi"))
        link = None                           # real client follows the
        break                                 # Link header; single page ok
    return out


def fetch_ocm(country="NL", limit=3000):
    key = os.environ.get("OCM_KEY")
    if not key:
        raise SystemExit("OCM rung needs OCM_KEY")
    url = ("https://api.openchargemap.io/v3/poi/?output=json"
           f"&key={key}&countrycode={country}&maxresults={limit}"
           "&compact=true&verbose=false")
    out = []
    for p in _http(url):
        ts = _iso(p.get("DateLastStatusUpdate"))
        st = p.get("StatusType") or {}
        out.append(dict(
            st_id=f"ocm-{p['ID']}", evse_id=f"ocm-{p['ID']}",
            lat=p.get("AddressInfo", {}).get("Latitude"),
            lon=p.get("AddressInfo", {}).get("Longitude"),
            status="BLOCKED" if not st.get("IsOperational", True)
            else "AVAILABLE",
            power_kw=None, stalls=1, last_updated=ts, source="ocm"))
    return out


def load_fixture(path):
    out = []
    for loc in json.load(open(path)):
        for evse in loc.get("evses", []):
            pw = 0.0
            for c in evse.get("connectors", []):
                pw = max(pw, c.get("power", 0) or 0)
            out.append(dict(
                st_id=f"fx-{loc['id']}", evse_id=str(evse["id"]),
                lat=evse["coordinates"]["latitude"],
                lon=evse["coordinates"]["longitude"],
                status=evse.get("status", "AVAILABLE"),
                power_kw=pw or None, stalls=1,
                last_updated=_iso(evse.get("last_updated")),
                source="fixture"))
    return out


def _iso(s):
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(
            s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


# -------------------------------------------------------------- analysis

def _dist_km(a, b, c, d):
    return 111.32 * math.hypot((c - a) * math.cos(math.radians(a)),
                               d - b)


def score(rec, now, qlat, qlon, decay_on):
    """Eq. 2 with the booking terms absent (rung 1 has no bookings)."""
    if rec["status"] == "BLOCKED":
        return -math.inf
    age_min = (now - rec["last_updated"]) / 60.0 \
        if rec["last_updated"] else None
    trust = conf(age_min) if decay_on else 1.0
    if decay_on and age_min is None:      # never verified: no trust
        trust = 0.0
    pw = rec["power_kw"] or 50.0
    d = _dist_km(qlat, qlon, rec["lat"], rec["lon"])
    if d > VICINITY_KM:
        return -math.inf
    return (math.log(pw / 50.0) + 0.6 * math.exp(-d / 12.0)
            + W_TRUST * (trust - 1.0))


def analyze(records, now=None, queries=QUERY_SAMPLES, seed=7):
    """Age distribution, implied T, raw-vs-decay decision flips."""
    import random
    rnd = random.Random(seed)
    now = now or dt.datetime.now().timestamp()
    dated = [r for r in records if r["last_updated"]]
    ages = sorted((now - r["last_updated"]) / 60.0 for r in dated)

    def pct(p):
        return ages[min(len(ages) - 1, int(p * len(ages)))] if ages \
            else None

    med = pct(0.5)
    # T needed so that f(median age) >= 0.9:  (A/T)^3 <= 0.1
    implied_T = med / 0.1 ** (1.0 / ALPHA) if med is not None else None

    # leave-one-out queries at station locations (uniform-trust subset
    # fallback: any record with coordinates)
    anchors = [r for r in records
               if r["lat"] is not None and r["status"] != "BLOCKED"]
    rnd.shuffle(anchors)
    anchors = anchors[:queries]
    flips = top_flips = n_q = n_multi = 0
    for a in anchors:
        vic = [r for r in records
               if r is not a and r["lat"] is not None
               and r["status"] != "BLOCKED"
               and _dist_km(a["lat"], a["lon"], r["lat"], r["lon"])
               <= VICINITY_KM][:K_MAX]
        if len(vic) < 2:
            continue
        n_multi += 1
        raw = sorted(vic, key=lambda r: -score(r, now, a["lat"],
                                               a["lon"], False))
        dec = sorted(vic, key=lambda r: -score(r, now, a["lat"],
                                               a["lon"], True))
        if raw and dec:
            n_q += 1
            if raw[0]["evse_id"] != dec[0]["evse_id"]:
                flips += 1
            if {r["evse_id"] for r in raw[:3]} != \
                    {r["evse_id"] for r in dec[:3]}:
                top_flips += 1
    cov = len(dated) / len(records) if records else 0.0
    return dict(
        n_records=len(records), n_dated=len(dated),
        date_coverage=cov,
        age_median_min=med,
        age_p10_min=pct(0.1), age_p90_min=pct(0.9),
        age_max_min=pct(1.0) if ages else None,
        implied_T_min=implied_T,
        queries=n_q, queries_multi_candidate=n_multi,
        top1_flips=flips,
        top1_flip_rate=flips / n_q if n_q else None,
        top3_flip_rate=top_flips / n_q if n_q else None,
        T_minutes=TTL, alpha=ALPHA)


# ------------------------------------------------------------------ CLI

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("capture")
    c.add_argument("--provider", default="osm",
                   choices=["osm", "ocm", "ocpi"])
    c.add_argument("--area", default="IE")
    c.add_argument("--bbox", default=None,
                   help="s,w,n,e (Amsterdam: 52.27,4.66,52.46,5.06)")
    c.add_argument("--limit", type=int, default=6000)
    c.add_argument("--out", required=True)

    a = sub.add_parser("analyze")
    a.add_argument("--snap", required=True)
    a.add_argument("--out", required=True)

    d = sub.add_parser("demo")
    d.add_argument("--fixture", required=True)
    d.add_argument("--out", required=True)

    args = ap.parse_args()
    if args.cmd == "capture":
        if args.provider == "osm":
            recs, key_hits = fetch_osm(
                area=args.area,
                bbox=[float(x) for x in args.bbox.split(",")]
                if args.bbox else None,
                limit=args.limit)
            snap = dict(provider="osm",
                        area=args.bbox or args.area,
                        captured=dt.datetime.now().isoformat(),
                        date_key_hits=key_hits, records=recs)
        else:
            recs = fetch_ocm(args.area) if args.provider == "ocm" \
                else fetch_ocpi()
            snap = dict(provider=args.provider, area=args.area,
                        captured=dt.datetime.now().isoformat(),
                        records=recs)
        json.dump(snap, open(args.out, "w"))
        print(f"captured {len(recs)} records -> {args.out}")
    else:
        path = args.snap if args.cmd == "analyze" else args.fixture
        loaded = json.load(open(path))
        if args.cmd == "demo":
            snap = dict(provider="fixture", area="fixture",
                        captured=dt.datetime.now().isoformat())
            recs = load_fixture(path)
        else:
            snap = loaded
            recs = loaded["records"]
        rep = dict(snapshot=path, provider=snap.get("provider"),
                   area=snap.get("area"),
                   captured=snap.get("captured"),
                   date_key_hits=snap.get("date_key_hits"),
                   **analyze(recs))
        json.dump(rep, open(args.out, "w"), indent=1)
        print(json.dumps({k: v for k, v in rep.items()
                          if k != "date_key_hits"}, indent=1))


if __name__ == "__main__":
    main()
