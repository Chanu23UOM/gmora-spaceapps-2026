"""Assemble the two real browser captures into an exact 10:00 silent master."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
def run(args,log):
 with (OUT/log).open('w') as stream:subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT,check=True)
def duration(path):
 d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)]))
 return float(d['format']['duration'])
common=['-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-r','25','-threads','4','-an','-movflags','+faststart']
main_marker=OUT/'main-raw-video-path.txt'
main=Path(main_marker.read_text().strip()) if main_marker.exists() else sorted((OUT/'raw').glob('*.webm'),key=lambda p:p.stat().st_mtime)[0]
main_out=OUT/'main_380.mp4'
if not main_out.exists():
 print('Rendering main prototype recording',flush=True)
 run(['ffmpeg','-y','-hide_banner','-ss','1.0','-i',str(main),'-t','380','-vf','scale=1920:1080:flags=lanczos,fade=t=in:st=0:d=0.6',*common,str(main_out)],'render-main.log')
marker=OUT/'tail-raw-video-path.txt'
if not marker.exists():
 print('Main render complete; final capture is still running.',flush=True)
 raise SystemExit(0)
tail=Path(marker.read_text().strip());tail_out=OUT/'tail_220.mp4';offset=max(0,duration(tail)-220)
print('Rendering research and closing sequence',flush=True)
run(['ffmpeg','-y','-hide_banner','-ss',str(offset),'-i',str(tail),'-t','220','-vf','scale=1920:1080:flags=lanczos,fade=t=out:st=219:d=1',*common,str(tail_out)],'render-tail.log')
concat=OUT/'concat.txt';concat.write_text(f"file '{main_out}'\nfile '{tail_out}'\n")
final=OUT/'PyroSync_10min_Presenter.mp4'
print('Assembling final presenter master',flush=True)
run(['ffmpeg','-y','-hide_banner','-f','concat','-safe','0','-i',str(concat),'-f','ffmetadata','-i',str(OUT/'chapters.ffmeta'),'-map','0:v:0','-map_metadata','1','-map_chapters','1','-c:v','copy','-an','-movflags','+faststart',str(final)],'render-final.log')
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(final)]))
(OUT/'video-metadata.json').write_text(json.dumps(meta,indent=2))
assert abs(float(meta['format']['duration'])-600)<.1
video=next(s for s in meta['streams'] if s['codec_type']=='video')
assert (video['width'],video['height'])==(1920,1080)
assert not any(s['codec_type']=='audio' for s in meta['streams'])
print('Ready:',final,'duration',meta['format']['duration'],'bytes',final.stat().st_size,flush=True)
