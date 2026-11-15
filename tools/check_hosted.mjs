import {chromium} from '../.qa/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.PYROSYNC_AUDIT_URL||'http://127.0.0.1:8767';
const output=process.env.PYROSYNC_AUDIT_OUTPUT||'.qa/hosted-audit.json';
const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
const p=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});const checks=[];const errors=[];const bad=[];
p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)bad.push({url:r.url(),status:r.status()});});
try{
 await p.goto(base);await p.waitForSelector('#app:not([hidden])');
 for(const country of ['Sri_Lanka','Argentina']){
  await p.click('#tab-overview');await p.selectOption('#country',country);await p.waitForSelector('#app:not([hidden])');await p.selectOption('#month','2025-08');
  await p.waitForFunction(c=>document.getElementById('ctx-country').textContent===c.replaceAll('_',' '),country);
  if(await p.locator('#period-brief').isHidden())await p.click('#period-brief-toggle');
  for(const [tab,buttons] of [['overview',['#brief-period-download']],['explore',['#csv-download','#geojson-download']],['research',['#brief-download','#packet-download','#predictions-download']]]){
   await p.click('#tab-'+tab);
   for(const button of buttons){console.log('Checking',country,button);const event=p.waitForEvent('download');await p.click(button);const dl=await event;assert.equal(await dl.failure(),null);const bytes=await fs.readFile(await dl.path());assert.ok(bytes.length>20);assert.ok(!bytes.subarray(0,100).toString().toLowerCase().includes('<!doctype html>'));checks.push({country,check:'download',file:dl.suggestedFilename(),bytes:bytes.length,passed:true});}
  }
 }
 await p.click('#tab-overview');await p.selectOption('#country','Sri_Lanka');await p.waitForSelector('#app:not([hidden])');await p.click('#tab-research');await p.locator('#scenario-form button[type=submit]').click();await p.waitForSelector('#scenario-detail:not([hidden])');
 assert.match(await p.locator('#scenario-summary').innerText(),/prepared/);assert.equal(await p.locator('#scenario-start').isDisabled(),true);
 const event=p.waitForEvent('download');await p.click('#scenario-seed');const dl=await event;const state=JSON.parse(await fs.readFile(await dl.path(),'utf8'));assert.equal(state.phase,'prepared');assert.equal(state.country,'Sri_Lanka');checks.push({check:'public-scenario-prepare-and-state-download',passed:true});
 await p.reload();await p.waitForSelector('#app:not([hidden])');await p.click('#tab-research');await p.waitForSelector('#scenario-detail:not([hidden])');assert.match(await p.locator('#scenario-summary').innerText(),/prepared/);checks.push({check:'prepared-state-restored-after-reload',passed:true});
 for(const endpoint of ['/api/research','/api/mirofish']){const r=await p.request.get(base+endpoint);assert.equal(r.status(),200);assert.ok((await r.json()));checks.push({check:endpoint,passed:true});}
 assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);
 await fs.writeFile(output,JSON.stringify({tested_url:base,status:'passed',checks,page_errors:errors,failed_site_responses:bad,credentials_used:false,scope:'archive, exports, research summaries, public scenario preparation; live AI execution remains local'},null,2)+'\n');
 console.log(`${checks.length} deployment checks passed at ${base}`);
}finally{await browser.close();}
