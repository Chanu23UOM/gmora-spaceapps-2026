"""python -m pyrosync build | brief COUNTRY | verify COUNTRY CLAIMS.json"""
import argparse
import csv
import hashlib
import io
import json
import platform
from pathlib import Path

import h3
import numpy as np

from .data import COUNTRIES, load_country
from .evidence import evidence_packet, render_brief, verify_claims
from .forecast import benchmark
from .pipeline import analyze

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":"), sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def build(root=ROOT):
    evaluation_summary = {}
    manifest = {"schema_version": 1, "dataset_year": 2025, "countries": [], "inputs": [],
                "method": {"grid": "H3", "resolution": 8, "day": "UTC",
                           "quality": "MODIS confidence >=30; VIIRS nominal/high; type=0",
                           "deduplication_unit": "unique (H3 cell, UTC date), across all instruments",
                           "map_aggregation": "resolution-8 cell-days grouped into resolution-7 parents"},
                "runtime": {"python": platform.python_version(), "numpy": np.__version__, "h3": h3.__version__}}
    code = hashlib.sha256()
    for source in sorted((root/"pyrosync").glob("*.py")):
        code.update(source.name.encode())
        code.update(source.read_bytes())
    manifest["pipeline_sha256"] = code.hexdigest()
    for country in COUNTRIES:
        print(f"Analyzing {country}…", flush=True)
        records, inputs = load_country(root, country)
        payload = analyze(records, country)
        payload["benchmark"] = benchmark([d["active_cells"] for d in payload["daily"]])
        map_cells = payload.pop("map_cells")
        payload["map_months"] = {}
        for month in range(1, 13):
            key = f"2025-{month:02d}"
            map_path = root/"web_app"/"data"/f"{country}_{key}_map.json"
            write_json(map_path, [c for c in map_cells if c["month"] == key])
            payload["map_months"][key] = {"path": f"data/{map_path.name}",
                                           "sha256": hashlib.sha256(map_path.read_bytes()).hexdigest()}
        packet = evidence_packet(payload)
        evaluation_summary[country] = {"summary": payload["summary"],
                                       "sensor_dropout": payload["sensor_dropout"],
                                       "sensitivity": payload["sensitivity"],
                                       "benchmark": {k:v for k,v in payload["benchmark"].items()
                                                     if k not in ("predictions", "forecast")}}
        output = root/"web_app"/"data"/f"{country}.json"
        write_json(output, payload)
        write_json(root/"processed_data"/f"{country}_evidence.json", packet)
        write_json(root/"web_app"/"data"/f"{country}_evidence.json", packet)
        brief = render_brief(payload, packet)
        (root/"processed_data"/f"{country}_brief.md").write_text(brief)
        (root/"web_app"/"data"/f"{country}_brief.md").write_text(brief)
        csv_stream = io.StringIO()
        columns = ["date", "raw", "vegetation_raw", "filtered_raw", "active_cells", "multi_sensor_cells", "industrial_raw"]
        writer = csv.DictWriter(csv_stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(payload["daily"])
        (root/"web_app"/"data"/f"{country}_daily.csv").write_text(csv_stream.getvalue())
        manifest["inputs"].extend(inputs)
        manifest["countries"].append({"id": country, "label": country.replace("_", " "),
                                      "path": f"data/{country}.json",
                                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()})
        print(f"  {payload['summary']['active_cell_days']:,} cell-days; selected {payload['benchmark']['selected_model']}; "
              f"promotion={payload['benchmark']['promotion_passed']}", flush=True)
    manifest["run_id"] = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:16]
    write_json(root/"web_app"/"data"/"manifest.json", manifest)
    write_json(root/"processed_data"/"evaluation_summary.json", evaluation_summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    miro = sub.add_parser('mirofish',help='Local MiroFish communication tabletop')
    commands = miro.add_subparsers(dest='operation',required=True)
    commands.add_parser('doctor')
    prepare = commands.add_parser('prepare')
    prepare.add_argument('country',choices=COUNTRIES)
    prepare.add_argument('--month',required=True)
    prepare.add_argument('--policy',choices=('independent','coordinated'),default='coordinated')
    prepare.add_argument('--reviewers',type=int,default=4)
    prepare.add_argument('--reviews-per-day',type=int,default=20)
    prepare.add_argument('--max-rounds',type=int,default=4)
    prepare.add_argument('--replicate',type=int,default=0)
    for name in ('status','advance'):
        p = commands.add_parser(name)
        p.add_argument('run_id')
    for command in ("brief", "verify"):
        p = sub.add_parser(command)
        p.add_argument("country", choices=COUNTRIES)
        if command == "verify":
            p.add_argument("claims", type=Path)
    args = parser.parse_args()
    if args.command == 'mirofish':
        from .mirofish import ScenarioStore, doctor
        store = ScenarioStore()
        if args.operation == 'doctor':
            result = doctor()
        elif args.operation == 'prepare':
            result = store.prepare(args.country,args.month,args.policy,args.reviewers,args.reviews_per_day,args.max_rounds,args.replicate)
        elif args.operation == 'advance':
            result = store.advance(args.run_id)
        else:
            result = store.get(args.run_id)
        print(json.dumps(result,indent=2))
    elif args.command == "build":
        build()
    else:
        payload = json.loads((ROOT/"web_app"/"data"/f"{args.country}.json").read_text())
        if args.command == "brief":
            print(render_brief(payload, evidence_packet(payload)))
        else:
            verify_claims(payload, json.loads(args.claims.read_text()))
            print("Claims match allowlisted evidence.")


if __name__ == "__main__":
    main()
