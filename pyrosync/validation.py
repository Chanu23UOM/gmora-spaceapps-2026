"""Exploratory audit of the frozen sensor mappings; not operational validation.

Uses the already-seen 2023/2024 test years without choosing a new mapping.
A simulated sensor switch measures error relative to the same VIIRS reference.
It does not identify real sensor retirements or validate a climate trend.
"""
import hashlib
import json
from datetime import date, timedelta

import numpy as np

from .forecast import metrics
from .mirofish import ROOT, save
from .research import mapping


def transition_audit(days, prediction):
    """At each month boundary, switch from MODIS-derived values to VIIRS.

    Compare the 7-day-before/after jump to an all-VIIRS series on the same dates.
    The post-switch error is zero by construction; report this limitation.
    """
    dates = [date.fromisoformat(d['date']) for d in days]
    reference = np.array([d['viirs_active_cells'] for d in days], dtype=float)
    prediction = np.asarray(prediction, dtype=float)
    if len(prediction) != len(days):
        raise ValueError('Prediction and daily series lengths differ')
    rows = []
    for i, day in enumerate(dates):
        if day.day != 1 or i < 7 or i + 7 > len(days):
            continue
        window = dates[i - 7:i + 7]
        if any(b - a != timedelta(days=1) for a, b in zip(window, window[1:])):
            raise ValueError('A transition window has missing calendar dates')
        reference_jump = reference[i:i + 7].mean() - reference[i - 7:i].mean()
        switched_jump = reference[i:i + 7].mean() - prediction[i - 7:i].mean()
        rows.append({'boundary':day.isoformat(), 'reference_relative_jump':float(switched_jump - reference_jump)})
    return {'simulated_boundaries':len(rows),
            'mean_absolute_reference_relative_jump':float(np.mean([abs(r['reference_relative_jump']) for r in rows])) if rows else None,
            'boundaries':rows}


def audit_country(payload, plan):
    daily = payload['daily']
    if any(not d['complete_source_inputs'] for d in daily):
        raise ValueError('Missing source inputs cannot be treated as zero')
    if [d['date'] for d in daily] != sorted({d['date'] for d in daily}):
        raise ValueError('Daily dates must be unique and ordered')
    outputs = []
    for fold in plan['outer_folds']:
        train = [d for d in daily if int(d['date'][:4]) in fold['selection_years']]
        calibration = [d for d in daily if int(d['date'][:4]) == fold['calibration_year']]
        test = [d for d in daily if int(d['date'][:4]) == fold['test_year']]
        if not train or not calibration or not test:
            raise ValueError('Incomplete historical fold')
        if max(d['date'] for d in train) >= min(d['date'] for d in calibration) or max(d['date'] for d in calibration) >= min(d['date'] for d in test):
            raise ValueError('Selection, calibration and test must be in time order')
        chosen = min(plan['calibration_candidates'], key=lambda m:metrics(
            [d['viirs_active_cells'] for d in calibration], mapping(train,calibration,m))['mae'])
        actual = np.array([d['viirs_active_cells'] for d in test],dtype=float)
        raw = np.array(mapping(train,test,'identity'))
        selected = np.array(mapping(train,test,chosen))
        raw_mae = metrics(actual,raw)['mae']; selected_mae = metrics(actual,selected)['mae']
        zero = np.array([d['source_cells']['modis'] == 0 for d in test])
        outputs.append({**fold, 'selected_mapping':chosen, 'test_days':len(test),
                        'identity_MAE':raw_mae, 'selected_MAE':selected_mae,
                        'MAE_reduction_vs_identity':1-selected_mae/raw_mae if raw_mae else None,
                        'identity_transition':transition_audit(test,raw),
                        'selected_transition':transition_audit(test,selected),
                        'zero_MODIS_days':int(zero.sum()),
                        'zero_MODIS_but_positive_VIIRS_days':int((zero & (actual>0)).sum()),
                        'selected_MAE_on_zero_MODIS_days':metrics(actual[zero],selected[zero])['mae'] if zero.any() else None})
    return {'country':payload['country'], 'outer_folds':outputs}


def main():
    path=ROOT/'experiments/forecast-v2.json'; plan=json.loads(path.read_text())
    countries=[];inputs={}
    for country in plan['countries']:
        source=ROOT/'processed_data'/f'{country}_history.json'
        inputs[country]=hashlib.sha256(source.read_bytes()).hexdigest()
        countries.append(audit_country(json.loads(source.read_text()),plan))
    result={'schema_version':1, 'status':'exploratory_audit_of_spent_holdouts',
            'protocol_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'input_sha256':inputs,
            'reference':'VIIRS-only recorded active-cell union, not ground truth',
            'transition_scope':'Simulated month-boundary switch to VIIRS; zero error after switch is by construction. Not a real retirement test.',
            'release_status':'research_only; no climate-trend or operational warning validation', 'countries':countries}
    save(ROOT/'processed_data/evaluations/sensor_validation_audit.json',result)
    for c in countries:
        for f in c['outer_folds']:
            print(c['country'],f['test_year'],f['selected_mapping'],round(100*f['MAE_reduction_vs_identity'],1),'percent lower MAE')


if __name__=='__main__':main()
