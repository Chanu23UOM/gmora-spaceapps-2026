"""Build the PyroSync pitch from repository evidence; no invented survey results."""
from pathlib import Path
import json, math, copy, csv, re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
EVAL = json.loads((ROOT/'processed_data/evaluation_summary.json').read_text())
HIST = json.loads((ROOT/'processed_data/evaluations/forecast_v2.json').read_text())
POLICY = json.loads((ROOT/'processed_data/evaluations/policy_study.json').read_text())
DARK='12291F'; PANEL='1C372A'; GREEN='245442'; LIME='D6EB91'; PAPER='F5F4EC'; INK='19392B'; MUTED='52675C'; SOFT='DEE5D7'; ORANGE='E4895D'; LIGHT='B6C9B8'; WHITE='FFFFFF'
prs=Presentation(); prs.slide_width=Inches(13.333333); prs.slide_height=Inches(7.5)
prs.core_properties.title='PyroSync — Clearer evidence. Stronger decisions.'
prs.core_properties.subject='10-minute pitch · Team Gmora · NASA Space Apps'
prs.core_properties.author='Team Gmora'
prs.core_properties.keywords='PyroSync, NASA FIRMS, fire observations, research, Team Gmora'
GUIDE=[]; CLAIMS=[]

def col(x): return RGBColor.from_string(x)
def rect(s,x,y,w,h,fill,line=None,radius=False):
 sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
 sh.fill.solid();sh.fill.fore_color.rgb=col(fill);sh.line.fill.background() if line is None else None
 if line: sh.line.color.rgb=col(line); sh.line.width=Pt(1)
 if radius:
  try:sh.adjustments[0]=.08
  except:pass
 return sh

def ellipse(s,x,y,w,h,fill=None,line=None,width=1):
 sh=s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
 if fill:sh.fill.solid();sh.fill.fore_color.rgb=col(fill)
 else:sh.fill.background()
 if line: sh.line.color.rgb=col(line);sh.line.width=Pt(width)
 else:sh.line.fill.background()
 return sh

def txt(s,text,x,y,w,h,size=24,color=INK,bold=False,font='Inter',align=None):
 box=s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h));tf=box.text_frame
 tf.clear();tf.word_wrap=True;tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0
 for i,line in enumerate(text.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=col(color)
  p.space_after=Pt(0);p.space_before=Pt(0);p.line_spacing=1.08
  if align is not None:p.alignment=align
 return box

def line(s,x,y,w,color=SOFT,width=1):
 sh=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x+w), Inches(y));sh.line.color.rgb=col(color);sh.line.width=Pt(width);return sh

def tag(s,text,x=.8,y=.55,dark=False):return txt(s,text,x,y,11.7,.35,18,LIME if dark else GREEN,True)
def title(s,text,dark=False,size=42):return txt(s,text,.8,1.02,11.8,1.4,size,PAPER if dark else INK,True)
def base(dark=False):
 s=prs.slides.add_slide(prs.slide_layouts[6]); s.background.fill.solid();s.background.fill.fore_color.rgb=col(DARK if dark else PAPER); return s

def notes(s,timing,script,sources=(),detail=''):
 n='TIMING: '+timing+'\n\nSPOKEN SCRIPT\n'+script+'\n\nEVIDENCE / PRESENTER NOTES\n'+detail+'\n'+'\n'.join(str(x) for x in sources)
 s.notes_slide.notes_text_frame.text=n
 GUIDE.append({'slide':len(prs.slides),'timing':timing,'script':script,'sources':list(sources),'detail':detail})

def claim(name,value,source):CLAIMS.append({'claim':name,'value':value,'source':source})
def arrow(s,x,y,w=.6,color=GREEN):
 sh=s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(.28));sh.fill.solid();sh.fill.fore_color.rgb=col(color);sh.line.fill.background()

def globe(s,x,y,d):
 ellipse(s,x,y,d,d,None,GREEN,1.2)
 for f in [.35,.68]:ellipse(s,x+d*(1-f)/2,y,d*f,d,None,GREEN,1)
 for f in [.36,.7]:ellipse(s,x,y+d*(1-f)/2,d,d*f,None,GREEN,1)
 for a,b,c in [(.25,.31,LIME),(.49,.19,ORANGE),(.65,.45,LIME),(.38,.66,ORANGE),(.73,.7,LIME),(.28,.48,LIME),(.56,.8,ORANGE)]:
  ellipse(s,x+a*d-.055,y+b*d-.055,.11,.11,c)

