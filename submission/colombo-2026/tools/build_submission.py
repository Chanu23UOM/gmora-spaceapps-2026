from pathlib import Path
import json,math,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
old=ROOT/'presentation/deck/build_deck.py'
# Reuse the original deck's visual primitives without rebuilding its outputs.
ns={'__file__':str(old)};exec(compile(old.read_text().split('scripts=[')[0],str(old),'exec'),ns)
globals().update({k:v for k,v in ns.items() if not k.startswith('__')})
OUT=Path(__file__).resolve().parents[1];N=json.loads((OUT/'narration.json').read_text())
from pptx.oxml.xmlchemy import OxmlElement
# Original helper namespace owns its presentation; rebind only output-independent helpers.
P=ns['prs']; allslides=[]
def addnotes(s,n,t,extra):
 s.notes_slide.notes_text_frame.text=f'TIMING: {t}\n\n'+N[n]+'\n\nEVIDENCE\n'+extra
 allslides.append({'slide':len(P.slides),'key':n,'target_seconds':t,'script':N[n]})
# 1
s=base(True);tag(s,'TEAM GMORA · NASA SPACE APPS',dark=True)
txt(s,'PyroSync',.8,1.6,8,1.0,64,PAPER,True);txt(s,'Clearer evidence.\nStronger decisions.',.8,3,8,1.8,44,LIME,True);txt(s,'Understand the instrument.\nExplain the observation.',.83,5.4,7.5,1.0,27,LIGHT);globe(s,8.8,1.65,3.6)
addnotes(s,'pitch_01','00:00–00:35','Independent research prototype. No NASA endorsement. Evaluated upstream revision 4b39801.')
#2
s=base();tag(s,'THE PROBLEM · SRI LANKA, 2025');title(s,'Same country.\nVery different numbers.')
for i,(lab,n) in enumerate([('MODIS',684),('VIIRS S-NPP',5519)]):
 y=3.05+i*1.35;txt(s,lab,.82,y,3,.4,24,INK,True);rect(s,3.7,y+.02,5.25*n/5519,.48,GREEN);txt(s,f'{n:,}',3.7,y+.59,5.3,.55,32,INK,True)
rect(s,10.15,2.8,2.4,2.9,LIME,radius=True);txt(s,'8.07×',10.35,3.2,2,.75,42,INK,True);txt(s,'as many\nobservations',10.35,4.15,2,1,23,INK)
txt(s,'More observations ≠ more separate fires.',.8,6.48,11.7,.5,27,INK,True)
addnotes(s,'pitch_02','00:35–01:10','Raw rows in original 2025 Sri Lanka CSVs. S-NPP-only comparison, not the union of both VIIRS streams. Zero-based bars. Source: modis/2025 and viirs-snpp/2025.')
#3
s=base();tag(s,'THE METHOD');title(s,'One place. One day.\nOne shared count.')
for i,lab in enumerate(['MODIS','VIIRS S-NPP','VIIRS NOAA-20']):
 y=3.05+i*.68;ellipse(s,.9,y+.08,.18,.18,GREEN);txt(s,lab,1.25,y,3.3,.45,24,INK)
arrow(s,4.2,3.9,.7)
for q,r in [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)]:
 sh=s.shapes.add_shape(MSO_SHAPE.HEXAGON, Inches(5.25+q*.64+(r%2)*.32), Inches(3.1+r*.62), Inches(.77), Inches(.68));sh.fill.solid();sh.fill.fore_color.rgb=col(LIME if(q,r)==(1,1) else SOFT);sh.line.color.rgb=col(PAPER)
txt(s,'Same cell + same day',4.85,4.8,3.4,.6,22,INK,True,align=PP_ALIGN.CENTER);arrow(s,8.2,3.9,.7);txt(s,'1',9.4,2.75,2,.95,78,GREEN,True,align=PP_ALIGN.CENTER);txt(s,'active cell-day',9,4.2,3.3,.6,27,INK,True,align=PP_ALIGN.CENTER)
txt(s,'A shared counting rule. Source details stay attached.',.83,6.38,11.7,.55,25,INK,True)
addnotes(s,'pitch_03','01:10–01:45','H3 resolution 8, UTC days, quality-filtered vegetation detections; union across three source streams. Not incident reconstruction. Source: pyrosync/pipeline.py; docs/ARCHITECTURE_REVIEW.md.')
#4
s=base(True);tag(s,'THE WORKING PRODUCT',dark=True);title(s,'Select. Inspect. Explain. Export.',True,40)
txt(s,'Sri Lanka · 2025 calendar',.83,2.25,6.6,.5,25,LIME,True);s.shapes.add_picture(str(OUT/'render/calendar.png'), Inches(.8), Inches(3),width=Inches(6.6))
txt(s,'August · source evidence',7.9,2.25,4.7,.5,25,LIME,True);s.shapes.add_picture(str(OUT/'render/map.png'),Inches(7.9),Inches(3),width=Inches(4.6))
for x,t in [(.83,'Period brief'),(4.9,'Source row references'),(9.25,'CSV + GeoJSON')]:txt(s,t,x,6.4,3.9,.7,24,PAPER,True)
addnotes(s,'pitch_04','01:45–02:30','Screenshots from latest upstream 4b39801. Optional live path: Overview → month August → Show period brief → Explore map & sensors → mapped cell → evidence → export. Map displays aggregated units, not fire boundaries. Source: web_app/.')
#5
s=base(True);tag(s,'MEASURED RESULTS',dark=True);title(s,'Test the claim. Keep the limits.',True,40)
txt(s,'Seven-day forecasts vs. repeating last week',.83,2.15,11.7,.45,24,LIGHT)
for x,year,skill in [(.83,'Argentina · 2023','19.2%'),(6.9,'Argentina · 2024','31.9%')]:
 txt(s,year,x,2.8,5.4,.5,28,PAPER,True);txt(s,skill,x,3.55,5.4,1,62,LIME,True);txt(s,'lower average forecast error',x,4.73,5.4,.6,24,LIGHT)
