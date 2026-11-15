"""Inject manually dispatched CI secrets without emitting their values."""
import json
import os
from pathlib import Path

from .mirofish import ROOT


def main():
    names=('PILOT_ZEP_KEY','PILOT_BRIDGE_KEY','PILOT_VERTEX_JSON','PILOT_PROJECT','PILOT_MODEL')
    if any(not os.environ.get(name) for name in names):
        raise SystemExit('Required pilot secrets/configuration are missing')
    credential=json.loads(os.environ['PILOT_VERTEX_JSON'])
    if credential.get('type')!='service_account':
        raise SystemExit('Expected a Google service-account credential')
    path=ROOT/'.integrations/vertex-service-account.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(credential));path.chmod(0o600)
    values={'LLM_API_KEY':os.environ['PILOT_BRIDGE_KEY'],'ZEP_API_KEY':os.environ['PILOT_ZEP_KEY'],
            'LLM_BASE_URL':'http://127.0.0.1:5002/v1','LLM_MODEL_NAME':os.environ['PILOT_MODEL'],
            'VERTEX_PROJECT':os.environ['PILOT_PROJECT'],'VERTEX_LOCATION':os.environ.get('PILOT_LOCATION') or 'global',
            'GOOGLE_APPLICATION_CREDENTIALS':str(path),'FLASK_HOST':'127.0.0.1','FLASK_DEBUG':'false'}
    if any('\n' in value or '\r' in value for value in values.values()):
        raise SystemExit('Multiline provider setting rejected')
    env=ROOT/'.integrations/mirofish/.env';env.parent.mkdir(parents=True,exist_ok=True)
    env.write_text('\n'.join(k+'='+v for k,v in values.items())+'\n');env.chmod(0o600)
    print('Pilot credentials injected; values hidden.')


if __name__=='__main__':main()