scripts=[
'''Imagine you are responsible for watching fire activity in your country. One satellite gives you a number. Another gives you a number eight times higher. Which one should you use? Has fire activity increased? Is one satellite seeing smaller sources of heat? Or are the instruments simply measuring things differently? Before you decide what to do, you need to understand what those numbers mean. That is the problem we are working on. Good morning. We are Team Gmora, and our product is PyroSync. PyroSync helps people compare satellite fire observations, understand the differences, and follow the evidence behind the numbers. Our idea is simple: better decisions begin with a clearer picture of what we actually know.''',
'''We started with NASA satellite data from Sri Lanka and Argentina. In our Sri Lanka files for 2025, MODIS recorded 684 observations. VIIRS on the Suomi-NPP satellite recorded 5,519. That is about eight times as many observations of the same country during the same year. But it does not mean there were eight times as many fires. Different instruments see different levels of detail. They pass over places at different times. The same burning area may appear in several observations. Some heat sources may also come from industrial activity. If we put all those numbers into a chart without explaining them, the chart can tell a misleading story. For someone studying fire patterns or preparing a report, that difference matters. A number is only useful when we understand what it counts.''',
'''PyroSync brings these observations into one place and gives people a clear way to explore them. We organise the land into small grid cells. When a cell has at least one vegetation fire detection that passes our checks on a given day, we count that cell once for that day. We call this an active cell-day. Think of it as marking a square on a calendar: this place had recorded activity on this day. If several satellites observe that same cell that day, we keep their source details, while counting the cell-day once. This gives us a shared counting rule. It does not tell us the exact number of separate fires. But it makes the comparison clearer, and it gives users a definition they can check.''',
'''Let me show you how that works. This is our burning activity calendar. Each day gives us a quick view of the activity recorded in our data. We can select a month and explore it in more detail. We can also switch between raw observation counts and active cell-days. That lets us see how the picture changes when we change the way we count. Next, we open the map. We can select an area and inspect which satellite sources contributed to it. Instead of stopping at a coloured dot, the user can ask: where did this result come from? PyroSync keeps that connection between the picture and the evidence.''',
'''Imagine an analyst preparing a monthly report. They see a rise in recorded activity and need to explain it. With PyroSync, they can compare the sources, inspect the locations, and check the original observation details. They can also view static heat sources separately, so those sources are not silently mixed into the vegetation activity count. Then they can download the data and an evidence brief to share with their team. The same workflow works for Argentina. That matters because the differences between instruments are not the same everywhere. Our two countries already show different observation ratios. A single rule that multiplies every number by the same amount would hide those differences. PyroSync helps the analyst investigate them and explain the result with evidence.''',
'''We also built tools to challenge our own results. For example, what happens if we remove one satellite source? How much recorded activity remains? That helps us understand how much the combined record depends on each source. We can also change the grid size and the confidence filters, then see how the results change. These checks matter because every method involves choices. If a small change in our method produces a large change in the answer, the user should be able to see it. We apply the same thinking to quiet days. A day with no recorded detections does not prove that no fire happened. Clouds or gaps in observation may affect what satellites see. PyroSync makes room for that uncertainty.''',
'''We also explore a practical question: can past recorded activity help us estimate the next seven days? To test that, we compare forecasting models with simple methods, such as using last week’s values. We choose the models using earlier data, then test them on later periods they have not seen. Our historical work covers almost three million source records from 2020 to 2024. In Argentina, our selected model reduced average forecast error by about 19 percent in the 2023 test and 32 percent in the 2024 test, compared with using last week’s values. Those are promising research results. Sri Lanka’s results were less conclusive, and both models in our original 2025 experiment failed our checks for moving forward. We report those outcomes too.''',
'''There is another part of the problem: how people communicate about the evidence. A team may have useful data and still struggle to produce a clear, shared update. Our experimental MiroFish lab explores that question through AI-generated discussions between fictional stakeholder roles. It lets us explore separate updates and a coordinated bulletin using the same observation workload. This is a practice exercise. It does not predict how real people will behave. Our first study produced seven completed reports, but the AI did not keep the intended roles consistent across the comparisons. So we cannot yet say which communication approach works better. That gives us a clear next step: keep the roles fixed and have independent experts review the outputs. Generated discussion stays separate from our verified data.''',
'''The people we want to help include fire analysts, researchers, environmental teams, and people preparing public information. For them, the value is practical. They can compare observations, investigate a surprising result, explain their method, and share the supporting evidence. Today, we have a working research prototype with a 2025 dashboard for Sri Lanka and Argentina, supported by earlier historical experiments. Our next step is to work with real users and domain experts. We want to learn which questions take them the most time, which parts of the interface need to be simpler, and what evidence they need before trusting a result. We also need better information about where satellites had a clear chance to observe. That will help us make stronger comparisons.''',
'''At the start, we asked a simple question. If one satellite records eight times more observations, what does that actually mean? PyroSync gives people a way to investigate the answer. They can compare the sources. They can follow the evidence. They can test the assumptions. And they can see when a forecast has not yet earned their trust. Our long-term vision is to make satellite fire records easier to understand and compare as instruments change over time. Our ask today is for the chance to validate this work with fire analysts, researchers, and emergency planning teams. Because the people making important decisions deserve information they can understand, question, and explain. We are Team Gmora. This is PyroSync. Clearer evidence. Stronger decisions. Thank you.'''
]