line(s,.83,5.6,11.7,GREEN)
txt(s,'Sri Lanka: historical gains inconclusive.',.83,5.92,11.7,.5,25,PAPER,True);txt(s,'2025: neither country passed promotion.',.83,6.52,11.7,.5,25,PAPER,True)
addnotes(s,'pitch_05','02:30–03:25','Seven-day forecasts of recorded activity counts. Historical ridge choices selected using earlier data; 2023 and 2024 separate outer tests. Percent MAE reduction vs last-week baseline. Both Argentina folds passed exploratory gates; no operational validation. Sri Lanka +14.5%/+11.5% point estimates remain inconclusive. Original 2025 Sri Lanka −15.0%, Argentina +21.2%, both gates failed. Source: processed_data/evaluations/forecast_v2.json; processed_data/evaluation_summary.json.')
#6
s=base();tag(s,'IMPACT AND NEXT VALIDATION');title(s,'Built for people\nwho must explain the numbers.')
for x,big,lab in [(.83,'2','country cases'),(5.1,'2.97M','historical source rows'),(9.25,'3','sensor streams')]:txt(s,big,x,2.9,3.9,1,54,GREEN,True);txt(s,lab,x,4,3.8,.85,23,INK)
line(s,.83,5.15,11.7)
txt(s,'Next: analyst trials + observation coverage.',.83,5.65,11.7,.7,28,INK,True);txt(s,'AI study v2 frozen; user study not yet run.',.83,6.45,11.7,.5,24,MUTED)
addnotes(s,'pitch_06','03:25–04:15','Two country cases are Sri Lanka and Argentina, not partners/customers. 30 historical files, 2,966,278 source rows, 2020–2024; dashboard 2025. UI usability protocol preregistered, no participants or results yet. v1 AI study had seven reports but zero valid matched pairs. Upstream now rejects drift before simulation; v2 protocol frozen, not yet run; independent reviewer scores pending. Sources: docs/BACKEND_RESEARCH.md; docs/USABILITY_STUDY_PROTOCOL.md; docs/POLICY_REVIEW_RUBRIC.md; experiments/mirofish-policies-v2.json.')
#7
s=base(True);tag(s,'PYROSYNC · TEAM GMORA',dark=True);title(s,'Clearer evidence.\nStronger decisions.',True,48)
txt(s,'Help us validate with analysts\nand researchers.',.83,3.35,11.7,1.3,32,LIME,True)
line(s,.83,5.22,11.7,GREEN)
txt(s,'Built with NASA FIRMS · MODIS + VIIRS',.83,5.65,11.7,.6,25,PAPER,True)
t=txt(s,'firms.modaps.eosdis.nasa.gov',.83,6.36,11.7,.5,24,LIGHT)
# Source URL stays plain and high-contrast; the full link is in presenter notes.
addnotes(s,'pitch_07','04:15–05:00','NASA FIRMS data courtesy NASA/GSFC ESDIS. Official resource: https://firms.modaps.eosdis.nasa.gov/ . Country data: https://firms.modaps.eosdis.nasa.gov/country/ . VIIRS attributes: https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html . Other code/text/image resources in docs/DATA_SOURCES.md. AI assistance: OpenAI Codex/ChatGPT for coding, research and submission authoring; Google Gemini via Vertex AI for synthetic communication study and adult synthetic voiceover. Zep stores synthetic simulation context. No NASA marks/logos generated or modified. No names, likenesses, or human recordings included.')
for slide in P.slides:
 for sh in slide.shapes:
  props=sh._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
  if props is not None:props.append(OxmlElement('a:effectLst'))
  assert sh.left>=0 and sh.top>=0 and sh.left+sh.width<=P.slide_width+100 and sh.top+sh.height<=P.slide_height+100
P.core_properties.title='PyroSync — NASA Space Apps Colombo 2026 submission';P.save(OUT/'PyroSync_Submission_7_Slides.pptx')
(OUT/'slide_script.json').write_text(json.dumps(allslides,indent=2))
md=['# PyroSync — five-minute live pitch','', 'Seven slides. Stop at 5:00, then allow five minutes for judge questions. The 30-second video is an alternative submission demo, not the live pitch.','']
for v in allslides:md += [f"## Slide {v['slide']} · {v['target_seconds']}",'',v['script'],'']
(OUT/'LIVE_PITCH_5_MIN.md').write_text('\n'.join(md))
summary='''PyroSync helps people understand why different satellites can tell different stories about fire activity. Using NASA FIRMS observations from MODIS and VIIRS, we built a working dashboard for Sri Lanka and Argentina that combines an activity calendar, a map, source evidence, and downloadable briefs. A shared counting rule records each active grid cell once per day while preserving the observations behind it. Users can inspect sensor differences and see how results change when a source or analytical choice changes. We also evaluate seven-day forecasts against simple baselines using earlier data for model selection and later years for testing. Historical results are promising in Argentina, while Sri Lanka’s gains remain inconclusive. PyroSync is a research prototype, not a live emergency-warning service. Our goal is to help analysts compare, question, and explain satellite fire records before those records inform decisions.'''
assert 50<=len(summary.split())<=200
(OUT/'SUMMARY.txt').write_text(summary+'\n')
print('7 slides; summary',len(summary.split()),'words; live script',sum(len(v['script'].split()) for v in allslides),'words')
