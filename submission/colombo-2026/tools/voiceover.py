"""Generate only the approved submission narration using supplied local Vertex credentials.
Reads existing ignored configuration, never logs credentials or persists bearer tokens.
"""
from pathlib import Path
import base64,json,sys,wave,time
import google.auth
from google.auth.transport.requests import AuthorizedSession
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
def synthesize(name,text):
 target=OUT/'render'/f'{name}.wav'
 if target.exists():return
 settings={}
 for l in (ROOT/'.integrations/mirofish/.env').read_text().splitlines():
  if '=' in l and not l.lstrip().startswith('#'):
   k,v=l.split('=',1);settings[k.strip()]=v.strip().strip('"').strip("'")
 path=settings.get('GOOGLE_APPLICATION_CREDENTIALS',str(ROOT/'.integrations/vertex-service-account.json'))
 credentials,project=google.auth.load_credentials_from_file(path,scopes=['https://www.googleapis.com/auth/cloud-platform'])
 project=settings.get('VERTEX_PROJECT',project)
 url=f'https://aiplatform.googleapis.com/v1beta1/projects/{project}/locations/us-central1/publishers/google/models/gemini-2.5-pro-tts:generateContent'
 style='Speak ONLY the transcript below, verbatim. Use a mature adult professional documentary narrator voice, warm, grounded and conversational. Natural English, clear international pronunciation, confident but never theatrical or salesy. Gentle sentence rhythm, realistic brief pauses, no music or sound effects. Keep a natural but purposeful pace, 150 words per minute, without long dramatic pauses. Pronounce PyroSync as pie-roh-sink, Gmora as guh-mora, VIIRS as veers, MODIS as moh-dis. Do not speak these directions. Transcript: '
 payload={'contents':[{'role':'user','parts':[{'text':style+text}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'languageCode':'en-US','voiceConfig':{'prebuiltVoiceConfig':{'voiceName':'Charon'}}}}}
 response=AuthorizedSession(credentials).post(url,json=payload,timeout=180)
 if response.status_code!=200:
  data=response.json();print(json.dumps({'status':response.status_code,'message':data.get('error',{}).get('message','TTS error')[:500]}));raise SystemExit(1)
 data=response.json();chunks=[]
 for cand in data.get('candidates',[]):
  for p in cand.get('content',{}).get('parts',[]):
   if p.get('inlineData'):chunks.append(base64.b64decode(p['inlineData']['data']))
 if not chunks:raise RuntimeError('Vertex returned no audio')
 with wave.open(str(target),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b''.join(chunks))
 with wave.open(str(target)) as w:duration=w.getnframes()/w.getframerate()
 meta={'provider':'Google Vertex AI','model':'gemini-2.5-pro-tts','voice':'Charon','language':'en-US','adult_synthetic_voice':True,'duration_seconds':duration,'usage':data.get('usageMetadata',{}),'source_text':text}
 (OUT/'render'/f'{name}.json').write_text(json.dumps(meta,indent=2))
 print(name,round(duration,2),'seconds',flush=True)
if __name__=='__main__':
 content=json.loads((OUT/'narration.json').read_text())
 names=sys.argv[1:] or list(content)
 for n in names:synthesize(n,content[n])
