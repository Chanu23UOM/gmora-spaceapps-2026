import {chromium} from '../../.qa/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
const output=path.resolve('presentation/output');
await fs.mkdir(output+'/raw',{recursive:true});await fs.mkdir(output+'/stills',{recursive:true});
const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--font-render-hinting=none']});
const context=await browser.newContext({viewport:{width:1600,height:900},deviceScaleFactor:1,recordVideo:{dir:output+'/raw',size:{width:1600,height:900}},acceptDownloads:true});
await context.addInitScript(()=>{
 document.addEventListener('DOMContentLoaded',()=>{
  const style=document.createElement('style');style.textContent=`html{scroll-behavior:smooth}#pitch-cursor{position:fixed;width:31px;height:40px;pointer-events:none;z-index:2147483647;left:0;top:0;filter:drop-shadow(0 2px 3px #000b)}#pitch-ripple{position:fixed;width:46px;height:46px;border:2px solid #e8f4a0;border-radius:50%;pointer-events:none;z-index:2147483646;opacity:0}#pitch-ripple.active{animation:pitchClick .6s ease-out}@keyframes pitchClick{from{opacity:.9;transform:scale(.3)}to{opacity:0;transform:scale(1.2)}}#pitch-top{position:fixed;inset:0 0 auto 0;height:29px;background:#0c120fe8;border-bottom:1px solid #53644766;color:#c7d5be;z-index:2147483645;font:10px Arial,sans-serif;letter-spacing:1.5px;padding:8px 22px;display:flex;justify-content:space-between;pointer-events:none}#pitch-caption{position:fixed;bottom:17px;left:5%;right:5%;background:#0e1611ed;border:1px solid #65794c80;border-left:3px solid #e8f4a0;padding:14px 22px;color:#eff4e8;font:18px/1.4 Arial,sans-serif;z-index:2147483645;pointer-events:none;box-shadow:0 5px 22px #0004}#pitch-caption:empty{display:none}`;document.head.append(style);
  const cursor=document.createElement('div');cursor.id='pitch-cursor';cursor.innerHTML='<svg viewBox="0 0 31 40" width="31" height="40"><path d="M3 2L4 31L11 24L17 37L23 34L17 21L28 20Z" fill="#fff" stroke="#121b13" stroke-width="2"/><path d="M4 3L5 29L11 22" fill="none" stroke="#e8f4a0" stroke-width="2"/></svg>';document.body.append(cursor);
  const ripple=document.createElement('div');ripple.id='pitch-ripple';document.body.append(ripple);
  const top=document.createElement('div');top.id='pitch-top';top.innerHTML='<span id="pitch-chapter"></span><span id="pitch-clock"></span>';document.body.append(top);
  const caption=document.createElement('div');caption.id='pitch-caption';document.body.append(caption);
  document.addEventListener('mousemove',e=>{cursor.style.transform=`translate(${e.clientX}px,${e.clientY}px)`;});
  document.addEventListener('mousedown',e=>{ripple.style.left=(e.clientX-20)+'px';ripple.style.top=(e.clientY-20)+'px';ripple.classList.remove('active');void ripple.offsetWidth;ripple.classList.add('active');});
  window.__pitch=(data)=>{document.getElementById('pitch-chapter').textContent=data.chapter;caption.textContent=data.caption||'';window.__pitchEpoch=data.epoch;};
  setInterval(()=>{if(window.__pitchEpoch){let s=Math.max(0,Math.floor((Date.now()-window.__pitchEpoch)/1000));document.getElementById('pitch-clock').textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')+' / 10:00';}},200);
 });
});
const page=await context.newPage();const errors=[];const log=[];const downloads=[];
page.on('pageerror',e=>{errors.push(e.message);console.error('PAGE ERROR',e.message);});
page.on('download',async d=>{const name=d.suggestedFilename();await d.saveAs(output+'/'+name);downloads.push(name);console.log('DOWNLOAD',name);});
let epoch=Date.now();let chapter='';let caption='';let mouse={x:90,y:760};
async function overlay(){await page.evaluate(d=>window.__pitch?.(d),{chapter,caption,epoch:epoch-380000});}
async function move(x,y,ms=650){const n=32;const start={...mouse};for(let i=1;i<=n;i++){await page.mouse.move(start.x+(x-start.x)*i/n,start.y+(y-start.y)*i/n);await page.waitForTimeout(ms/n);}mouse={x,y};}
async function reveal(selector){const el=page.locator(selector).first();const tab=await el.evaluate(el=>el.closest('[role=tabpanel]')?.getAttribute('aria-labelledby'));if(tab && !(await el.isVisible()))await click('#'+tab);}
async function point(selector){await reveal(selector);await page.locator(selector).first().scrollIntoViewIfNeeded();const b=await page.locator(selector).first().boundingBox();if(!b)throw Error('No bounding box: '+selector);await move(b.x+b.width/2,b.y+b.height/2);}
async function click(selector){await point(selector);await page.waitForTimeout(250);await page.mouse.click(mouse.x,mouse.y);}
async function scroll(selector){await reveal(selector);const target=await page.locator(selector).first().evaluate(el=>el.getBoundingClientRect().top+scrollY-90);let now=await page.evaluate(()=>scrollY);const delta=target-now;await move(1480,500,300);for(let i=0;i<8;i++){await page.mouse.wheel(0,delta/8);await page.waitForTimeout(95);}await page.waitForTimeout(650);}
async function select(selector,value){await click(selector);await page.keyboard.press('Home');const i=await page.locator(selector).evaluate((el,v)=>Array.from(el.options).findIndex(o=>o.value===v),value);if(i<0)throw Error('Unknown option '+value);for(let n=0;n<i;n++)await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');await page.waitForTimeout(1100);}
async function stage(scene){await page.goto('http://127.0.0.1:8766/?scene='+scene);await page.waitForSelector('html[data-ready=true]');await page.evaluate(()=>document.fonts.ready);await overlay();await move(75,760,250);}
async function app(){await page.goto('http://127.0.0.1:8765');await page.waitForSelector('#app:not([hidden])');await page.waitForSelector('#map circle',{state:'attached'});await page.evaluate(()=>document.fonts.ready);await overlay();await move(90,740,250);}
async function at(second,label,fn,subtitle){const wait=epoch+(second-380)*1000-Date.now();if(wait>0)await page.waitForTimeout(wait);if(label){chapter=label;caption=subtitle||'';}if(fn)await fn();await overlay();const elapsed=(Date.now()-epoch)/1000;log.push({target:second,elapsed,label:label||chapter});console.log('CUE',second,label||chapter,'actual',elapsed.toFixed(1));}
try{
 await stage('historical');epoch=Date.now();chapter='11 / HISTORICAL BACKEND EVALUATION';await overlay();
 await at(380,null,async()=>{});
 await at(396,null,()=>point('.grid .card:nth-child(1)'));
 await at(411,null,()=>point('#skill-2023'));
 await at(425,null,async()=>{await point('#skill-2024');await page.screenshot({path:output+'/stills/historical-results.png'});});
 await at(440,'12 / OPEN A COMPLETED CLOUD RUN',async()=>{await app();await scroll('#scenario-title');},'Recorded run results: this opens an existing completed scenario; it does not start a new cloud run.');
 await at(451,null,async()=>{await select('#scenario-policy','independent');await click('#scenario-rounds');await page.keyboard.press('Control+A');await page.keyboard.type('1');await click('#scenario-replicate');await page.keyboard.press('Control+A');await page.keyboard.type('201');});
 await at(462,null,async()=>{await click('#scenario-form button[type=submit]');await page.waitForFunction(()=>document.getElementById('scenario-summary').textContent.includes('completed'));await scroll('#scenario-detail');});
 await at(472,null,async()=>{assert.equal(await page.locator('#scenario-start').isDisabled(),true);await click('#scenario-report');await page.screenshot({path:output+'/stills/completed-scenario.png'});});
 await at(480,'13 / TEST THE SIMULATION TOO',()=>stage('study'));
 await at(493,null,()=>point('#reports'));
 await at(507,null,()=>point('#pairs'));
 await at(520,'14 / WHY THIS WORKFLOW MATTERS',()=>stage('uniqueness'));
 await at(538,null,()=>point('.flow'));
 await at(555,'15 / THE NEXT VALIDATION MILESTONES',()=>stage('roadmap'));
 await at(575,'16 / OUR ASK',()=>stage('close'));
 await at(588,null,()=>page.screenshot({path:output+'/stills/closing.png'}));
 await at(600,null,async()=>{});
 await fs.writeFile(output+'/tail-recording-log.json',JSON.stringify({epoch,duration_target:600,events:log,downloads,page_errors:errors,source:'Real Playwright browser interaction; pitch-only cards labeled separately'},null,2));
 const video=page.video();await context.close();const videoPath=await video.path();await fs.writeFile(output+'/tail-raw-video-path.txt',videoPath);console.log('VIDEO',videoPath);assert.deepEqual(errors,[]);
}catch(error){await page.screenshot({path:output+'/recording-failure.png'}).catch(()=>{});await fs.writeFile(output+'/tail-recording-error.txt',String(error.stack));console.error(error);await context.close().catch(()=>{});process.exitCode=1;}
await browser.close();