# 01 — Cover / simple hook.
s=base(True);tag(s,'TEAM GMORA',dark=True)
txt(s,'PyroSync',.8,1.55,8,1.0,64,PAPER,True)
txt(s,'Clearer evidence.\nStronger decisions.',.8,2.95,8,1.8,44,LIME,True)
txt(s,'Make satellite fire observations\neasier to compare and explain.',.83,5.35,7.3,1.0,26,LIGHT)
globe(s,8.8,1.65,3.6)
notes(s,'00:00–01:00',scripts[0],['README.md','docs/ARCHITECTURE_REVIEW.md'],'Pause after the opening question. Do not imply operational warning capability.')

# 02 — Data-driven problem, honest zero-based bars.
s=base();tag(s,'THE PROBLEM · SRI LANKA, 2025');title(s,'Same country.\nVery different numbers.')
raw={}
for key,path in [('modis','modis/2025'),('viirs-snpp','viirs-snpp/2025')]:
 files=list((ROOT/path).glob('*_Sri_Lanka.csv'));assert len(files)==1
 with files[0].open() as f:raw[key]=sum(1 for _ in csv.DictReader(f))
assert raw=={'modis':684,'viirs-snpp':5519}
for i,(label,n,color) in enumerate([('MODIS',raw['modis'],GREEN),('VIIRS S-NPP',raw['viirs-snpp'],GREEN)]):
 y=3.05+i*1.35;txt(s,label,.82,y,3,.4,24,INK,True)
 rect(s,3.7,y+.02,5.25*n/5519,.48,color)
 txt(s,f'{n:,}',3.7,y+.59,5.3,.55,32,INK,True)
rect(s,10.15,2.8,2.4,2.9,LIME,radius=True)
txt(s,'8.07×',10.35,3.18,2.0,.75,42,INK,True)
txt(s,'as many\nobservations',10.35,4.12,2.0,1.05,23,INK)
line(s,.8,6.23,11.7)
txt(s,'More observations ≠ more separate fires.',.8,6.48,11.7,.5,27,INK,True)
notes(s,'01:00–02:00',scripts[1],['modis/2025/*_Sri_Lanka.csv','viirs-snpp/2025/*_Sri_Lanka.csv'],'Raw rows, all types. Ratio is S-NPP VIIRS only divided by Terra/Aqua MODIS, not both VIIRS streams. The bar axis starts at zero; maximum 5,519.')
claim('Sri Lanka 2025 MODIS raw rows',684,'modis/2025/*_Sri_Lanka.csv');claim('Sri Lanka 2025 S-NPP raw rows',5519,'viirs-snpp/2025/*_Sri_Lanka.csv')

# 03 — Visual counting explanation.
s=base();tag(s,'THE IDEA');title(s,'One place. One day.\nOne shared count.')
for i,(label,c) in enumerate([('MODIS',GREEN),('VIIRS S-NPP',GREEN),('VIIRS NOAA-20',GREEN)]):
 y=3.05+i*.68;ellipse(s,.9,y+.08,.18,.18,c);txt(s,label,1.25,y,3.3,.45,24,INK)
arrow(s,4.2,3.9,.7)
for q,r in [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)]:
 x=5.25+q*.64+(r%2)*.32;y=3.1+r*.62
 sh=s.shapes.add_shape(MSO_SHAPE.HEXAGON, Inches(x), Inches(y), Inches(.77), Inches(.68));sh.fill.solid();sh.fill.fore_color.rgb=col(LIME if (q,r)==(1,1) else SOFT);sh.line.color.rgb=col(PAPER);sh.line.width=Pt(2)
