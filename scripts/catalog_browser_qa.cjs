/* Real app recording and local portfolio QA. No external assets or state injection.
   Dwell times are for video readability, never used to establish test success. */
const {chromium} = require(process.env.ECP_PLAYWRIGHT);
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const {reveal,press,tick,choose,pick,openExpander,download,shot} = require('./browser_qa.cjs');
const output = process.env.ECP_QA_OUTPUT;
const catalog = path.resolve('demo/product_catalog');
const checks = [], errors = [], external = [];
let browser, lastPage;

async function context(options={}) {
  const ctx = await browser.newContext({acceptDownloads:true, reducedMotion:'reduce', viewport:{width:1440,height:1000}, ...options});
  await ctx.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.protocol === 'file:' || ['127.0.0.1','localhost'].includes(url.hostname)) return route.continue();
    external.push(url.origin); return route.abort();
  });
  ctx.on('page', page => { page.setDefaultTimeout(15000); page.on('pageerror', e=>errors.push(e.message)); lastPage=page; });
  return ctx;
}
async function step(name, action) { await action(); checks.push(name); console.log('PASS '+name); }
async function dwell(page, milliseconds) { await page.waitForTimeout(milliseconds); }

async function appDemo() {
  const ctx = await context({recordVideo:{dir:path.join(output,'recording'), size:{width:1440,height:1000}}});
  const page = await ctx.newPage();
  const video = page.video();
  try {
    await step('catalog:upload', async()=>{
      await page.goto('http://127.0.0.1:8523');
      await page.getByRole('button',{name:/^(Upload|Browse files)$/}).waitFor();
      await page.locator('input[type=file]').setInputFiles(path.join(catalog,'catalogo_originale.csv'));
      await dwell(page,2500);
      await press(page,'Carica dataset');
      await page.getByRole('heading',{name:'2 · Panoramica dati',exact:true}).waitFor();
      await shot(page,'2 · Panoramica dati','overview.png');
      await dwell(page,4000);
    });
    await step('catalog:explicit_rules', async()=>{
      await tick(page,'Rimuovi spazi esterni e comprimi spazi interni');
      await pick(page,'Colonne da normalizzare come testo','nome');
      await pick(page,'Colonne da normalizzare come testo','categoria');
      await choose(page,'Maiuscole/minuscole','title');
      await openExpander(page,'Numeri e date: formato esplicito per ogni colonna');
      await choose(page,'prezzo_eur · numero','Italiano (1.234,56)');
      await choose(page,'disponibilita · numero','Italiano (1.234,56)');
      await choose(page,'aggiornato_il · data','%d/%m/%Y');
      await tick(page,'Rimuovi duplicati esatti presenti nella sorgente');
      await tick(page,'Confermo la rimozione delle copie esatte, mantenendo la prima riga');
      await dwell(page,2500);
      await press(page,'Applica e mostra anteprima');
      await page.getByText('Controlli di integrità superati',{exact:true}).waitFor();
      await page.getByText(/^Regole selezionate nell'ultima applicazione: 7\./).waitFor();
      assert.equal(await page.locator('[data-testid="stException"]').count(),0);
    });
    await step('catalog:preview_and_issues', async()=>{
      await shot(page,'4 · Anteprima modifiche','preview.png');
      await dwell(page,6500);
      const issues=page.getByRole('tab',{name:'Anomalie della sorgente e conversioni',exact:true});
      await reveal(issues); await issues.click();
      await page.screenshot({path:path.join(output,'issues.png')});
      await dwell(page,4000);
      const log=page.getByRole('tab',{name:'Log operazioni',exact:true});
      await reveal(log); await log.click();
      await dwell(page,4000);
    });
    await step('catalog:actual_downloads', async()=>{
      await press(page,'Prepara esportazioni');
      await download(page,'Scarica report Excel','app_report.xlsx');
      await download(page,'Scarica dati CSV (UTF-8, ;)','app_data.csv');
      await shot(page,'5 · Esporta','export.png');
      await dwell(page,5000);
    });
  } finally { await ctx.close(); }
  await video.saveAs(path.join(output,'demo_catalogo.webm'));
}

async function portfolioDemo() {
  const ctx=await context();
  const page=await ctx.newPage();
  try {
    await step('portfolio:desktop_and_comparison', async()=>{
      await page.goto('http://127.0.0.1:8524');
      await page.getByRole('heading',{level:1}).waitFor();
      assert.equal(await page.locator('#data-body tr').count(),10);
      assert.ok((await page.locator('#data-body tr').first().textContent()).includes('€ 1.234,56'));
      await page.screenshot({path:path.join(output,'portfolio_desktop.png')});
      await page.getByRole('radio',{name:'Dopo',exact:true}).check();
      assert.ok((await page.locator('#data-body tr').first().textContent()).includes('1234.56'));
      assert.ok((await page.locator('#data-body tr').first().textContent()).includes('2026-02-01'));
      await page.getByRole('radio',{name:'Valori da verificare',exact:true}).check();
      assert.equal(await page.locator('#data-body tr').count(),6);
      assert.ok((await page.locator('#data-body').textContent()).includes('31/02/2026'));
    });
    await step('portfolio:keyboard_and_downloads', async()=>{
      await page.getByRole('radio',{name:'Prima',exact:true}).focus();
      await page.keyboard.press('ArrowRight');
      assert.ok(await page.getByRole('radio',{name:'Dopo',exact:true}).isChecked());
      for (const [label,file] of [['Scarica l’originale','portfolio_source.csv'],['Scarica il risultato','portfolio_cleaned.csv'],['Scarica il report completo','portfolio_report.xlsx']]) {
        const name=label.replace('’',"'");
        const link=page.getByRole('link',{name,exact:true});
        const [event]=await Promise.all([page.waitForEvent('download'),link.click()]);
        await event.saveAs(path.join(output,file));
      }
      const response=await page.request.get('http://127.0.0.1:8524/SERVICE_EN.md');
      assert.equal(response.status(),200);
    });
    await step('portfolio:recorded_video_plays', async()=>{
      await page.locator('video').scrollIntoViewIfNeeded();
      const duration = await page.locator('video').evaluate(async video=>{
        video.muted=true;
        await video.play();
        await new Promise((resolve,reject)=>{
          video.addEventListener('timeupdate',()=>{ if(video.currentTime>0)resolve(); },{once:true});
          video.addEventListener('error',()=>reject(new Error('Video decode error')),{once:true});
        });
        video.pause();
        return video.duration;
      });
      assert.ok(Number.isFinite(duration) && duration>20 && duration<120,`Unexpected recording length ${duration}`);
      console.log(`VIDEO_SECONDS ${duration.toFixed(2)}`);
    });
    await step('portfolio:mobile', async()=>{
      const mobileCtx=await context({viewport:{width:390,height:844}});
      try {
        const mobile=await mobileCtx.newPage();
        await mobile.goto('http://127.0.0.1:8524');
        await mobile.getByRole('heading',{level:1}).waitFor();
        assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
        await mobile.screenshot({path:path.join(output,'portfolio_mobile.png')});
        await mobile.getByRole('radio',{name:'Dopo',exact:true}).check();
        assert.equal(await mobile.locator('#data-body tr').count(),10);
        assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
      } finally { await mobileCtx.close(); }
    });
    await step('portfolio:double_click_without_server', async()=>{
      await page.goto(require('node:url').pathToFileURL(path.join(catalog,'index.html')).href);
      await page.getByRole('radio',{name:'Dopo',exact:true}).check();
      assert.equal(await page.locator('#data-body tr').count(),10);
      assert.ok((await page.locator('#data-body tr').first().textContent()).includes('000001'));
    });
  } finally { await ctx.close(); }
}

(async()=>{
  browser=await chromium.launch({headless:true,executablePath:process.env.ECP_CHROMIUM});
  try {
    if(process.argv.includes('--app')) await appDemo(); else await portfolioDemo();
    assert.deepEqual(errors,[],'JavaScript errors');
    assert.deepEqual(external,[],'External asset requests');
  } catch(error) {
    if(lastPage && !lastPage.isClosed()) await lastPage.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});
    throw error;
  } finally {
    await fs.writeFile(path.join(output,process.argv.includes('--app')?'app_browser_results.json':'portfolio_browser_results.json'),JSON.stringify({timestamp:new Date().toISOString(),checks,pageErrors:errors,externalOrigins:external},null,2));
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
