"""Reproducible acquisition from NASA's public yearly country catalog."""
import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .data import SOURCES, COUNTRIES, load_country
from .pipeline import analyze
from .mirofish import ROOT, save

BASE='https://firms.modaps.eosdis.nasa.gov/data/country/'


def acquire(root=ROOT, years=range(2020,2025)):
    directory=root/'.integrations/firms-history'
    directory.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(BASE+'yearly_summary_files.txt',timeout=60) as r:
        catalog=r.read()
    (directory/'catalog.csv').write_bytes(catalog)
    entries={r['filename']:r for r in csv.DictReader(io.StringIO(catalog.decode()))}
    fetched=datetime.now(timezone.utc).isoformat()
    def fetch(case):
        source,year,country=case
        name=f'{source}_{year}_{country}.csv'
        relative=f'{source}/{year}/{name}'
        metadata={'source':source,'year':year,'country':country,'url':BASE+relative,
                  'path':relative,'fetched_at':fetched,'observation_coverage':'unknown'}
        if name not in entries:
            return {**metadata,'file_status':'not_in_catalog','sensor_availability':'not_listed_in_official_catalog'}
        entry=entries[name];path=directory/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        expected=int(entry['size'])
        if not path.exists() or path.stat().st_size!=expected:
            with urllib.request.urlopen(BASE+relative,timeout=120) as r:
                content=r.read()
            if len(content)!=expected or not content.startswith(b'latitude,longitude,'):
                raise ValueError(f'Invalid archive payload or catalog size: {name}')
            temp=path.with_suffix('.part');temp.write_bytes(content);temp.replace(path)
        content=path.read_bytes()
        versions=set();dates=[];count=0
        for row in csv.DictReader(io.StringIO(content.decode())):
            count+=1;versions.add(row['version']);dates.append(row['acq_date'])
        print(f'{country} {source} {year}: {count:,} rows',flush=True)
        return {**metadata,'file_status':'present','sensor_availability':'archive_file_present',
                'catalog_updated':entry['updated'],'bytes':expected,'rows':count,
                'date_range':[min(dates),max(dates)] if dates else None,
                'product_versions':sorted(versions),'sha256':hashlib.sha256(content).hexdigest()}
    cases=[(s,y,c) for y in years for c in COUNTRIES for s in SOURCES]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        files=list(pool.map(fetch,cases))
    manifest={'schema_version':1,'catalog_url':BASE+'yearly_summary_files.txt',
              'catalog_sha256':hashlib.sha256(catalog).hexdigest(),'fetched_at':fetched,'files':files,
              'coverage_note':'Positive detection archives do not contain non-fire, cloud or observation-opportunity masks.',
              'coverage_reference':'https://firms.modaps.eosdis.nasa.gov/api/data_availability/'}
    save(root/'processed_data/history_manifest.json',manifest)
    return manifest


def build(root=ROOT):
    manifest=json.loads((root/'processed_data/history_manifest.json').read_text())
    directory=root/'.integrations/firms-history'
    for country in COUNTRIES:
        series=[];year_summaries=[]
        for year in sorted({f['year'] for f in manifest['files']}):
            files=[f for f in manifest['files'] if f['country']==country and f['year']==year]
            for entry in files:
                if entry['file_status']=='present':
                    path=directory/entry['path']
                    if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
                        raise ValueError(f'History input hash mismatch: {path.name}')
            records,inputs=load_country(directory,country,year,allow_missing=True,invalid_rows='quarantine')
            by_source={f['source']:f for f in files}
            for item in inputs:
                if item['source'] in by_source and by_source[item['source']]['file_status']=='not_in_catalog':
                    item['file_status']='not_in_catalog';item['sensor_availability']='not_listed_in_official_catalog'
            payload=analyze(records,country,year,inputs,include_map=False,diagnostics=False)
            series.extend(payload['daily'])
            year_summaries.append({'year':year,'summary':payload['summary'],'inputs':inputs})
            print(f'{country} {year}: {payload["summary"]["active_cell_days"]:,} cell-days',flush=True)
        save(root/'processed_data'/f'{country}_history.json',{'country':country,'daily':series,'years':year_summaries,
             'coverage':'unknown','input_manifest_sha256':hashlib.sha256((root/'processed_data/history_manifest.json').read_bytes()).hexdigest()})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['acquire','build'])
    args=parser.parse_args()
    acquire() if args.command=='acquire' else build()


if __name__=='__main__':main()