txt(s,'Same cell + same day',4.85,4.8,3.4,.6,22,INK,True,align=PP_ALIGN.CENTER)
arrow(s,8.2,3.9,.7)
txt(s,'1',9.4,2.75,2,.95,78,GREEN,True,align=PP_ALIGN.CENTER)
txt(s,'active cell-day',9.0,4.2,3.3,.6,27,INK,True,align=PP_ALIGN.CENTER)
rect(s,.8,6.05,11.7,.75,DARK,radius=True);txt(s,'A shared counting rule. Source details stay attached.',1.05,6.23,11.2,.4,24,PAPER)
notes(s,'02:00–03:00',scripts[2],['docs/ARCHITECTURE_REVIEW.md','pyrosync/pipeline.py'],'Concept illustration. Active cell-day = at least one qualifying presumed-vegetation detection in an H3 resolution-8 cell on a UTC day. Cell-days are not distinct incidents or burned area.')

# 04 — Real dashboard crops, with large slide-native labels.
s=base(True);tag(s,'THE WORKING PRODUCT',dark=True);title(s,'A full year. A clear place to start.',True,40)
txt(s,'Sri Lanka · 2025 activity calendar',.85,2.32,6.6,.45,24,LIME,True)
s.shapes.add_picture(str(OUT/'assets/live-calendar.png'), Inches(.8), Inches(3.0), width=Inches(6.6))
txt(s,'August · Sri Lanka',7.9,2.32,4.8,.45,24,LIME,True)
s.shapes.add_picture(str(OUT/'assets/live-map.png'), Inches(7.9), Inches(2.98), width=Inches(4.6))
for x,num,label in [(.85,'01','Select a month'),(4.8,'02','Inspect an area'),(8.8,'03','Trace the source')]:
 txt(s,num,x,6.0,1,.5,24,LIME,True);txt(s,label,x,6.48,3.9,.5,24,PAPER,True)
notes(s,'03:00–04:00',scripts[3],['web_app/index.html','web_app/data/Sri_Lanka.json','web_app/data/Sri_Lanka_2025-08_map.json'],'Screenshots captured from the real local dashboard, August 2025. Map dots aggregate resolution-8 cell-days into resolution-7 parent cells; they are not incident boundaries. Use the dashboard live if convenient. Slide-native labels remain readable; embedded UI is visual evidence, not text to read aloud.')

# 05 — Capability comparison, no invented user performance.
s=base();tag(s,'THE USER VALUE');title(s,'Help an analyst explain the result.')
rect(s,.8,2.52,5.6,.62,SOFT);rect(s,6.58,2.52,5.93,.62,GREEN)
txt(s,'Starting with separate files',1.03,2.66,5.1,.4,23,INK,True);txt(s,'With PyroSync',6.82,2.66,5.3,.4,23,PAPER,True)
rows=[('Separate sensor counts','One shared counting rule'),('A point on a map','Source rows and timestamps'),('Numbers to copy into a report','Data and a brief to download')]
for i,(a,b) in enumerate(rows):
 y=3.42+i*.93;txt(s,a,1.03,y,5.1,.7,23,MUTED);txt(s,b,6.82,y,5.3,.7,23,INK,True);line(s,.8,y+.73,11.7)
txt(s,'Compare → inspect → explain → share',.83,6.45,11.5,.6,28,GREEN,True)
notes(s,'04:00–05:00',scripts[4],['README.md','web_app/index.html'],'This is a comparison of implemented capabilities with starting from separate CSV files, not a measured usability study, a competitor benchmark, or a claim of faster task completion.')

# 06 — Quantitative sensor-removal stress test.
s=base();tag(s,'CHALLENGE THE RESULT');title(s,'What changes when\na sensor is removed?',size=40)
txt(s,'Share of recorded cell-days retained · Sri Lanka, 2025',.83,2.62,11.7,.45,22,MUTED)
labels={'modis':'Remove MODIS','viirs-snpp':'Remove S-NPP','viirs-jpss1':'Remove NOAA-20'}
for i,r in enumerate(EVAL['Sri_Lanka']['sensor_dropout']):
 y=3.5+i*.83;txt(s,labels[r['removed']],.83,y,3.4,.45,24,INK,True)
 rect(s,4.45,y+.02,5.7,.35,SOFT);rect(s,4.45,y+.02,5.7*r['retained_fraction'],.35,GREEN)
 txt(s,f"{r['retained_fraction']*100:.1f}%",10.5,y-.12,2.0,.62,34,GREEN,True)
 claim('Sri Lanka retained after removing '+r['removed'],r['retained_fraction'],'processed_data/evaluation_summary.json#/Sri_Lanka/sensor_dropout')
