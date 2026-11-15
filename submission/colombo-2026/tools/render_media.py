from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,math,wave,textwrap,re,sys
OUT=Path(__file__).resolve().parents[1];R=OUT/'render'
DARK='#12291F';LIME='#D6EB91';PAPER='#F5F4EC';LIGHT='#B6C9B8';GREEN='#245442'
FONT='/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf';BOLD='/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
def run(cmd):subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def txt(d,text,xy,size=60,color=PAPER,b=False):d.multiline_text(xy,text,font=font(size,b),fill=color,spacing=16)
def base(k):
 im=Image.new('RGB',(1920,1080),DARK);d=ImageDraw.Draw(im);txt(d,k,(110,65),32,LIME,True);return im,d
# Pixel-clean assets reserve the bottom 170px for mandatory English captions.
im,d=base('PYROSYNC  /  TEAM GMORA');txt(d,'One country.\nTwo very different counts.',(110,150),94,PAPER,True)
txt(d,'684',(110,470),140,LIME,True);txt(d,'MODIS',(115,640),44,LIGHT)
txt(d,'5,519',(950,470),140,LIME,True);txt(d,'VIIRS S-NPP',(955,640),44,LIGHT)
txt(d,'Sri Lanka · 2025 · NASA FIRMS observations',(110,800),38,LIGHT);im.save(R/'demo-scene-1.png')
im,d=base('THE IDEA');txt(d,'Make the difference\nunderstandable.',(110,150),94,PAPER,True)
for x,label in [(115,'MODIS'),(665,'VIIRS S-NPP'),(1215,'VIIRS NOAA-20')]:
 d.rounded_rectangle((x,480,x+490,600),radius=18,fill=GREEN);txt(d,label,(x+30,510),46,PAPER,True)
txt(d,'One active cell-day',(110,700),70,LIME,True);txt(d,'Same place. Same day. Source details preserved.',(110,805),38,LIGHT);im.save(R/'demo-scene-2.png')
im,d=base('THE WORKING PRODUCT');txt(d,'Follow the evidence.',(110,150),94,PAPER,True)
cal=Image.open(R/'calendar.png').convert('RGB');cal.thumbnail((980,440));im.paste(cal,(100,390))
mp=Image.open(R/'map.png').convert('RGB');mp.thumbnail((710,470));im.paste(mp,(1100,350))
txt(d,'Calendar → map → source evidence',(110,820),44,LIME,True);im.save(R/'demo-scene-3.png')
im,d=base('TEAM GMORA');txt(d,'PyroSync',(110,160),140,PAPER,True);txt(d,'Clearer evidence.\nStronger decisions.',(110,370),94,LIME,True);txt(d,'Sri Lanka + Argentina',(110,690),44,PAPER,True);txt(d,'Working research prototype',(110,790),38,LIGHT);im.save(R/'demo-scene-4.png')
# Use audio-derived timestamps when available, with a readable sentence fallback.
review=R/'demo_30s_audio_review.json';offset=1.0
if review.exists():segments=json.loads(review.read_text())['segments']
else:
 text=json.loads((OUT/'narration.json').read_text())['demo_30s'];sentences=re.findall(r'[^.!?]+[.!?]',text);weight=sum(len(t.split()) for t in sentences);t=.05;segments=[]
 with wave.open(str(R/'demo_30s.wav')) as w:duration=w.getnframes()/w.getframerate()
 for sentence in sentences:
  end=t+duration*len(sentence.split())/weight;segments.append({'start':t,'end':min(end,duration),'text':sentence.strip()});t=end

def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
srt=[]
for i,v in enumerate(segments,1):
 srt += [str(i),stamp(offset+float(v['start']))+' --> '+stamp(min(29.8,offset+float(v['end']))),'\n'.join(textwrap.wrap(v['text'].replace('Pyro sync','PyroSync').replace('pyro sync','PyroSync'),48)),'']
