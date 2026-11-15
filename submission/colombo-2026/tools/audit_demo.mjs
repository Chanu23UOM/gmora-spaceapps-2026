// Deterministic task checks, never participant or screen-reader usability evidence.
import {chromium} from '../../../.qa/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const out=process.env.PYROSYNC_AUDIT_OUTPUT || new URL('../evidence/demo_audit.json',import.meta.url);
const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
const checks=[];const errors=[];
const page=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});
page.on('pageerror',e=>errors.push(e.message));
const base=process.env.PYROSYNC_AUDIT_URL||'http://127.0.0.1:8765';
try{
 await page.goto(base);await page.waitForSelector('#app:not([hidden])');
 for(const country of ['Sri_Lanka','Argentina']){
  await page.click('#tab-overview');await page.selectOption('#country',country);await page.selectOption('#month','2025-08');
  await page.waitForFunction(c=>document.getElementById('ctx-country').textContent===c.replaceAll('_',' '),country);
  const payload=await page.evaluate(async c=>(await fetch(`data/${c}.json`)).json(),country);
  const days=payload.daily.filter(d=>d.date.startsWith('2025-08'));const raw=days.reduce((s,d)=>s+d.raw,0);const cells=days.reduce((s,d)=>s+d.active_cells,0);
  assert.equal((await page.locator('#stat-raw').innerText()).replaceAll(',',''),String(raw));
  assert.equal((await page.locator('#stat-cells').innerText()).replaceAll(',',''),String(cells));
  checks.push({country,check:'selected-country-and-month-counts',passed:true,raw,active_cell_days:cells});
  const monthly={};for(const d of payload.daily)monthly[d.date.slice(0,7)]=(monthly[d.date.slice(0,7)]||0)+d.active_cells;
  const peak=Object.entries(monthly).sort((a,b)=>b[1]-a[1])[0][0];
  const expected=new Date(peak+'-01').toLocaleString('en',{month:'long',timeZone:'UTC'});
  assert.match(await page.locator('#stat-peak').innerText(),new RegExp(expected.slice(0,3),'i'));
  checks.push({country,check:'peak-month-agrees-with-data',passed:true,peak_month:peak});
  if(await page.locator('#period-brief').isHidden())await page.click('#period-brief-toggle');
  const brief=await page.locator('#brief-body').innerText();assert.match(brief,/active cell.day/i);assert.match(brief,/unknown|coverage/i);
  const download=page.waitForEvent('download');await page.click('#brief-period-download');const dl=await download;assert.equal(await dl.failure(),null);
  checks.push({country,check:'brief-unit-coverage-and-download',passed:true,filename:dl.suggestedFilename()});
  const first=page.locator('.day-tile[data-date="2025-08-01"]');await first.focus();await page.keyboard.press('ArrowRight');
  assert.equal(await page.locator(':focus').getAttribute('data-date'),'2025-08-02');
  checks.push({country,check:'calendar-keyboard-day-navigation',passed:true});
  await page.click('#tab-explore');await page.waitForSelector('#map circle');
  const dot=page.locator('#map circle[tabindex="0"]').last();await dot.focus();await page.keyboard.press('Enter');
  const evidence=await page.locator('#map-evidence').innerText();assert.match(evidence,/August 2025/);assert.match(evidence,/raw detection/);
  assert.match(await dot.getAttribute('aria-label'),/August 2025.*active cell-days/);
  await page.locator('#map-evidence details').first().locator('summary').click();
  const expanded=await page.locator('#map-evidence').innerText();assert.match(expanded,/\.csv:\d+/);assert.match(expanded,/aggregate detail/);assert.doesNotMatch(expanded,/for every record/);
  checks.push({country,check:'keyboard-map-evidence-period-source-and-export-scope',passed:true});
  await page.click('#tab-research');assert.match(await page.locator('#promotion').innerText(),/not passed|failed/i);
  checks.push({country,check:'research-gate-failure-visible',passed:true});
  await page.setViewportSize({width:390,height:844});await page.click('#tab-overview');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  const sizes=await page.locator('.day-tile').evaluateAll(els=>els.map(el=>({w:el.getBoundingClientRect().width,h:el.getBoundingClientRect().height})));
  assert.ok(sizes.every(s=>s.w>=24&&s.h>=24));
  checks.push({country,check:'390px-no-page-overflow-and-24px-day-targets',passed:true});
  await page.setViewportSize({width:1440,height:1000});
 }
 assert.deepEqual(errors,[]);
 const manifest=await page.evaluate(async()=>(await fetch('data/manifest.json')).json());
 const source_sha256={};for(const f of ['web_app/app.js','web_app/index.html','web_app/style.css'])source_sha256[f]=createHash('sha256').update(await fs.readFile(f)).digest('hex');
 await fs.writeFile(out,JSON.stringify({tested_url:base,source_sha256,status:'passed',git_commit:execFileSync('git',['rev-parse','HEAD']).toString().trim(),working_tree_changes_included:true,run_id:manifest.run_id,kind:'deterministic browser checks; not human study or WCAG certification',participant_count:0,checks,page_errors:errors},null,2)+'\n');
 console.log(`${checks.length} deterministic demo checks passed; zero participants claimed.`);
}finally{await browser.close();}
