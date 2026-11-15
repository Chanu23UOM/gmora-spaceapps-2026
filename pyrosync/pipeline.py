"""Country analysis and counterfactual instrument-availability experiments."""
from collections import Counter, defaultdict
from datetime import date, timedelta
from statistics import median

import h3

from .data import SOURCES


def occupancy(records, resolution=8, quality=True, excluded=()):
    return {(r.day, r.cell if resolution == 8 else h3.latlng_to_cell(r.lat, r.lon, resolution))
            for r in records if r.kind == 0 and (r.quality or not quality) and r.source not in excluded}


def analyze(records, country, year=2025, source_manifest=None, include_map=True, diagnostics=True):
    first = date(year, 1, 1)
    days = [(first+timedelta(days=i)).isoformat() for i in range((date(year+1,1,1)-first).days)]
    daily = {d: {"date": d, "raw": 0, "vegetation_raw": 0, "filtered_raw": 0,
                 "industrial_raw": 0, "active_cells": 0, "viirs_active_cells":0, "multi_sensor_cells": 0,
                 "by_source": {s: 0 for s in SOURCES},
                 "source_cells": {s: 0 for s in SOURCES}} for d in days}
    cell_sensors, source_sets = defaultdict(set), {s: set() for s in SOURCES}
    monthly = defaultdict(lambda: {"raw": 0, "cells": set(), "sensors": Counter(), "samples": []})
    quality_rows, types = 0, Counter()
    for r in records:
        item = daily[r.day]
        item["raw"] += 1
        types[str(r.kind)] += 1
        item["vegetation_raw"] += r.kind == 0
        item["industrial_raw"] += r.kind == 2
        if r.kind == 0 and r.quality:
            quality_rows += 1
            item["filtered_raw"] += 1
            item["by_source"][r.source] += 1
            cell_sensors[(r.day, r.cell)].add(r.source)
            source_sets[r.source].add((r.day, r.cell))
        if r.kind not in (0, 2) or not r.quality:
            continue
        if not include_map:
            continue
        parent = h3.cell_to_parent(r.cell, 7)
        bucket = monthly[(r.day[:7], parent, r.kind)]
        bucket["raw"] += 1
        bucket["cells"].add((r.day, r.cell))
        bucket["sensors"][r.source] += 1
        if len(bucket["samples"]) < 3:
            bucket["samples"].append({"source": r.source, "row": r.row, "utc": r.utc,
                                      "frp_mw": r.frp_mw, "footprint_km2": round(r.footprint_km2, 4)})
    for (day, _), sensors in cell_sensors.items():
        daily[day]["active_cells"] += 1
        daily[day]["multi_sensor_cells"] += len(sensors) > 1
        daily[day]['viirs_active_cells'] += any(s != 'modis' for s in sensors)
    for source, cells in source_sets.items():
        for day, _ in cells:
            daily[day]["source_cells"][source] += 1
    map_cells = []
    for (month, cell, kind), bucket in sorted(monthly.items()):
        lat, lon = h3.cell_to_latlng(cell)
        map_cells.append({"month": month, "h3": cell, "lat": round(lat, 5), "lon": round(lon, 5),
                          "type": kind, "raw": bucket["raw"], "cell_days": len(bucket["cells"]),
                          "sensors": dict(sorted(bucket["sensors"].items())), "samples": bucket["samples"]})
    union = set(cell_sensors)
    dropouts = []
    for source in SOURCES:
        remaining = set().union(*(s for k,s in source_sets.items() if k != source))
        lost = len(union - remaining)
        dropouts.append({"removed": source, "lost_cell_days": lost,
                         "retained_fraction": len(remaining)/len(union) if union else 1})
    modis = source_sets["modis"]
    viirs = source_sets["viirs-snpp"] | source_sets["viirs-jpss1"]
    sensitivity = [{"resolution": res, "quality": quality,
                    "active_cell_days": len(occupancy(records, res, quality))}
                   for res in (7, 8, 9) for quality in (True, False)] if diagnostics else []
    summary = {"raw_rows": len(records), "type_counts": dict(sorted(types.items())),
               "filtered_vegetation_rows": quality_rows, "active_cell_days": len(union),
               "multi_sensor_cell_days": sum(len(s) > 1 for s in cell_sensors.values()),
               "modis_viirs_jaccard": len(modis & viirs)/len(union) if union else None,
               "median_footprint_km2": {s: median(values) if (values := [r.footprint_km2 for r in records if r.source == s]) else None
                                         for s in SOURCES},
               "observation_reduction_fraction": 1-len(union)/quality_rows if quality_rows else 0}
    source_status = {item['source']:item['file_status'] for item in source_manifest} if source_manifest is not None else {s:'present' for s in SOURCES}
    complete = all(source_status.get(s) == 'present' for s in SOURCES)
    for item in daily.values():
        item['observation_coverage'] = 'unknown'
        item['complete_source_inputs'] = complete
        item['observed_active_cells'] = item['active_cells']
        item['activity_status'] = ('qualifying_detections' if item['active_cells'] else
                                   'no_recorded_qualifying_detections' if complete else 'unknown_missing_input')
        if not complete:
            item['active_cells'] = None
    historical = source_manifest is not None or year != 2025
    if not historical:
        for item in daily.values():
            for key in ('viirs_active_cells','observation_coverage','complete_source_inputs','observed_active_cells','activity_status'):
                item.pop(key,None)
    return {"country": country, "year": year,
            **({'source_status':source_status,'observation_coverage':'unknown'} if historical else {}),
            "summary": summary, "daily": list(daily.values()),
            "map_cells": map_cells, "sensor_dropout": dropouts, "sensitivity": sensitivity,
            "limitations": ["Active cell-days are observations, not distinct fires or burned area.",
                            "No cloud or observation-coverage masks: zero means no qualifying detections in these files.",
                            "UTC days may split a local fire episode; H3 boundaries may split nearby observations.",
                            "Source-type 0 includes agricultural burning; no wildfire attribution is inferred.",
                            "One year cannot establish climate anomalies, multi-decade trends or sensor inter-calibration."]}
