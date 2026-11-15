from pathlib import Path
import json,base64,sys
import google.auth
from google.auth.transport.requests import AuthorizedSession
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
s={}
for l in (ROOT/'.integrations/mirofish/.env').read_text().splitlines():
 if '=' in l and not l.lstrip().startswith('#'):
  k,v=l.split('=',1);s[k.strip()]=v.strip().strip('"').strip("'")
c,p=google.auth.load_credentials_from_file(s.get('GOOGLE_APPLICATION_CREDENTIALS',str(ROOT/'.integrations/vertex-service-account.json')),scopes=['https://www.googleapis.com/auth/cloud-platform']);p=s.get('VERTEX_PROJECT',p)
name=sys.argv[1] if len(sys.argv)>1 else 'demo_30s'
f=OUT/'render'/f'{name}.wav'
if not f.exists():f=OUT/f'{name}.mp3'
body={'contents':[{'role':'user','parts':[{'text':'Listen to the audio and transcribe exactly what is actually spoken. Return JSON with transcript, complete_ending (boolean), concerns (list), and segments (each sentence or short caption with start and end times in seconds, and text). Do not invent missing speech. Timestamps must match the audio. Use the first audible word as its actual time, not automatically zero.'},{'inlineData':{'mimeType':'audio/wav' if f.suffix=='.wav' else 'audio/mpeg','data':base64.b64encode(f.read_bytes()).decode()}}]}],'generationConfig':{'responseMimeType':'application/json','temperature':0}}
r=AuthorizedSession(c).post(f'https://us-central1-aiplatform.googleapis.com/v1/projects/{p}/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent',json=body,timeout=180)
if r.status_code!=200:print('Audio review HTTP',r.status_code);raise SystemExit(1)
d=r.json();result=json.loads(''.join(x.get('text','') for x in d['candidates'][0]['content']['parts']));(OUT/'render'/f'{name}_audio_review.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
