"""Pinned MiroFish REST adapter and durable, bounded tabletop workflow."""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from .data import COUNTRIES
from .evidence import evidence_packet, render_brief

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'integrations/mirofish.json').read_text())
POLICIES = {
    'independent': 'Each role publishes its own evidence-grounded update independently, without a designated bulletin coordinator.',
    'coordinated': 'The field coordinator collects the same role updates and publishes one daily evidence-grounded bulletin; other roles review and correct it.',
}
ROLES = {
    'Asha': 'fictional district analyst; explain the observed workload and data coverage limits',
    'Bruno': 'fictional field coordinator; discuss review priorities and communication bottlenecks',
    'Chandra': 'fictional agricultural liaison; flag ambiguous agricultural-versus-wildfire attribution',
    'Devi': 'fictional skeptical reviewer; challenge unsupported claims and missing evidence',
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    temporary.replace(path)


class MiroFishError(RuntimeError):
    pass


class Client:
    def __init__(self, base=None, timeout=180):
        self.base = (base or os.environ.get('PYROSYNC_MIROFISH_URL', PIN['api_base'])).rstrip('/')
        # The local UI is not an arbitrary HTTP proxy. Credentials live upstream.
        if not re.fullmatch(r'http://(127\.0\.0\.1|localhost):[0-9]{1,5}', self.base):
            raise ValueError('MiroFish URL must be a local http://127.0.0.1:PORT service')
        self.timeout = timeout

    def request(self, path, data=None, multipart=None):
        headers = {'Accept': 'application/json', 'Accept-Language': 'en'}
        body = None
        if multipart is not None:
            boundary = 'PyroSync' + uuid.uuid4().hex
            chunks = []
            for name, value in multipart.items():
                chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
            chunks.append(f'--{boundary}--\r\n'.encode())
            body = b''.join(chunks)
            headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        elif data is not None:
            body = json.dumps(data).encode()
            headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(self.base+path, body, headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            # Do not expose upstream response bodies: they may contain provider details.
            code = getattr(exc, 'code', None)
            raise MiroFishError(f'MiroFish request failed ({code or type(exc).__name__}); inspect its local logs.') from exc
        if path == '/health':
            if result.get('service') != 'MiroFish Backend' or result.get('status') != 'ok':
                raise MiroFishError('Unexpected service on MiroFish port')
            return result
        if result.get('success') is not True or not isinstance(result.get('data'), dict):
            raise MiroFishError('MiroFish returned an unsuccessful or incompatible response')
        return result['data']

    def ontology(self, seed, requirement, name):
        boundary = 'PyroSync' + uuid.uuid4().hex
        chunks = []
        for key, value in {'project_name': name, 'simulation_requirement': requirement,
                           'additional_context': 'English. Exactly the four named fictional stakeholder personas; never treat H3 cells as agents.'}.items():
            chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="pyrosync_seed.md"\r\nContent-Type: text/markdown\r\n\r\n'.encode()+seed.encode()+b'\r\n')
        chunks.append(f'--{boundary}--\r\n'.encode())
        request = urllib.request.Request(self.base+'/api/graph/ontology/generate', b''.join(chunks),
                                         {'Content-Type':f'multipart/form-data; boundary={boundary}', 'Accept-Language':'en'})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise MiroFishError('Ontology submission failed; inspect MiroFish before retrying to avoid duplicate projects.') from exc
        if result.get('success') is not True or not isinstance(result.get('data'), dict):
            raise MiroFishError('Ontology response unsuccessful or incompatible')
        return result['data']


def doctor(root=ROOT, client=None):
    checkout = root/'.integrations/mirofish'
    configured = {key: bool(os.environ.get(key)) for key in ('LLM_API_KEY', 'ZEP_API_KEY')}
    env = checkout/'.env'
    if env.exists():
        for line in env.read_text().splitlines():
            key, _, value = line.partition('=')
            if key.strip() in configured and value.strip().strip('"\''):
                configured[key.strip()] = True
    status = {'revision': PIN['revision'], 'source_present': (checkout/'backend/run.py').exists(),
              'runtime_present': (checkout/'backend/.venv/bin/python').exists(),
              'credentials_present': configured, 'connected': False}
    try:
        (client or Client(timeout=2)).request('/health')
        status['connected'] = True
    except MiroFishError:
        pass
    status['message'] = ('MiroFish backend connected. Scenarios may use its configured LLM and Zep services.'
                         if status['connected'] else 'MiroFish is offline. Run make mirofish-setup, configure its local .env, then make mirofish-start.')
    return status


class ScenarioStore:
    def __init__(self, root=ROOT, client=None, evidence_root=None):
        self.root = Path(root)
        self.evidence_root=Path(evidence_root) if evidence_root else self.root/'web_app/data'
        self.directory = self.root/'processed_data/scenarios'
        self.client = client or Client()
        self.lock = threading.Lock()
        self.jobs = set()

    def path(self, run_id):
        if not re.fullmatch(r'[0-9a-f]{20}', run_id):
            raise ValueError('invalid scenario ID')
        return self.directory/run_id

    def get(self, run_id):
        result = json.loads((self.path(run_id)/'state.json').read_text())
        with self.lock:
            result['busy'] = run_id in self.jobs
        return result

    def prepare(self, country, month, policy='coordinated', reviewers=4,
                reviews_per_day=20, max_rounds=4, replicate=0):
        if country not in COUNTRIES or policy not in POLICIES:
            raise ValueError('unknown country or policy')
        if not isinstance(month, str) or not re.fullmatch(r'2025-(0[1-9]|1[0-2])', month):
            raise ValueError('month must be in 2025')
        for name, value, low, high in [('reviewers',reviewers,1,100), ('reviews_per_day',reviews_per_day,1,1000),
                                       ('max_rounds',max_rounds,1,12), ('replicate',replicate,0,1000)]:
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f'{name} must be an integer in {low}..{high}')
        payload = json.loads((self.evidence_root/f'{country}.json').read_text())
        packet = evidence_packet(payload)
        render_brief(payload, packet)  # Same evidence gate as the existing brief.
        days = [d for d in payload['daily'] if d['date'].startswith(month)]
        assumption = {'reviewers': reviewers, 'reviews_per_reviewer_day': reviews_per_day,
                      'interpretation': 'One observed active cell-day is assumed to generate one review ticket; not a fire incident.'}
        spec = {'schema_version':1, 'country':country, 'month':month, 'policy':policy,
                'assumptions': assumption, 'max_rounds':max_rounds, 'replicate':replicate,
                'upstream_revision':PIN['revision'], 'artifact_sha256':packet['artifact_sha256'],
                'runtime_patch_sha256':hashlib.sha256((ROOT/'integrations/mirofish-tabletop.patch').read_bytes()).hexdigest() if (ROOT/'integrations/mirofish-tabletop.patch').exists() else None,
                'daily_workload':[{'date':d['date'], 'review_tickets':d['active_cells']} for d in days],
                'roles': ROLES, 'release_status':'synthetic_research_only'}
        run_id = hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()[:20]
        path = self.path(run_id)
        if (path/'state.json').exists():
            return self.get(run_id)
        capacity = reviewers*reviews_per_day
        queue, peak = 0, 0
        for day in spec['daily_workload']:
            queue = max(0, queue+day['review_tickets']-capacity)
            peak = max(peak,queue)
        spec['capacity_baseline'] = {'daily_capacity':capacity, 'end_backlog':queue, 'peak_backlog':peak,
                                      'method':'Deterministic daily queue, starts empty; same assumptions for both policies. Not a MiroFish result.'}
        requirement = (f'Run a synthetic communication-policy tabletop in English for {country.replace("_"," ")} {month}. '
                       f'Policy: {POLICIES[policy]} Use only Asha, Bruno, Chandra and Devi as stakeholder personas. '
                       'Use the supplied workload and assumptions unchanged. Discuss workload interpretation, duplicate claims, '
                       'uncertainty communication and correction of unsupported statements. Treat the social platform as an internal simulated discussion board. '
                       'Compare observations with assumptions explicitly. Report qualitative communication findings and unresolved questions. '
                       'Do not invent measured response times, public behaviour, accuracy, burned area, lives saved or ignition/spread forecasts. '
                       'No real-world posting or messaging. The capacity queue is computed independently; do not claim the conversation improves it.')
        seed = '# PyroSync synthetic tabletop seed\n\n'+requirement+'\n\n## Scenario and immutable evidence\n\n```json\n'+json.dumps(spec,indent=2)+'\n```\n\n## Observation limitations\n'+ '\n'.join('- '+s for s in payload['limitations'])+'\n'
        path.mkdir(parents=True, exist_ok=True)
        (path/'seed.md').write_text(seed)
        save(path/'spec.json', spec)
        save(path/'state.json', {'id':run_id,'country':country,'month':month,'policy':policy,
                                'phase':'prepared','requirement':requirement,'max_rounds':max_rounds,
                                'capacity_baseline':spec['capacity_baseline'], 'trace':[],
                                'upstream_revision':PIN['revision'], 'pending_operation':None,
                                'release_status':'synthetic_research_only'})
        return self.get(run_id)

    def advance(self, run_id):
        """Perform one transition. Never automatically repeat an ambiguous mutation."""
        state = self.get(run_id)
        path = self.path(run_id)
        if state.get('pending_operation'):
            raise MiroFishError('Uncertain upstream operation. Reconcile its IDs with local MiroFish before retrying; no automatic resubmission.')
        phase = state['phase']
        if phase in ('completed','failed'):
            return state
        def mutate(operation, action):
            state['pending_operation'] = operation
            save(path/'state.json', state)
            result = action()
            state['trace'].append({'operation':operation, 'result':'accepted'})
            return result
        def check_task(result):
            if result.get('status') == 'failed':
                state['phase'] = 'failed'
                raise MiroFishError('Upstream task failed; inspect its local logs.')
            return result.get('status') in ('completed','ready')
        try:
            if phase == 'prepared':
                self.client.request('/health')
                result = mutate('ontology', lambda: self.client.ontology((path/'seed.md').read_text(), state['requirement'], f'PyroSync {run_id}'))
                state['project_id'] = result['project_id']
                state['phase'] = 'ontology_ready'
            elif phase == 'ontology_ready':
                result = mutate('graph_build', lambda: self.client.request('/api/graph/build', {'project_id':state['project_id']}))
                state['graph_task_id'] = result['task_id']
                state['phase'] = 'graph_building'
            elif phase == 'graph_building':
                result = self.client.request('/api/graph/task/'+state['graph_task_id'])
                if check_task(result):
                    project = self.client.request('/api/graph/project/'+state['project_id'])
                    if project.get('status') != 'graph_completed' or not project.get('graph_id'):
                        raise MiroFishError('Graph task completed without a ready project graph')
                    state['graph_id'] = project['graph_id']
                    state['phase'] = 'graph_ready'
            elif phase == 'graph_ready':
                result = mutate('simulation_create', lambda: self.client.request('/api/simulation/create',
                                  {'project_id':state['project_id'],'graph_id':state['graph_id'], 'enable_twitter':False,'enable_reddit':True}))
                state['simulation_id'] = result['simulation_id']
                state['phase'] = 'created'
            elif phase == 'created':
                result = mutate('simulation_prepare', lambda: self.client.request('/api/simulation/prepare',
                                  {'simulation_id':state['simulation_id'],'use_llm_for_profiles':False,'parallel_profile_count':1}))
                state['prepare_task_id'] = result.get('task_id')
                state['phase'] = 'ready' if result.get('already_prepared') else 'preparing'
            elif phase == 'preparing':
                result = self.client.request('/api/simulation/prepare/status',
                                            {'simulation_id':state['simulation_id'],'task_id':state['prepare_task_id']})
                if check_task(result):
                    state['phase'] = 'ready'
            elif phase == 'ready':
                profiles = self.client.request('/api/simulation/'+state['simulation_id']+'/profiles')
                if type(profiles.get('count')) is not int or not 1 <= profiles['count'] <= 8:
                    state['phase'] = 'failed'
                    raise MiroFishError('Prepared persona count is outside the 1..8 pilot limit; simulation not started.')
                state['persona_count'] = profiles['count']
                mutate('simulation_start', lambda: self.client.request('/api/simulation/start',
                       {'simulation_id':state['simulation_id'],'platform':'reddit','max_rounds':state['max_rounds'],
                        'enable_graph_memory_update':False,'force':False}))
                state['phase'] = 'running'
            elif phase == 'running':
                result = self.client.request('/api/simulation/'+state['simulation_id']+'/run-status')
                status = result.get('runner_status')
                if status == 'failed':
                    state['phase'] = 'failed'
                    raise MiroFishError('MiroFish simulation failed')
                if status in ('completed','stopped'):
                    state['phase'] = 'simulated'
                state['progress'] = {k:result.get(k) for k in ('current_round','total_rounds','total_actions_count')}
            elif phase == 'simulated':
                result = mutate('report_generate', lambda: self.client.request('/api/report/generate', {'simulation_id':state['simulation_id']}))
                state['report_id'] = result['report_id']
                state['report_task_id'] = result.get('task_id')
                state['phase'] = 'reporting'
            elif phase == 'reporting':
                result = self.client.request('/api/report/generate/status',
                                            {'simulation_id':state['simulation_id'],'task_id':state['report_task_id']})
                if check_task(result):
                    report = self.client.request('/api/report/'+state['report_id'])
                    if report.get('status') != 'completed' or not isinstance(report.get('markdown_content'),str):
                        raise MiroFishError('Report status/content is not complete')
                    # Keep generated prose outside the verified-observation claim system.
                    save(path/'upstream_report.json', report)
                    (path/'report.md').write_text('# Synthetic MiroFish tabletop report\n\nUnvalidated generated narrative. Not a physical forecast or verified PyroSync evidence brief.\n\n'+report['markdown_content'])
                    state['phase'] = 'completed'
            elif phase not in ('completed','failed'):
                raise MiroFishError('Unknown workflow phase')
            state['pending_operation'] = None
            state.pop('last_error',None)
        except (MiroFishError, KeyError, TypeError) as exc:
            state['last_error'] = str(exc) if isinstance(exc,MiroFishError) else 'Incompatible MiroFish response schema'
            save(path/'state.json', state)
            raise MiroFishError(state['last_error']) from exc
        save(path/'state.json', state)
        return self.get(run_id)

    def start(self, run_id):
        self.get(run_id)
        with self.lock:
            if run_id in self.jobs:
                return
            self.jobs.add(run_id)
        def worker():
            try:
                deadline = time.monotonic()+2700
                while time.monotonic() < deadline:
                    state = self.advance(run_id)
                    if state['phase'] in ('completed','failed'):
                        break
                    time.sleep(3)
            except MiroFishError:
                pass  # Durable last_error and pending_operation explain the failure.
            finally:
                with self.lock:
                    self.jobs.discard(run_id)
        threading.Thread(target=worker, daemon=True).start()
