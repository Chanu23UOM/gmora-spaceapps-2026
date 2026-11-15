"""Run/reconcile the frozen MiroFish study and export a blinded review packet."""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import random
import shutil
import secrets
import time
import urllib.request
from pathlib import Path

from .mirofish import ROOT, ROLES, ScenarioStore, MiroFishError, save


def cases(plan):
    return [(c,p,r) for c in plan['countries'] for r in plan['replicates'] for p in plan['policies']]


def role_names_match(profiles):
    names=[profile.get('name') for profile in profiles]
    return len(names)==len(ROLES) and set(names)==set(ROLES)


def role_comparable(result):
    """Only runs with exactly one profile per intended actor can be paired.

    Prefers the lock recorded durably at simulation-start time; falls back to a
    post-hoc profile listing. Absence of evidence is not treated as a match.
    """
    lock=result.get('role_lock')
    if isinstance(lock,dict) and 'satisfied' in lock:
        return bool(lock['satisfied'])
    return result.get('role_names_match') is True


def freeze_inputs(plan,root=ROOT):
    directory=root/'processed_data/policy_inputs';directory.mkdir(parents=True,exist_ok=True)
    marker=directory/'manifest.json'
    if marker.exists():
        hashes=json.loads(marker.read_text())
        for name,digest in hashes.items():
            if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
                raise ValueError('Frozen policy input changed; refusing to continue')
    else:
        hashes={}
        for country in plan['countries']:
            name=country+'.json';shutil.copyfile(root/'web_app/data'/name,directory/name)
            hashes[name]=hashlib.sha256((directory/name).read_bytes()).hexdigest()
        save(marker,hashes)
    return directory


def execute(case, plan):
    country,policy,replicate=case;store=ScenarioStore(evidence_root=freeze_inputs(plan))
    state=store.prepare(country,plan['month'],policy,plan['reviewers'],plan['reviews_per_day'],
                        plan['max_rounds'],replicate,plan.get('require_exact_roles',False))
    start=time.monotonic();last=None
    try:
        while time.monotonic()-start<2400:
            state=store.advance(state['id'])
            if state['phase']!=last:
                print(state['id'],state['phase'],flush=True);last=state['phase']
            if state['phase'] in ('completed','failed'):break
            time.sleep(5)
    except MiroFishError:
        pass
    save(store.path(state['id'])/'study_metadata.json',{'study':plan['id'],'replicate':replicate,
         'elapsed_seconds':round(time.monotonic()-start,2),'model':'google/gemini-3.8-flash',
         'provider':'Google Vertex AI','monetary_cost':None,'cost_note':'Provider invoice/price audit not available; not inferred from rounds.'})
    return store.get(state['id'])