rect(s,.8,6.24,11.7,.65,LIME,radius=True);txt(s,'Source dependence is visible, so users can question it.',1.03,6.38,11.2,.45,23,INK,True)
notes(s,'05:00–06:00',scripts[5],['processed_data/evaluation_summary.json#/Sri_Lanka/sensor_dropout','docs/EVALUATION_PROTOCOL.md'],'Each source stream is removed and the annual active-cell-day union is recomputed. Bars start at zero and have a 100% maximum. This measures observation redundancy, not the proportion of true fires recovered. Full grid/confidence sensitivity appears in appendix A2.')

# 07 — Forecast evidence, with honest scope and zero-based actual MAE bars.
s=base(True);tag(s,'THE RESEARCH RESULTS · ARGENTINA',dark=True);title(s,'A forecast has to earn its place.',True,40)
txt(s,'Seven-day forecasts · average error · lower is better',.83,2.2,11.7,.45,22,LIGHT)
a=next(c for c in HIST['countries'] if c['country']=='Argentina')
for i,f in enumerate(a['outer_folds']):
 x=.83+i*6.04;y=3.0
 baseline=next(r for r in f['results'] if r['model']=='last_week')['test']['mae'];selected=next(r for r in f['results'] if r['model']==f['selected_model'])['test']['mae']
 txt(s,str(f['test_year']),x,y,1.5,.5,26,PAPER,True)
 txt(s,f"{100*f['MAE_skill']:.1f}%",x+2.8,y-.12,2.9,.75,43,LIME,True)
 txt(s,'less error',x+2.85,y+.63,2.6,.45,22,LIGHT)
 for j,(lab,v,c) in enumerate([('Last week',baseline,LIGHT),('Selected model',selected,LIME)]):
  by=y+1.42+j*.82;txt(s,lab,x,by,3.0,.35,20,PAPER)
  rect(s,x,by+.38,4.6*v/450,.22,c);txt(s,f'{v:.1f}',x+4.7,by+.12,1.0,.5,25,PAPER,True)
 claim('Argentina '+str(f['test_year'])+' MAE reduction vs last_week',f['MAE_skill'],'processed_data/evaluations/forecast_v2.json')
line(s,.83,6.17,11.7,GREEN)
txt(s,'Sri Lanka: gains remain inconclusive.',.83,6.4,8.9,.45,25,PAPER,True)
notes(s,'06:00–07:00',scripts[6],['processed_data/evaluations/forecast_v2.json','experiments/forecast-v2.json','docs/BACKEND_RESEARCH.md'],'Forecast target is recorded quality-filtered active-cell counts, not ignition probability. Both Argentina folds passed an exploratory screening gate, not operational validation. Earlier years select ridge; a separate earlier year calibrates intervals; test years are 2023 and 2024. All bars share a zero baseline and scale 0–450 active cells/day MAE. Sri Lanka improvements are inconclusive. Both original 2025 country selections failed promotion; see appendix A1.')

# 08 — Honest AI experiment outcome.
s=base();tag(s,'THE AI COMMUNICATION LAB');title(s,'Can teams turn evidence\ninto a clearer update?',size=40)
rect(s,.83,3.0,5.5,2.55,SOFT,radius=True)
txt(s,'Separate updates',1.1,3.27,4.9,.5,26,INK,True)
for x in [1.15,2.18,3.21]:
 ellipse(s,x,4.1,.32,.32,GREEN);rect(s,x-.1,4.5,.52,.38,GREEN,radius=True)
