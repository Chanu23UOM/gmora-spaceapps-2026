"""Install the pinned upstream backend separately from PyroSync."""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pin = json.loads((ROOT/'integrations/mirofish.json').read_text())
checkout = ROOT/'.integrations/mirofish'

if not shutil.which('uv'):
    raise SystemExit('Install uv first: https://docs.astral.sh/uv/getting-started/installation/')
created = not (checkout/'.git').exists()
if created:
    subprocess.run(['git','clone','--no-checkout',pin['repository'],str(checkout)],check=True)
current = subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD'],text=True).strip()
if current != pin['revision']:
    # Refuse to overwrite local upstream edits.
    if not created and subprocess.check_output(['git','-C',str(checkout),'status','--porcelain'],text=True).strip():
        raise SystemExit('Upstream checkout has local edits; preserve them before switching revisions.')
    subprocess.run(['git','-C',str(checkout),'fetch','origin',pin['revision']],check=True)
    subprocess.run(['git','-C',str(checkout),'checkout','--detach',pin['revision']],check=True)
elif not (checkout/'backend/run.py').exists():
    subprocess.run(['git','-C',str(checkout),'checkout','--detach',pin['revision']],check=True)
python = checkout/'backend/.venv/bin/python'
if not python.exists():
    subprocess.run(['uv','venv','--python','3.12',str(python.parent.parent)],check=True)
# Upstream's general lock pulls CUDA libraries on Linux. This application uses
# hosted LLMs; install CPU torch first and constrain its version for this backend.
subprocess.run(['uv','pip','install','--python',str(python),'--index-url',
                'https://download.pytorch.org/whl/cpu','torch==2.10.0+cpu'],check=True)
subprocess.run(['uv','pip','install','--python',str(python),'-e',str(checkout/'backend'),
                '--constraint',str(ROOT/'integrations/mirofish-cpu.txt')],check=True)
if not (checkout/'.env').exists():
    shutil.copyfile(ROOT/'integrations/mirofish.env.example',checkout/'.env')
    (checkout/'.env').chmod(0o600)
subprocess.run([str(python),'-c',
                'import oasis; from app import create_app; '
                'response=create_app().test_client().get("/health"); '
                'assert response.status_code == 200; print("OASIS import and upstream health passed")'],
               cwd=str(checkout/'backend'),check=True)
print('Installed pinned MiroFish backend. Configure .integrations/mirofish/.env, then make mirofish-start.')