(OUT/'PyroSync_Demo_30s.en.srt').write_text('\n'.join(srt))
scenes=[(1,6.7),(2,6.0),(3,7.6),(4,9.7)]
for i,duration in scenes:
 run(['ffmpeg','-y','-loop','1','-i',str(R/f'demo-scene-{i}.png'),'-t',str(duration),'-r','30','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(R/f'demo-part-{i}.mp4')])
(R/'demo-concat.txt').write_text(''.join(f"file 'demo-part-{i}.mp4'\n" for i,_ in scenes))
run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(R/'demo-concat.txt'),'-i',str(R/'demo_30s.wav'),'-filter_complex',"[0:v]subtitles="+str(OUT/'PyroSync_Demo_30s.en.srt')+":force_style='FontName=Inter,FontSize=16,Outline=1,Shadow=0,BackColour=&HCC12291F,BorderStyle=3,MarginV=14',drawtext=fontfile=/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf:text='SI-assisted visuals | SI-generated voice':fontcolor=0xD6EB91:fontsize=32:x=w-tw-80:y=68:box=1:boxcolor=0x12291F@0.9:boxborderw=10[v];[1:a]adelay=1000|1000,loudnorm=I=-16:TP=-1.5:LRA=9,apad[a]",'-map','[v]','-map','[a]','-t','30','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-metadata','comment=SI-assisted visual authoring by OpenAI Codex/ChatGPT. Adult synthetic narration generated with Google Vertex AI Gemini 2.5 Pro TTS, Charon voice. NASA FIRMS observations are source data, not SI-generated data.','-metadata:s:a:0','title=SI-generated adult narration - Vertex Gemini 2.5 Pro TTS / Charon','-movflags','+faststart',str(OUT/'PyroSync_Demo_30s.mp4')])
run(['ffmpeg','-y','-i',str(R/'demo_30s.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','libmp3lame','-b:a','192k',str(OUT/'PyroSync_Demo_Voice.mp3')])
print('30-second captioned demo rendered',flush=True)
if '--demo-only' not in sys.argv and all((R/f'pitch_{i:02}.wav').exists() for i in range(1,8)):
 durations=[35,35,35,45,55,50,45]
 metadata=[]
 for i,duration in enumerate(durations,1):
  with wave.open(str(R/f'pitch_{i:02}.wav')) as w:actual=w.getnframes()/w.getframerate()
  tempo=max(1,actual/(duration-1.5));assert tempo<1.12,('Review speaking pace',i,actual)
  filt=(f'atempo={tempo},' if tempo>1 else '')+'loudnorm=I=-16:TP=-1.5:LRA=9,apad'
  run(['ffmpeg','-y','-loop','1','-i',str(R/f'slide-{i}.png'),'-i',str(R/f'pitch_{i:02}.wav'),'-t',str(duration),'-vf','scale=1920:1080','-af',filt,'-r','25','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',str(R/f'live-part-{i}.mp4')])
  metadata.append({'slide':i,'slot_seconds':duration,'generated_audio_seconds':actual,'tempo_factor':tempo})
 (R/'live-concat.txt').write_text(''.join(f"file 'live-part-{i}.mp4'\n" for i in range(1,8)))
 run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(R/'live-concat.txt'),'-t','300','-c','copy','-movflags','+faststart',str(OUT/'PyroSync_Live_Pitch_5min.mp4')])
 run(['ffmpeg','-y','-i',str(OUT/'PyroSync_Live_Pitch_5min.mp4'),'-vn','-c:a','libmp3lame','-b:a','192k',str(OUT/'PyroSync_Live_Pitch_5min.mp3')])
 (OUT/'VOICE_PROVENANCE.json').write_text(json.dumps({'provider':'Google Vertex AI','model':'gemini-2.5-pro-tts','voice':'Charon','adult_synthetic_voice':True,'style':'Warm professional documentary narration; natural conversational delivery','music':False,'human_recordings':False,'live_sections':metadata,'transcript_file':'narration.json','tts_documentation':'https://docs.cloud.google.com/text-to-speech/docs/gemini-tts'},indent=2))
 print('Five-minute narrated rehearsal rendered',flush=True)