arrow(s,4.28,4.25,.6);txt(s,'Shared\nbulletin',5.0,4.1,1.15,1.0,21,INK,True)
txt(s,'7',7.05,2.9,1.4,1.0,68,GREEN,True);txt(s,'reports\ncompleted',8.7,3.13,3.6,1.0,26,INK)
txt(s,'0',7.05,4.2,1.4,1.0,68,ORANGE,True);txt(s,'valid comparison\npairs',8.7,4.42,3.8,1.0,26,INK)
txt(s,'Roles changed between runs.\nNo winning policy claimed.',.83,6.05,11.7,.95,26,INK,True)
notes(s,'07:00–08:00',scripts[7],['processed_data/evaluations/policy_study.json','docs/BACKEND_RESEARCH.md'],'Synthetic MiroFish communication exercise, not physical fire prediction. Eight amended study attempts, seven completed reports, one prevented due to excessive prepared personas. Zero pairs maintained the intended four role identities. Two earlier setup runs excluded. Independent domain review pending. The visual depicts the policy comparison concept, not an observed successful coordination outcome.')
assert sum(r['phase']=='completed' for r in POLICY['runs'])==7
assert sum(c['eligible_pairs'] for c in POLICY['comparisons'])==0
claim('Completed amended-study reports',7,'processed_data/evaluations/policy_study.json#/runs');claim('Eligible policy comparison pairs',0,'processed_data/evaluations/policy_study.json#/comparisons')

# 09 — User validation is a next step, not fictional survey evidence.
s=base();tag(s,'THE NEXT STEP');title(s,'Built. Tested.\nReady for real users.')
for x,num,head,body in [(.83,'01','Work with analysts','Test clear questions\nwith real users.'),(4.86,'02','Improve coverage','Add cloud and\nobservation information.'),(8.89,'03','Review the AI lab','Keep roles fixed.\nBring in experts.')]:
 line(s,x,3.2,3.48,GREEN,3);txt(s,num,x,3.55,1,.6,26,GREEN,True);txt(s,head,x,4.38,3.5,.92,28,INK,True);txt(s,body,x,5.65,3.5,1.0,23,MUTED)
notes(s,'08:00–09:00',scripts[8],['docs/EVALUATION_PROTOCOL.md#ui-ab-protocol-designed-not-run','docs/BACKEND_RESEARCH.md'],'No participant survey, usability study, agency adoption, or operational benefit has been demonstrated. The user-study plan measures interpretation correctness, errors, completion time, and usability. No invented satisfaction percentages or sample sizes. Appendix A4 explains the planned study.')

# 10 — Clear close, one ask.
s=base(True);tag(s,'PYROSYNC · TEAM GMORA',dark=True)
txt(s,'Clearer evidence.\nStronger decisions.',.8,1.55,11.5,2.0,56,PAPER,True)
line(s,.85,4.12,1.15,LIME,4)
txt(s,'Help us validate PyroSync\nwith fire analysts and researchers.',.83,4.65,11.7,1.4,32,LIME,True)
txt(s,'Compare. Trace. Test.',.85,6.35,10,.55,27,LIGHT)
notes(s,'09:00–10:00',scripts[9],['README.md','docs/BACKEND_RESEARCH.md'],'Look at the audience. Pause between compare, trace, and test. End on the ask; do not promise live warnings or existing agency customers.')

# A1 — Complete forecast results, separate historical and 2025 experiments.
s=base();tag(s,'A1 · FORECAST EVIDENCE');title(s,'Promising results. Clear limits.',size=40)
headers=[('Test',.83,2.2),('Sri Lanka',4.2,2.2),('Argentina',8.35,2.2)]
for t,x,y in headers:txt(s,t,x,y,3.9,.5,25,GREEN,True)
for i,year in enumerate([2023,2024]):
 y=3.05+i*1.02;txt(s,str(year),.83,y,3,.5,27,INK,True)
 for c,x in [('Sri_Lanka',4.2),('Argentina',8.35)]:
  co=next(v for v in HIST['countries'] if v['country']==c);f=next(f for f in co['outer_folds'] if f['test_year']==year)
  txt(s,f"{f['MAE_skill']*100:+.1f}%",x,y,3.7,.5,29,INK,True)
  txt(s,'Exploratory gate passed' if f['promotion_passed'] else 'Inconclusive',x,y+.51,3.9,.4,20,GREEN if f['promotion_passed'] else MUTED)
 line(s,.83,y+.94,11.7)
txt(s,'2025 Q4',.83,5.35,3,.55,25,INK,True)
for c,x in [('Sri_Lanka',4.2),('Argentina',8.35)]:
 b=EVAL[c]['benchmark'];txt(s,f"{b['skill_vs_last_week']*100:+.1f}%",x,5.35,3.7,.5,29,INK,True);txt(s,'Promotion gate failed',x,5.87,3.9,.4,20,MUTED)
