"""Vercel adapter: public archive and scenario preparation, without provider keys."""
import tempfile
from urllib.parse import urlsplit

from pyrosync.mirofish import ROOT, ScenarioStore
from pyrosync.server import handler_class

# Vercel's deployed source is read-only. Preparation writes only to /tmp;
# the browser retains prepared states so a cold start does not lose a download.
store = ScenarioStore(root=tempfile.mkdtemp(prefix='pyrosync-'), evidence_root=ROOT/'web_app/data')
Base = handler_class(store)


class handler(Base):
    def do_GET(self):
        path=urlsplit(self.path).path
        if path == '/api/mirofish':
            return self.reply(200, {'connected':False, 'hosting_mode':'public_archive',
                'scenario_execution':'local_backend_only',
                'message':'Public demo: prepare and download scenario states here. New AI simulations run through the separately configured local MiroFish backend; no paid AI service is exposed on this public site.'})
        if path == '/api/research':
            import json
            results={}
            for name in ('forecast_v2','sensor_calibration_v1','policy_study','sensor_validation_audit'):
                source=ROOT/'processed_data/evaluations'/f'{name}.json'
                results[name]=json.loads(source.read_text()) if source.exists() else {'status':'not_built'}
            return self.reply(200,{'schema_version':1,'results':results,'purpose':'research only; not operational alerts'})
        if path.startswith('/api/scenarios/'):
            return super().do_GET()
        return self.reply(404,{'error':'Unknown API route'})

    def do_POST(self):
        # The shared local handler expects HTTP loopback. Vercel is HTTPS.
        # Enforce origin here, then pass the validated request to that handler.
        origin=self.headers.get('Origin')
        host=self.headers.get('X-Forwarded-Host') or self.headers.get('Host','')
        if origin and origin not in {f'https://{host}',f'http://{host}'}:
            return self.reply(403,{'error':'Cross-origin mutation denied'})
        if urlsplit(self.path).path != '/api/scenarios':
            return self.reply(409,{'error':'New AI simulations require the configured local MiroFish backend.'})
        if origin:
            del self.headers['Origin']
        return super().do_POST()
