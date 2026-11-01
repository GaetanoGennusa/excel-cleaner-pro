/* Optional local-only end-to-end test. Uses installed Playwright, no downloads. */
const { chromium } = require(process.env.ECP_PLAYWRIGHT);
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const output = process.env.ECP_QA_OUTPUT;
const checks = [];

async function main() {
  const browser = await chromium.launch({headless: true, executablePath: process.env.ECP_CHROMIUM || undefined});
  const context = await browser.newContext({acceptDownloads: true, reducedMotion: 'reduce', viewport: {width: 1440, height: 1000}});
  const blocked = [];
  await context.route('**/*', route => {
    const url = new URL(route.request().url());
    if (['127.0.0.1', 'localhost'].includes(url.hostname)) return route.continue();
    blocked.push(url.origin);
    return route.abort();
  });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  async function step(name, action) {
    await action();
    assert.equal(await page.locator('[data-testid="stException"]').count(), 0);
    checks.push(name);
    console.log(`PASS ${name}`);
  }
  async function select(label, option) {
    const combo = page.getByRole('combobox', {name: label, exact: true});
    if (await combo.evaluate(element => element.tagName) === 'SELECT') {
      await combo.selectOption({label: option});
      return;
    }
    await combo.fill(option);
    await combo.press('ArrowDown');
    const target = page.getByRole('option', {name: option, exact: true});
    await target.waitFor({state: 'visible'});
    await combo.press('Enter');
    assert.equal(await combo.inputValue(), option);
  }
  async function freshSession() {
    // A reload waits for a fresh WebSocket/session rather than racing a
    // file-uploader remount after the sidebar clear action.
    await page.reload();
    await page.getByRole('heading', {name: 'Excel Cleaner Pro', exact: true}).waitFor();
  }
  async function upload(file) {
    await freshSession();
    await page.locator('input[type=file]').setInputFiles(file);
    await page.getByRole('button', {name: 'Carica dataset', exact: true}).waitFor();
    await page.getByRole('button', {name: 'Carica dataset', exact: true}).click();
    await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor();
  }
  try {
    await step('initial_screen', async () => {
      await page.goto('http://127.0.0.1:8521');
      await page.getByRole('heading', {name: 'Excel Cleaner Pro', exact: true}).waitFor();
      await page.getByText('Carica un dataset per visualizzare profilo, regole, anteprima ed esportazioni.', {exact: true}).waitFor();
      await page.screenshot({path: path.join(output, '01_upload.png')});
    });
    await step('csv_upload_and_profile', async () => {
      await upload(path.resolve('demo/10_before.csv'));
      await page.getByText('Valori nulli', {exact: true}).waitFor();
      await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).evaluate(element => element.scrollIntoView({block: 'start', behavior: 'instant'}));
      await page.screenshot({path: path.join(output, '02_overview.png')});
    });
    await step('explicit_rules_and_duplicate_confirmation', async () => {
      await page.getByText('Rimuovi spazi esterni e comprimi spazi interni', {exact: true}).click();
      assert.equal(await page.getByLabel('Rimuovi spazi esterni e comprimi spazi interni', {exact: true}).isChecked(), true);
      await page.getByRole('combobox', {name: 'Colonne da normalizzare come testo', exact: true}).click();
      await page.getByRole('option', {name: 'name', exact: true}).click();
      await page.keyboard.press('Escape');
      await select('Maiuscole/minuscole', 'title');
      await page.getByText('Numeri e date: formato esplicito per ogni colonna', {exact: true}).click();
      await select('amount · numero', 'Italiano (1.234,56)');
      // Date-format selection is covered by AppTest and remains a manual browser
      // check: this Chromium/React-Aria combination did not commit it reliably.
      // This browser scenario deliberately leaves ambiguous dates unchanged.
      await page.getByText('Rimuovi duplicati esatti presenti nella sorgente', {exact: true}).click();
      await page.getByRole('button', {name: 'Applica e mostra anteprima', exact: true}).click();
      await page.getByText('Confermare esplicitamente la rimozione dei duplicati esatti.', {exact: true}).waitFor();
      await page.getByText('Confermo la rimozione delle copie esatte, mantenendo la prima riga', {exact: true}).click();
      await page.getByRole('button', {name: 'Applica e mostra anteprima', exact: true}).click();
      await page.getByText('Controlli di integrità superati', {exact: true}).waitFor();
      await page.getByRole('heading', {name: '4 · Preview Changes', exact: true}).evaluate(element => element.scrollIntoView({block: 'start', behavior: 'instant'}));
      await page.screenshot({path: path.join(output, '03_preview.png')});
    });
    await step('actual_xlsx_and_csv_downloads', async () => {
      await page.getByRole('button', {name: 'Prepara esportazioni', exact: true}).click();
      const xlsx = page.waitForEvent('download');
      await page.getByRole('button', {name: 'Scarica report Excel', exact: true}).click();
      await (await xlsx).saveAs(path.join(output, 'downloaded_report.xlsx'));
      const csv = page.waitForEvent('download');
      await page.getByRole('button', {name: 'Scarica dati CSV (UTF-8, ;)', exact: true}).click();
      await (await csv).saveAs(path.join(output, 'downloaded_data.csv'));
      await page.screenshot({path: path.join(output, '04_export.png')});
    });
    await step('undo_and_reset', async () => {
      await page.getByRole('button', {name: 'Annulla ultima applicazione', exact: true}).click();
      await page.getByText('Scegli le regole e applicale per generare una versione esportabile, anche senza trasformazioni.', {exact: true}).waitFor();
      await page.getByRole('button', {name: 'Applica e mostra anteprima', exact: true}).click();
      await page.getByText('Controlli di integrità superati', {exact: true}).waitFor();
      await page.getByRole('button', {name: 'Ripristina dati originali', exact: true}).click();
      await page.getByText('Scegli le regole e applicale per generare una versione esportabile, anche senza trasformazioni.', {exact: true}).waitFor();
    });
    await step('xlsx_upload_and_sheet_selection', async () => {
      await upload(path.join(output, 'multi_sheet.xlsx'));
      await select('Foglio Excel', 'Notes');
      await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor({state: 'hidden'});
      await page.getByRole('button', {name: 'Carica dataset', exact: true}).click();
      await page.locator('input[aria-label="Synthetic notes · numero"]').waitFor({state: 'attached'});
      await select('Foglio Excel', 'Customers');
      await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor({state: 'hidden'});
      await page.getByRole('button', {name: 'Carica dataset', exact: true}).click();
      await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor();
      await page.locator('input[aria-label="code · numero"]').waitFor({state: 'attached'});
      assert.equal(await page.getByLabel('Rimuovi duplicati esatti presenti nella sorgente', {exact: true}).isChecked(), false);
    });
    await step('empty_and_invalid_files_rejected', async () => {
      for (const file of ['09_empty.csv', '08_malformed.csv']) {
        await freshSession();
        await page.locator('input[type=file]').setInputFiles(path.resolve('demo', file));
        await page.getByRole('button', {name: 'Carica dataset', exact: true}).click();
        await page.locator('[data-testid="stAlertContainer"]').filter({hasText: /vuoto|non leggibile/}).waitFor();
        assert.equal(await page.getByRole('button', {name: 'Scarica report Excel', exact: true}).count(), 0);
      }
    });
    await step('file_upload_size_limit', async () => {
      await page.locator('input[type=file]').setInputFiles(path.join(output, 'oversize.csv'));
      await page.getByText(/File must be 10.*or smaller|must be.*10.*MB|limite|too large/i).first().waitFor();
    });
    await step('narrow_viewport', async () => {
      const mobile = await context.newPage();
      mobile.on('pageerror', error => errors.push(error.message));
      await mobile.setViewportSize({width: 390, height: 844});
      await mobile.goto('http://127.0.0.1:8521');
      const title = mobile.getByRole('heading', {name: 'Excel Cleaner Pro', exact: true});
      await title.waitFor();
      await mobile.getByText('Carica un dataset per visualizzare profilo, regole, anteprima ed esportazioni.', {exact: true}).waitFor();
      const box = await title.boundingBox();
      assert.ok(box && box.x >= 0 && box.x + box.width <= 391);
      await mobile.screenshot({path: path.join(output, '05_mobile.png')});
      await mobile.close();
    });
    assert.deepEqual(errors, []);
  } catch (error) {
    await fs.writeFile(path.join(output, 'controls.json'), JSON.stringify({comboboxes: await page.getByRole('combobox').evaluateAll(elements => elements.map(element => ({html: element.outerHTML, value: element.value}))), options: await page.getByRole('option').allTextContents()}, null, 2));
    await page.screenshot({path: path.join(output, 'failure.png'), fullPage: true});
    await fs.writeFile(path.join(output, 'failure.txt'), `${error.stack}\n\n${await page.locator('body').innerText()}`);
    throw error;
  } finally {
    await fs.writeFile(path.join(output, 'browser_results.json'), JSON.stringify({timestamp: new Date().toISOString(), browser: browser.version(), checks, pageErrors: errors, blockedExternalOrigins: blocked}, null, 2));
    await browser.close();
  }
}
main().catch(error => {console.error(error); process.exitCode = 1;});