txt(s,'Percent reduction in average error versus last week. Research only.',.83,6.72,11.7,.4,20,INK)
notes(s,'APPENDIX · Q&A only','Use this table to distinguish historical results from the original 2025 dashboard experiment. Positive values mean lower average absolute error than last week. Sri Lanka is not promoted despite positive historical point estimates.', ['processed_data/evaluations/forecast_v2.json','processed_data/evaluation_summary.json'],'2023/2024 use frozen historical outer folds. 2025 uses October–December holdout and pre-July model choice. These experiments have separate evaluation windows. MAE reduction = 1 − selected MAE / baseline MAE. No post-hoc reselection.')

# A2 — Grid sensitivity, actual paired data table.
s=base();tag(s,'A2 · METHOD SENSITIVITY');title(s,'The counting choices change the total.',size=38)
txt(s,'Sri Lanka · 2025 recorded active cell-days',.83,2.14,11.7,.5,23,MUTED)
for x,t,w in [(.83,'Grid resolution',3.7),(4.95,'Quality filter on',3.5),(9.0,'All confidence',3.5)]:txt(s,t,x,3.0,w,.5,24,GREEN,True)
for i,res in enumerate([7,8,9]):
 y=3.85+i*.78
 txt(s,str(res)+('  ·  default' if res==8 else ''),.83,y,3.7,.5,25,INK,True)
 for q,x in [(True,4.95),(False,9.0)]:
  v=next(r['active_cell_days'] for r in EVAL['Sri_Lanka']['sensitivity'] if r['resolution']==res and r['quality']==q);txt(s,f'{v:,}',x,y,3.3,.5,28,INK,True)
 line(s,.83,y+.62,11.7)
txt(s,'Finer cells can split observations across more places.',.83,6.6,11.7,.5,24,INK)
notes(s,'APPENDIX · Q&A only','Our default uses H3 resolution 8 with the quality filter enabled. Changing the grid or confidence rule changes observed totals. That sensitivity is visible instead of hidden.', ['processed_data/evaluation_summary.json#/Sri_Lanka/sensitivity'],'This is method sensitivity, not accuracy against a ground-truth inventory. Quality off still uses the intended source-type selection; it is not every raw thermal row.')

# A3 — Scope/provenance proof; no overstated global or multidecade record.
s=base(True);tag(s,'A3 · DATA AND REPRODUCIBILITY',dark=True);title(s,'A real archive. A traceable method.',True,40)
for x,big,lab in [(.83,'30','official NASA files'),(5.1,'2.97M','source records'),(9.25,'2','country cases')]:
 txt(s,big,x,2.8,3.8,1.0,52,LIME,True);txt(s,lab,x,3.95,3.5,.8,23,PAPER)
line(s,.83,5.1,11.7,GREEN)
txt(s,'2020–2024 historical experiments',.83,5.5,11.7,.6,27,PAPER,True)
txt(s,'File hashes → row checks → shared units → held-out tests',.83,6.37,11.7,.6,24,LIGHT)
notes(s,'APPENDIX · Q&A only','Historical acquisition contains 30 official country files across three sensor streams, two countries, and five years. The total is 2,966,278 source rows. The dashboard separately uses the 2025 archive.', ['processed_data/history_manifest.json','docs/BACKEND_RESEARCH.md','docs/DATA_SOURCES.md'],'Official catalog: https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt . Seven Argentina records are quarantined under explicit numeric validity rules. Source rows remain unchanged. NASA FIRMS data courtesy NASA/GSFC ESDIS. Independent project; NASA source attribution does not imply endorsement. Product data: MODIS Terra/Aqua, S-NPP VIIRS, NOAA-20 VIIRS. No validated operational warnings, burned-area estimates, or 26-year harmonized record.')
claim('Historical source rows',2966278,'docs/BACKEND_RESEARCH.md');claim('Historical input files',30,'processed_data/history_manifest.json')

# A4 — Explicit survey status and planned research rather than invented scores.
s=base();tag(s,'A4 · USER VALIDATION PLAN');title(s,'Does clearer evidence\nhelp people interpret the data?',size=39)
rect(s,.83,2.72,11.7,.7,LIME,radius=True);txt(s,'User study planned · no survey results collected yet',1.07,2.91,11.2,.4,23,INK,True)
for x,head,body in [(.83,'Compare two views','Calendar and counts\nvs. the evidence view.'),(4.86,'Use real tasks','Explain a spike.\nCheck a forecast.'),(8.89,'Measure the result','Correct answers,\ntime and usability.')]:
 txt(s,head,x,4.05,3.5,.8,26,INK,True);txt(s,body,x,5.22,3.5,1.2,23,MUTED)
