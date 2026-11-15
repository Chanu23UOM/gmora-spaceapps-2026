"""Frozen historical forecast and sensor-comparison experiments."""
import argparse
import hashlib
import json
import math
from datetime import date, timedelta

import numpy as np

from .forecast import predict, metrics, interval_radius, paired_block_interval
from .mirofish import ROOT, save


def candidate(history, model, horizon=7):
    if model != 'ewma_14':
        return predict(history,model,horizon)
    values=np.asarray(history[-56:],dtype=float)
    weights=(1-2/15)**np.arange(len(values)-1,-1,-1)
    return np.repeat(np.average(values,weights=weights),horizon)


def score_folds(folds):
    return metrics(np.concatenate([f['actual'] for f in folds]),np.concatenate([f['prediction'] for f in folds]))


def evaluate_country(payload,plan):
    daily=payload['daily']; dates=[date.fromisoformat(d['date']) for d in daily]
    if any(d['active_cells'] is None or not d['complete_source_inputs'] for d in daily):
        return {'country':payload['country'],'status':'insufficient_inputs','reason':'Missing source inputs; no zero imputation.'},[]
    y=np.array([d['active_cells'] for d in daily],dtype=float)
    folds=[]
    for origin in range(plan['initial_history_days'],len(y)-6,7):
        if dates[origin].year != dates[origin+6].year:
            continue
        for model in plan['models']:
            p=candidate(y[:origin],model)
            folds.append({'model':model,'origin':daily[origin]['date'],'train_end':daily[origin-1]['date'],
                          'target_dates':[d['date'] for d in daily[origin:origin+7]],
                          'year':dates[origin].year,'actual':y[origin:origin+7].tolist(),'prediction':p.tolist()})
    outputs=[]
    for outer in plan['outer_folds']:
        bymodel={m:{'selection':[f for f in folds if f['model']==m and f['year'] in outer['selection_years']],
                    'calibration':[f for f in folds if f['model']==m and f['year']==outer['calibration_year']],
                    'test':[f for f in folds if f['model']==m and f['year']==outer['test_year']]} for m in plan['models']}
        if any(not values for splits in bymodel.values() for values in splits.values()):
            raise ValueError('Incomplete preregistered outer fold')
        selected=min(plan['models'],key=lambda m:score_folds(bymodel[m]['selection'])['mae'])
        results=[]
        for model,splits in bymodel.items():
            calibration=splits['calibration'];test=splits['test']
            radius=interval_radius([np.abs(np.array(f['actual'])-f['prediction']) for f in calibration])
            actual=np.array([f['actual'] for f in test]);pred=np.array([f['prediction'] for f in test])
            lower=np.maximum(0,pred-radius);upper=pred+radius
            results.append({'model':model,'selection':score_folds(splits['selection']),'test':score_folds(test),
                            'coverage_80':float(((actual>=lower)&(actual<=upper)).mean()),
                            'mean_interval_width':float((upper-lower).mean()),'test_origins':len(test),
                            'quarter_mae':{str(q):score_folds([f for f in test if (int(f['origin'][5:7])-1)//3+1==q])['mae'] for q in range(1,5)}})
        baseline=bymodel['last_week']['test'];winner=bymodel[selected]['test']
        ci=paired_block_interval([np.mean(np.abs(np.array(a['actual'])-a['prediction']))-
                                  np.mean(np.abs(np.array(b['actual'])-b['prediction'])) for a,b in zip(winner,baseline)])
        base_mae=results[0]['test']['mae'];mae=next(r['test']['mae'] for r in results if r['model']==selected)
        skill=1-mae/base_mae if base_mae else None
        outputs.append({**outer,'selected_model':selected,'results':results,'MAE_skill':skill,
                        'paired_weekly_MAE_delta_ci95':ci,'promotion_passed':selected!='last_week' and skill is not None and skill>=.05 and ci[1]<0})
    return {'country':payload['country'],'status':'evaluated','outer_folds':outputs,
            'coverage':'unknown; forecast of recorded observations only','release_status':'research_only'},folds


def mapping(train, test, method):
    output=[]
    global_ratio=sum(d['viirs_active_cells'] for d in train)/max(1,sum(d['source_cells']['modis'] for d in train))
    for day in test:
        month=day['date'][5:7];sample=[d for d in train if d['date'][5:7]==month]
        x=np.array([d['source_cells']['modis'] for d in sample]);v=np.array([d['viirs_active_cells'] for d in sample])
        value=day['source_cells']['modis']
        if method=='identity':p=value
        elif method=='monthly_ratio':p=value*(v.sum()/x.sum() if x.sum() else global_ratio)
        elif method=='monthly_quantile_mapping':
            unique=np.unique(x)
            ranks=np.array([((x<item).sum()+.5*(x==item).sum())/len(x) for item in unique])
            p=float(np.interp(value,unique,np.quantile(v,ranks)))
        else:raise ValueError('unknown mapping')
        output.append(float(p))
    return output


def calibration_country(payload,plan):
    daily=payload['daily'];out=[]
    for fold in plan['outer_folds']:
        train=[d for d in daily if int(d['date'][:4]) in fold['selection_years']]
        calibration=[d for d in daily if int(d['date'][:4])==fold['calibration_year']]
        test=[d for d in daily if int(d['date'][:4])==fold['test_year']]
        if not train or not calibration or not test or any(not d['complete_source_inputs'] for d in train+calibration+test):
            raise ValueError('Incomplete calibration inputs')
        target=np.array([d['viirs_active_cells'] for d in test]);threshold=float(np.quantile([d['viirs_active_cells'] for d in train],.9))
        selected=min(plan['calibration_candidates'],key=lambda method:metrics([d['viirs_active_cells'] for d in calibration],mapping(train,calibration,method))['mae'])
        results=[]
        for method in plan['calibration_candidates']:
            p=np.array(mapping(train,test,method));mask=target>=threshold
            results.append({'method':method,'test':metrics(target,p),'mean_bias':float(np.mean(p-target)),
                            'extreme_threshold_from_training':threshold,'extreme_day_MAE':metrics(target[mask],p[mask])['mae'] if mask.any() else None})
        out.append({**fold,'selected_mapping':selected,'results':results})
    return {'country':payload['country'],'outer_folds':out,'reference':'VIIRS-only observed daily union; not ground truth',
            'claim':'Held-out distribution comparison; no validated historical fire-incidence reconstruction.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    protocol=ROOT/'experiments/forecast-v2.json';plan=json.loads(protocol.read_text())
    forecast=[];calibration=[]
    for country in plan['countries']:
        payload=json.loads((ROOT/'processed_data'/f'{country}_history.json').read_text())
        f,predictions=evaluate_country(payload,plan);forecast.append(f)
        calibration.append(calibration_country(payload,plan))
        save(ROOT/'processed_data/evaluations'/f'{country}_predictions.json',predictions)
        print(country,[(o['test_year'],o['selected_model'],o['MAE_skill'],o['promotion_passed']) for o in f.get('outer_folds',[])],flush=True)
    common={'schema_version':1,'protocol_id':plan['id'],'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),
            'input_manifest_sha256':hashlib.sha256((ROOT/'processed_data/history_manifest.json').read_bytes()).hexdigest()}
    save(ROOT/'processed_data/evaluations/forecast_v2.json',{**common,'countries':forecast})
    save(ROOT/'processed_data/evaluations/sensor_calibration_v1.json',{**common,'countries':calibration})


if __name__=='__main__':main()
