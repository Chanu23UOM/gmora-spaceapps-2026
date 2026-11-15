"""Read immutable FIRMS inputs and preserve source-row provenance."""
from __future__ import annotations

import csv
import hashlib
import math
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import h3

SOURCES = ("modis", "viirs-snpp", "viirs-jpss1")
COUNTRIES = ("Sri_Lanka", "Argentina")


@dataclass(frozen=True, slots=True)
class Detection:
    lat: float
    lon: float
    day: str
    utc: str
    source: str
    satellite: str
    kind: int
    quality: bool
    frp_mw: float
    footprint_km2: float
    cell: str
    row: int


def parse_row(row: dict, source: str, line: int, resolution: int = 8) -> Detection:
    lat, lon = float(row["latitude"]), float(row["longitude"])
    scan, track, frp = (float(row[k]) for k in ("scan", "track", "frp"))
    if not all(math.isfinite(x) for x in (lat, lon, scan, track, frp)):
        raise ValueError("non-finite numeric field")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180 and scan > 0 and track > 0 and frp >= 0):
        raise ValueError("coordinate, footprint or FRP out of range")
    day = date.fromisoformat(row["acq_date"])
    hhmm = row["acq_time"].zfill(4)
    if len(hhmm) != 4 or not hhmm.isdigit():
        raise ValueError("invalid acquisition time")
    timestamp = datetime(day.year, day.month, day.day, int(hhmm[:2]), int(hhmm[2:]), tzinfo=timezone.utc)
    if source == "modis":
        confidence = float(row["confidence"])
        if not math.isfinite(confidence) or not 0 <= confidence <= 100:
            raise ValueError("invalid MODIS confidence")
        quality = confidence >= 30
    else:
        if row["confidence"] not in ("l", "n", "h"):
            raise ValueError("invalid VIIRS confidence")
        quality = row["confidence"] in ("n", "h")
    kind = int(row["type"])
    if kind not in range(4) or row["daynight"] not in ("D", "N"):
        raise ValueError("invalid source type or daynight")
    return Detection(lat, lon, day.isoformat(), timestamp.isoformat(), source,
                     row["satellite"], kind, quality, frp, scan * track,
                     h3.latlng_to_cell(lat, lon, resolution), line)


def load_country(root: Path, country: str, year: int = 2025, allow_missing=False, invalid_rows='raise'):
    if invalid_rows not in ('raise','quarantine'):
        raise ValueError('unknown invalid-row policy')
    records, manifest = [], []
    for source in SOURCES:
        relative = f"{source}/{year}/{source}_{year}_{country}.csv"
        path = root / relative
        if not path.exists() and allow_missing:
            manifest.append({'path':relative,'source':source,'year':year,'country':country,
                             'file_status':'missing','sensor_availability':'unknown',
                             'observation_coverage':'unknown','rows':None})
            continue
        rows = 0
        seen = set()
        duplicates = 0
        quarantined=[]
        with path.open(newline="") as stream:
            for line, row in enumerate(csv.DictReader(stream), 2):
                rows += 1
                try:
                    record = parse_row(row, source, line)
                    if not record.day.startswith(str(year) + "-"):
                        raise ValueError("record outside requested year")
                except (ValueError, KeyError, TypeError) as exc:
                    if invalid_rows=='quarantine':
                        quarantined.append({'line':line,'reason':str(exc)})
                        continue
                    raise ValueError(f"{relative}:{line}: {exc}") from exc
                key = tuple(row.values())
                duplicates += key in seen
                seen.add(key)
                records.append(record)
        manifest.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "rows": rows, "exact_duplicate_rows": duplicates,'source':source,
                         'year':year,'country':country,'file_status':'present',
                         'accepted_rows':rows-len(quarantined),'quarantined_rows':quarantined,
                         'sensor_availability':'archive_file_present','observation_coverage':'unknown'})
    return records, manifest