notes(s,'APPENDIX · Q&A only','There are no completed participant surveys or usability trials in this repository. This is the existing planned A/B protocol, not a reported survey result.', ['docs/EVALUATION_PROTOCOL.md#ui-ab-protocol-designed-not-run'],'The plan compares calendar + raw sensor counts with the same data plus unit explanations, source agreement, and evidence inspection. Primary measure: scientifically correct answers per participant. Secondary measures: critical interpretation errors, task completion time, confidence calibration, usability. Sample size and stopping rules must be set before collecting results. No fabricated sample sizes or significance.')

# Override inherited theme effects so editable shapes stay flat and clean.
for slide in prs.slides:
 for shape in slide.shapes:
  props=shape._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
  if props is not None:
   for old in list(props):
    if old.tag.endswith('}effectLst') or old.tag.endswith('}effectDag'):props.remove(old)
   props.append(OxmlElement('a:effectLst'))

full=OUT/'PyroSync_10_Minute_Pitch.pptx';prs.save(full)

# Separate seven-slide cut for the competition limit documented in the repo.
compact=Presentation(full)
keep={1,2,3,4,7,8,10}
for idx in range(len(compact.slides)-1,-1,-1):
 if idx+1 not in keep:
  item=compact.slides._sldIdLst[idx];compact.part.drop_rel(item.rId);compact.slides._sldIdLst.remove(item)
compact.core_properties.title='PyroSync — Seven-slide submission cut'
groups=[([0],'00:00–01:00'),([1],'01:00–02:00'),([2],'02:00–03:00'),([3,4],'03:00–05:00'),([5,6],'05:00–07:00'),([7],'07:00–08:00'),([8,9],'08:00–10:00')]
for slide,(indices,timing) in zip(compact.slides,groups):
 slide.notes_slide.notes_text_frame.text='TIMING: '+timing+'\n\nSPOKEN SCRIPT\n'+'\n\n'.join(scripts[i] for i in indices)+'\n\nEVIDENCE / PRESENTER NOTES\n'+'\n\n'.join(GUIDE[i]['detail']+'\n'+'\n'.join(GUIDE[i]['sources']) for i in indices)
compact.save(OUT/'PyroSync_7_Slide_Submission.pptx')

md=['# PyroSync presenter guide','', 'The main deck has 10 pitch slides, followed by 4 evidence slides for Q&A. The seven-slide submission cut uses main slides 1, 2, 3, 4, 7, 8, and 10. It combines the analyst workflow with the product demo, the stress-test explanation with the forecast results, and the next steps with the closing ask.','', 'Speak at about 120–130 words per minute, allowing time for pauses and pointing to charts. Each slide follows the 10-minute script supplied in the conversation. Main-slide text is at least 18 pt, with 23–32 pt body text and 38–78 pt headlines or numbers. Source citations and definitions are in speaker notes, not dense footers.','', '| Slide | Time | Spoken words |','| --- | --- | ---: |']
for g in GUIDE[:10]:md.append(f"| {g['slide']} | {g['timing']} | {len(g['script'].split())} |")
for g in GUIDE:
 md += ['',f"## Slide {g['slide']} · {g['timing']}",'',g['script'],'','Presenter detail: '+g['detail'],'','Sources:']+['- '+x for x in g['sources']]
(OUT/'PyroSync_Presenter_Guide.md').write_text('\n'.join(md)+'\n')
(OUT/'evidence_manifest.json').write_text(json.dumps({'scope':'10-slide pitch plus four appendix slides; seven-slide submission cut','survey_status':'not_run','claims':CLAIMS,'slides':[{k:v for k,v in g.items() if k!='script'} for g in GUIDE]},indent=2)+'\n')
# Geometry and legibility checks for all generated slide objects.
issues=[]
for i,s in enumerate(prs.slides,1):
 for sh in s.shapes:
  if sh.left<0 or sh.top<0 or sh.left+sh.width>prs.slide_width+100 or sh.top+sh.height>prs.slide_height+100:issues.append(f'{i}: out of bounds {sh.name}')
  if sh.has_text_frame:
   for p in sh.text_frame.paragraphs:
    for r in p.runs:
     if r.font.size and r.font.size<Pt(18):issues.append(f'{i}: small text {r.text}')
assert not issues,issues
print(json.dumps({'slides':len(prs.slides),'compact_slides':len(compact.slides),'spoken_words':sum(len(x.split()) for x in scripts),'validation':'all shapes in bounds; text minimum 18 pt; raw counts verified; policy totals verified','pptx':str(full)},indent=2))