def summarize(plan,root=ROOT,plan_path=None):
    evidence_root=freeze_inputs(plan,root)
    store=ScenarioStore(root,evidence_root=evidence_root);results=[];review=[]
    for country,policy,replicate in cases(plan):
        state=store.prepare(country,plan['month'],policy,plan['reviewers'],plan['reviews_per_day'],
                            plan['max_rounds'],replicate,plan.get('require_exact_roles',False))
        path=store.path(state['id']);metadata=json.loads((path/'study_metadata.json').read_text()) if (path/'study_metadata.json').exists() else {}
        result={k:state.get(k) for k in ('id','country','month','policy','phase','project_id','graph_id','simulation_id','report_id','persona_count','last_error','capacity_baseline','require_exact_roles','role_lock')}
        result.update({'replicate':replicate,'metadata':metadata,'release_status':'synthetic_research_only'})
        if state.get('simulation_id'):
            try:
                profiles=store.client.request('/api/simulation/'+state['simulation_id']+'/profiles')
                result['actual_personas']=[{'name':p.get('name') or p.get('username'),'description':p.get('description','')[:300]} for p in profiles.get('profiles',[])]
                result['actual_profile_count']=profiles.get('count')
                result['role_names_match']=role_names_match(result['actual_personas'])
            except MiroFishError:result['actual_personas_status']='unavailable'
        if state['phase']=='completed':
            text=(path/'report.md').read_text()
            blind_id=hashlib.sha256((plan['id']+state['id']).encode()).hexdigest()[:12]
            review.append({'blind_id':blind_id,'text':text,'run_id':state['id'],'policy':policy})
            result['report_sha256']=hashlib.sha256(text.encode()).hexdigest()
        results.append(result)
    for country in plan['countries']:
        payload=json.loads((evidence_root/f'{country}.json').read_text())
        days=[d for d in payload['daily'] if d['date'].startswith(plan['month'])]
        text=(f'# Recorded activity summary\n\n{country.replace("_"," ")} · {plan["month"]}\n\n'
              f'Raw observations: {sum(d["raw"] for d in days)}. Quality-filtered active cell-days: {sum(d["active_cells"] for d in days)}. '
              'An active cell-day is a grid observation unit, not a distinct fire.\n\n'
              +'\n'.join('- '+item for item in payload['limitations']))
        review.append({'blind_id':hashlib.sha256((plan['id']+country+'baseline').encode()).hexdigest()[:12],
                       'text':text,'run_id':None,'policy':'deterministic_baseline'})
    random.Random(42).shuffle(review)
    review_dir=root/'processed_data/policy_review_private';review_dir.mkdir(parents=True,exist_ok=True)
    labels_path=review_dir/'review_labels.json'
    labels=json.loads(labels_path.read_text()) if labels_path.exists() else {}
    for item in review:
        item['blind_id']=labels.setdefault(item['blind_id'],secrets.token_hex(6))
    save(labels_path,labels)
    for item in review:
        (review_dir/(item['blind_id']+'.md')).write_text(item['text'])
    save(review_dir/'unblinding_key.json',[{k:v for k,v in item.items() if k!='text'} for item in review])
    fields=('blind_id','reviewer','unsupported_claims_0_3','uncertainty_omissions_0_3','contradictions_0_3',
            'usefulness_0_3','unblinding_guess','incomplete','notes')
    scores_path=review_dir/'scores.csv'
    existing=list(csv.DictReader(scores_path.open())) if scores_path.exists() else []
    valid_ids={item['blind_id'] for item in review}
    stale=[row for row in existing if row['blind_id'] not in valid_ids and any(v for k,v in row.items() if k!='blind_id')]
    if stale:save(review_dir/'legacy_scores.json',stale)
    existing=[row for row in existing if row['blind_id'] in valid_ids]
    known={row['blind_id'] for row in existing}
    existing += [{'blind_id':item['blind_id']} for item in review if item['blind_id'] not in known]
    with scores_path.open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(existing)
    comparisons=[]
    for country in plan['countries']:
        rows=[r for r in results if r['country']==country]
        def cell(rep,policy):
            return next(r for r in rows if r['replicate']==rep and r['policy']==policy)
        comparisons.append({'country':country,'completed':sum(r['phase']=='completed' for r in rows),
             'planned':len(rows),'capacity_baseline_equal':len({json.dumps(r['capacity_baseline'],sort_keys=True) for r in rows})==1,
             'role_comparable_runs':sum(r['phase']=='completed' and role_comparable(r) for r in rows),
             'eligible_pairs':sum(all(cell(rep,policy)['phase']=='completed' and role_comparable(cell(rep,policy))
                                      for policy in plan['policies']) for rep in plan['replicates'])})
    plan_file=Path(plan_path) if plan_path else root/'experiments/mirofish-policies-v1.json'
    output={'schema_version':1,'protocol_id':plan['id'],'protocol_path':str(plan_file.relative_to(root)),
            'protocol_sha256':hashlib.sha256(plan_file.read_bytes()).hexdigest(),
            'require_exact_roles':plan.get('require_exact_roles',False),
            'runs':results,'comparisons':comparisons,'human_review_status':'pending independent blinded reviewers',
            'efficacy_claim':'abstain: generated narratives and operational benefit are not validated',
            'blinding_limit':'Identifiers/policy labels removed from filenames; narrative may reveal its policy. Reviewers must record unblinding guesses.',
            'replicate_labels_are_random_seeds':False}
    usage_file=root/'.integrations/vertex-usage.jsonl'
    usage=[json.loads(line) for line in usage_file.read_text().splitlines()] if usage_file.exists() else []
    output['provider_usage']={'observed_requests':len(usage),
        'reported_total_tokens':sum((r.get('usage') or {}).get('total_tokens',0) for r in usage),
        'reported_models':sorted({r['model'] for r in usage if r.get('model')}),
        'monetary_cost':None,'scope':'Shared local relay after tabletop patch restart; not attributable per scenario. Streaming usage may be unavailable.'}
    save(root/'processed_data/evaluations/policy_study.json',output)
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true');parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--plan',help='frozen protocol JSON (default: experiments/mirofish-policies-v1.json)')
    parser.add_argument('--wait-services',action='store_true');args=parser.parse_args()
    if args.wait_services:
        for _ in range(60):
            try:
                for url in ('http://127.0.0.1:5001/health','http://127.0.0.1:5002/health'):
                    with urllib.request.urlopen(url,timeout=2):pass
                return
            except OSError:time.sleep(2)
        raise SystemExit('Pilot services did not start')
    plan_path=Path(args.plan) if args.plan else ROOT/'experiments/mirofish-policies-v1.json'
    plan=json.loads(plan_path.read_text())
    if args.run:
        freeze_inputs(plan)
        todo=cases(plan)[:1] if args.pilot else cases(plan)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            completed=list(pool.map(lambda case:execute(case,plan),todo))
        output=summarize(plan,plan_path=plan_path)
        if args.pilot and completed[0]['phase']!='completed':
            raise SystemExit('Pilot did not complete; inspect sanitized result and local upstream logs')
    else:output=summarize(plan,plan_path=plan_path)
    print('Completed scenarios:',sum(r['phase']=='completed' for r in output['runs']),'of',len(output['runs']))


if __name__=='__main__':main()
