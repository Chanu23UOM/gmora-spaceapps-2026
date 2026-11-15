import json
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pyrosync.mirofish import Client, MiroFishError, ScenarioStore
from pyrosync.server import handler_class


LOCKED_PROFILES = [{'name':'Asha'},{'name':'Bruno'},{'name':'Chandra'},{'name':'Devi'}]


class UpstreamStub(BaseHTTPRequestHandler):
    calls = []
    fail = None
    malformed = False
    profiles = {'count':4,'profiles':LOCKED_PROFILES}

    def log_message(self,*args):
        pass

    def do_GET(self):
        self.answer()

    def do_POST(self):
        self.answer()

    def answer(self):
        body = self.rfile.read(int(self.headers.get('Content-Length',0)))
        type(self).calls.append((self.path,body))
        if self.path == type(self).fail:
            self.send_response(503)
            self.end_headers()
            return
        responses = {
            '/health': {'status':'ok','service':'MiroFish Backend'},
            '/api/graph/ontology/generate': {'project_id':'proj_fixture'},
            '/api/graph/build': {'task_id':'graph_fixture'},
            '/api/graph/task/graph_fixture': {'status':'completed'},
            '/api/graph/project/proj_fixture': {'status':'graph_completed','graph_id':'graph_fixture'},
            '/api/simulation/create': {'simulation_id':'sim_fixture'},
            '/api/simulation/prepare': {'task_id':'prepare_fixture'},
            '/api/simulation/prepare/status': {'status':'ready'},
            '/api/simulation/sim_fixture/profiles': type(self).profiles,
            '/api/simulation/start': {'runner_status':'running'},
            '/api/simulation/sim_fixture/run-status': {'runner_status':'completed','current_round':4,'total_rounds':4},
            '/api/report/generate': {'task_id':'report_task','report_id':'report_fixture'},
            '/api/report/generate/status': {'status':'completed'},
            '/api/report/report_fixture': {'status':'completed','markdown_content':'# Simulated discussion\nThis is synthetic.'},
        }
        if self.path not in responses:
            self.send_response(404)
            self.end_headers()
            return
        value = responses[self.path]
        if self.path != '/health':
            value = {'success':True,'data':{} if type(self).malformed else value}
        payload = json.dumps(value).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class MiroFishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        data = self.root/'web_app/data'
        data.mkdir(parents=True)
        payload = {'country':'Sri_Lanka', 'summary':{'raw_rows':10,'active_cell_days':5,'multi_sensor_cell_days':2},
                   'daily':[{'date':'2025-08-01','active_cells':5},{'date':'2025-08-02','active_cells':2}],
                   'benchmark':{'selected_model':'last_week','promotion_passed':False},'limitations':['No coverage masks.']}
        (data/'Sri_Lanka.json').write_text(json.dumps(payload))
        UpstreamStub.calls=[]
        UpstreamStub.fail=None
        UpstreamStub.malformed=False
        UpstreamStub.profiles={'count':4,'profiles':LOCKED_PROFILES}
        self.upstream = ThreadingHTTPServer(('127.0.0.1',0),UpstreamStub)
        self.thread = threading.Thread(target=self.upstream.serve_forever,daemon=True)
        self.thread.start()
        self.store = ScenarioStore(self.root,Client(f'http://127.0.0.1:{self.upstream.server_port}',timeout=1))

    def tearDown(self):
        self.upstream.shutdown()
        self.upstream.server_close()
        self.thread.join()
        self.temp.cleanup()

    def test_full_rest_lifecycle_and_separate_report(self):
        state = self.store.prepare('Sri_Lanka','2025-08',max_rounds=3)
        for _ in range(12):
            state = self.store.advance(state['id'])
            if state['phase'] == 'completed':
                break
        self.assertEqual(state['phase'],'completed')
        report = (self.store.path(state['id'])/'report.md').read_text()
        self.assertIn('Unvalidated generated narrative',report)
        self.assertEqual(state['persona_count'],4)
        start = next(json.loads(b) for p,b in UpstreamStub.calls if p == '/api/simulation/start')
        self.assertEqual(start['max_rounds'],3)
        self.assertFalse(start['force'])
        self.assertFalse(start['enable_graph_memory_update'])
        ontology = next(b for p,b in UpstreamStub.calls if p == '/api/graph/ontology/generate')
        self.assertIn(b'filename="pyrosync_seed.md"',ontology)
        self.assertIn(b'artifact_sha256',ontology)
        self.assertEqual(state['release_status'],'synthetic_research_only')
        self.assertTrue(state['role_lock']['satisfied'])
        self.assertEqual(state['role_lock']['observed'],['Asha','Bruno','Chandra','Devi'])

    def run_until_stop(self, **kwargs):
        state = self.store.prepare('Sri_Lanka','2025-08',**kwargs)
        for _ in range(12):
            try:
                state = self.store.advance(state['id'])
            except MiroFishError:
                return self.store.get(state['id'])
            if state['phase'] in ('completed','failed'):
                break
        return state

    def test_role_drift_stops_before_paid_simulation(self):
        """Extra extracted actors must not be scored as a policy-comparable run."""
        UpstreamStub.profiles={'count':6,'profiles':LOCKED_PROFILES+[{'name':'MiroFish'},{'name':'PyroSync'}]}
        state = self.run_until_stop()
        self.assertEqual(state['phase'],'failed')
        self.assertFalse(state['role_lock']['satisfied'])
        self.assertEqual(state['role_lock']['unexpected'],['MiroFish','PyroSync'])
        self.assertIn('not policy-comparable',state['last_error'])
        self.assertNotIn('/api/simulation/start',[p for p,_ in UpstreamStub.calls])
        self.assertNotIn('/api/report/generate',[p for p,_ in UpstreamStub.calls])

    def test_duplicated_and_missing_roles_are_reported(self):
        UpstreamStub.profiles={'count':4,'profiles':[{'name':'Asha'},{'name':'Asha'},
                                                     {'name':'Bruno'},{'name':'Chandra'}]}
        state = self.run_until_stop()
        self.assertEqual(state['phase'],'failed')
        self.assertEqual(state['role_lock']['duplicated'],['Asha'])
        self.assertEqual(state['role_lock']['missing'],['Devi'])
        self.assertNotIn('/api/simulation/start',[p for p,_ in UpstreamStub.calls])

    def test_unverifiable_role_lock_stops_the_run(self):
        """A count alone is not evidence that the intended actors were prepared."""
        UpstreamStub.profiles={'count':4}
        state = self.run_until_stop()
        self.assertEqual(state['phase'],'failed')
        self.assertFalse(state['role_lock']['satisfied'])
        self.assertIn('cannot verify the role lock',state['role_lock']['reason'])
        self.assertNotIn('/api/simulation/start',[p for p,_ in UpstreamStub.calls])

    def test_role_drift_recorded_but_allowed_when_lock_disabled(self):
        """Exploratory runs may proceed, but the drift stays on the record."""
        UpstreamStub.profiles={'count':5,'profiles':LOCKED_PROFILES+[{'name':'MiroFish'}]}
        state = self.run_until_stop(require_exact_roles=False)
        self.assertEqual(state['phase'],'completed')
        self.assertFalse(state['role_lock']['satisfied'])
        self.assertEqual(state['role_lock']['unexpected'],['MiroFish'])
        self.assertIn('/api/simulation/start',[p for p,_ in UpstreamStub.calls])

    def test_role_lock_changes_the_run_identity(self):
        strict = self.store.prepare('Sri_Lanka','2025-08')
        relaxed = self.store.prepare('Sri_Lanka','2025-08',require_exact_roles=False)
        self.assertNotEqual(strict['id'],relaxed['id'])
        self.assertTrue(strict['require_exact_roles'])
        self.assertFalse(relaxed['require_exact_roles'])
        # Pre-lock runs must keep their original identity so that already recorded
        # study scenarios stay reconcilable: the flag enters the spec only when enforced.
        relaxed_spec = json.loads((self.store.path(relaxed['id'])/'spec.json').read_text())
        strict_spec = json.loads((self.store.path(strict['id'])/'spec.json').read_text())
        self.assertNotIn('require_exact_roles',relaxed_spec)
        self.assertTrue(strict_spec['require_exact_roles'])

    def test_require_exact_roles_must_be_boolean(self):
        with self.assertRaises(ValueError):
            self.store.prepare('Sri_Lanka','2025-08',require_exact_roles='yes')

    def test_policy_comparison_keeps_workload_and_capacity_fixed(self):
        a = self.store.prepare('Sri_Lanka','2025-08','independent',1,2)
        b = self.store.prepare('Sri_Lanka','2025-08','coordinated',1,2)
        self.assertNotEqual(a['id'],b['id'])
        self.assertEqual(a['capacity_baseline'],b['capacity_baseline'])
        self.assertEqual(a['capacity_baseline']['end_backlog'],3)
        again = self.store.prepare('Sri_Lanka','2025-08','independent',1,2)
        self.assertEqual(a['id'],again['id'])
        self.assertEqual(UpstreamStub.calls,[])

    def test_ambiguous_mutation_cannot_resubmit_after_restart(self):
        state = self.store.prepare('Sri_Lanka','2025-08')
        UpstreamStub.fail='/api/graph/ontology/generate'
        with self.assertRaises(MiroFishError):
            self.store.advance(state['id'])
        restarted = ScenarioStore(self.root,self.store.client)
        with self.assertRaises(MiroFishError):
            restarted.advance(state['id'])
        self.assertEqual(sum(p==UpstreamStub.fail for p,_ in UpstreamStub.calls),1)
        self.assertEqual(restarted.get(state['id'])['pending_operation'],'ontology')

    def test_malformed_success_keeps_mutation_uncertain(self):
        state = self.store.prepare('Sri_Lanka','2025-08')
        UpstreamStub.malformed=True
        with self.assertRaises(MiroFishError):
            self.store.advance(state['id'])
        self.assertEqual(self.store.get(state['id'])['pending_operation'],'ontology')

    def test_bounds_path_and_upstream_restrictions(self):
        for kwargs in ({'max_rounds':100},{'reviewers':True},{'policy':'invented'},{'replicate':-1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.store.prepare('Sri_Lanka','2025-08',**kwargs)
        with self.assertRaises(ValueError):
            self.store.get('../../.env')
        with self.assertRaises(ValueError):
            Client('https://example.com')

    def test_background_workflow_does_not_duplicate_submission(self):
        state = self.store.prepare('Sri_Lanka','2025-08')
        finished = threading.Event()
        original = self.store.advance
        def advance(run_id):
            result = original(run_id)
            if result['phase'] == 'completed':
                finished.set()
            return result
        with patch.object(self.store,'advance',side_effect=advance), patch('pyrosync.mirofish.time.sleep',return_value=None):
            self.store.start(state['id'])
            self.store.start(state['id'])
            self.assertTrue(finished.wait(5))
        self.assertEqual(sum(p == '/api/graph/ontology/generate' for p,_ in UpstreamStub.calls),1)

    def test_dashboard_api_preparation_and_origin_gate(self):
        server = ThreadingHTTPServer(('127.0.0.1',0),partial(handler_class(self.store),directory=str(self.root/'web_app')))
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            request = urllib.request.Request(base+'/api/scenarios',json.dumps({'country':'Sri_Lanka','month':'2025-08'}).encode(),{'Content-Type':'application/json'})
            with urllib.request.urlopen(request) as response:
                state = json.load(response)
            self.assertEqual(state['phase'],'prepared')
            with urllib.request.urlopen(base+'/api/scenarios/'+state['id']) as response:
                self.assertEqual(json.load(response)['id'],state['id'])
            with urllib.request.urlopen(base+'/api/research') as response:
                research=json.load(response)
                self.assertEqual(research['schema_version'],1)
                self.assertEqual(research['results']['forecast_v2']['status'],'not_built')
            request.add_header('Origin','https://foreign.example')
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            self.assertEqual(error.exception.code,403)
            self.assertEqual(UpstreamStub.calls,[])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
