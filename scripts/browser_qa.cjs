/* Optional local-only end-to-end test. Uses installed Playwright, no downloads.
   Interactions go through the real page like a person would: controls are
   brought well inside the window, then clicked. Nothing is written into the
   Streamlit state. Every wait is tied to a page condition. */
const { chromium } = require(process.env.ECP_PLAYWRIGHT);
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');

const output = process.env.ECP_QA_OUTPUT;
const BASE = 'http://127.0.0.1:8521';
const DESKTOP = {width: 1440, height: 1000};
const TABLET = {width: 900, height: 1100};
const MOBILE = {width: 390, height: 844};
const TRIM = 'Rimuovi spazi esterni e comprimi spazi interni';
const DEDUPE = 'Rimuovi duplicati esatti presenti nella sorgente';
const CONFIRM = 'Confermo la rimozione delle copie esatte, mantenendo la prima riga';
const FORMATS = 'Numeri e date: formato esplicito per ogni colonna';
const EMPTY_STATE = 'Carica un dataset per visualizzare profilo, regole, anteprima ed esportazioni.';
const CHANGED = 'Sorgente o impostazioni cambiate: carica nuovamente il dataset.';
const XLSX_BUTTON = 'Scarica report Excel';
const CSV_BUTTON = 'Scarica dati CSV (UTF-8, ;)';

const checks = [];
const errors = [];
const blocked = [];
let browser;
let lastPage;

async function openPage(viewport, reducedMotion) {
  const context = await browser.newContext({acceptDownloads: true, reducedMotion, viewport});
  await context.route('**/*', route => {
    const url = new URL(route.request().url());
    if (['127.0.0.1', 'localhost'].includes(url.hostname)) return route.continue();
    blocked.push(url.origin);
    return route.abort();
  });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  page.on('pageerror', error => errors.push(`${reducedMotion}@${viewport.width}: ${error.message}`));
  lastPage = page;
  return {context, page};
}

async function step(page, name, action) {
  await action();
  assert.equal(await page.locator('[data-testid="stException"]').count(), 0, `${name}: Streamlit exception`);
  checks.push(name);
  console.log(`PASS ${name}`);
}

// Resolve once an element keeps the same box for several frames (smooth scroll, expanders).
async function stable(locator) {
  await locator.evaluate(element => new Promise(resolve => {
    let last = '';
    let same = 0;
    const tick = () => {
      const box = element.getBoundingClientRect();
      const key = `${Math.round(box.top)}:${Math.round(box.left)}:${Math.round(box.height)}`;
      same = key === last ? same + 1 : 0;
      last = key;
      if (same >= 5) resolve(); else requestAnimationFrame(tick);
    };
    tick();
  }));
}

// Streamlit's select menus close when the page scrolls right after they open.
// Clicking a control at the very edge of the window triggers that scroll, for
// people as well as for scripts, so controls are first brought to the middle.
async function reveal(locator) {
  await locator.waitFor();
  await locator.evaluate(element => element.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'}));
  await stable(locator);
}

async function press(page, name) {
  const button = page.getByRole('button', {name, exact: true});
  await reveal(button);
  await button.click();
}

async function tick(page, label) {
  const text = page.getByText(label, {exact: true});
  await reveal(text);
  await text.click();
  const box = await page.getByLabel(label, {exact: true}).elementHandle();
  await page.waitForFunction(element => element.checked, box);
}

async function choose(page, label, option) {
  const combo = page.getByRole('combobox', {name: label, exact: true});
  await reveal(combo);
  await combo.click();
  await page.getByRole('option', {name: option, exact: true}).click();
  // The closed select must show the chosen option; the applied configuration
  // and the downloaded report are checked separately.
  await page.waitForFunction(([name, value]) => {
    const input = [...document.querySelectorAll('input[role="combobox"]')].find(element => element.getAttribute('aria-label') === name);
    return input && input.value === value && input.getAttribute('aria-expanded') !== 'true';
  }, [label, option]);
}

async function pick(page, label, option) {
  const combo = page.getByRole('combobox', {name: label, exact: true});
  await reveal(combo);
  await combo.click();
  await page.getByRole('option', {name: option, exact: true}).click();
  await page.keyboard.press('Escape');
  await page.locator('[data-testid="stMultiSelect"]').filter({hasText: label}).getByText(option, {exact: true}).waitFor();
}

async function openExpander(page, title) {
  const summary = page.getByText(title, {exact: true});
  await reveal(summary);
  await summary.click();
  const expander = page.locator('[data-testid="stExpander"]').filter({hasText: title}).first();
  await expander.locator('details[open]').waitFor();
  await stable(expander);
}

async function download(page, name, file) {
  const button = page.getByRole('button', {name, exact: true});
  await reveal(button);
  const [event] = await Promise.all([page.waitForEvent('download'), button.click()]);
  await event.saveAs(path.join(output, file));
}

async function noDownloads(page) {
  for (const name of [XLSX_BUTTON, CSV_BUTTON]) {
    assert.equal(await page.getByRole('button', {name, exact: true}).count(), 0, `stale download button: ${name}`);
  }
}

async function overviewHidden(page) {
  await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor({state: 'hidden'});
  await noDownloads(page);
}

async function noPageOverflow(page) {
  const overflow = await page.evaluate(() => {
    const main = document.querySelector('[data-testid="stMain"]');
    return {main: main.scrollWidth - main.clientWidth, document: document.documentElement.scrollWidth - window.innerWidth};
  });
  assert.ok(overflow.main <= 1 && overflow.document <= 1, `horizontal page overflow ${JSON.stringify(overflow)}`);
}

async function ready(page) {
  await page.getByRole('heading', {name: 'Excel Cleaner Pro', exact: true}).waitFor();
  await page.getByRole('button', {name: /^(Upload|Browse files)$/}).waitFor();
}

async function load(page, file) {
  await page.locator('input[type=file]').setInputFiles(file);
  await press(page, 'Carica dataset');
  await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor();
}

async function applyRules(page) {
  await press(page, 'Applica e mostra anteprima');
  await page.getByText('Controlli di integrità superati', {exact: true}).waitFor();
}

async function shot(page, heading, file) {
  if (heading) {
    await page.getByRole('heading', {name: heading, exact: true}).evaluate(element => element.scrollIntoView({block: 'start', behavior: 'instant'}));
    await stable(page.getByRole('heading', {name: heading, exact: true}));
  }
  await page.screenshot({path: path.join(output, file)});
}

async function mainFlow(label, reducedMotion, shots) {
  const {context, page} = await openPage(DESKTOP, reducedMotion);
  await step(page, `${label}:initial_screen`, async () => {
    await page.goto(BASE);
    await ready(page);
    await page.getByText(EMPTY_STATE, {exact: true}).waitFor();
    if (shots) await shot(page, null, '01_upload.png');
  });
  await step(page, `${label}:csv_upload_and_profile`, async () => {
    await load(page, path.resolve('demo/10_before.csv'));
    await page.getByText('Valori nulli', {exact: true}).waitFor();
    if (shots) await shot(page, '2 · Data Overview', '02_overview.png');
  });
  await step(page, `${label}:sidebar_navigation`, async () => {
    await page.getByRole('link', {name: 'Regole di pulizia', exact: true}).click();
    await page.waitForURL('**/#rules');
    const heading = page.getByRole('heading', {name: '3 · Cleaning Rules', exact: true});
    await stable(heading);
    const box = await heading.boundingBox();
    assert.ok(box && box.y >= 0 && box.y < DESKTOP.height / 2, `rules heading at ${box && box.y}`);
  });
  await step(page, `${label}:rules_with_explicit_date_format`, async () => {
    await tick(page, TRIM);
    await pick(page, 'Colonne da normalizzare come testo', 'name');
    await choose(page, 'Maiuscole/minuscole', 'title');
    await openExpander(page, FORMATS);
    await choose(page, 'amount · numero', 'Italiano (1.234,56)');
    await choose(page, 'date · data', '%d/%m/%Y');
    await tick(page, DEDUPE);
    await press(page, 'Applica e mostra anteprima');
    await page.getByText('Confermare esplicitamente la rimozione dei duplicati esatti.', {exact: true}).waitFor();
    await tick(page, CONFIRM);
    await applyRules(page);
    // Trim, title for name, Italian amount, date format and deduplication.
    await page.getByText(/^Regole selezionate nell'ultima applicazione: 5\./).waitFor();
    if (shots) await shot(page, '4 · Preview Changes', '03_preview.png');
  });
  await step(page, `${label}:xlsx_and_csv_downloads`, async () => {
    await press(page, 'Prepara esportazioni');
    await download(page, XLSX_BUTTON, `${label}_report.xlsx`);
    await download(page, CSV_BUTTON, `${label}_data.csv`);
    if (shots) await shot(page, '5 · Export', '04_export.png');
  });
  await step(page, `${label}:undo_and_reset`, async () => {
    await press(page, 'Annulla ultima applicazione');
    await page.getByText('Scegli le regole e applicale per generare una versione esportabile, anche senza trasformazioni.', {exact: true}).waitFor();
    await noDownloads(page);
    await applyRules(page);
    await press(page, 'Ripristina dati originali');
    await page.getByText('Scegli le regole e applicale per generare una versione esportabile, anche senza trasformazioni.', {exact: true}).waitFor();
    await noDownloads(page);
  });
  await context.close();
}

async function sameSessionFlow() {
  // One page for the whole scenario: no reloads between sources.
  const {context, page} = await openPage(DESKTOP, 'no-preference');
  await page.goto(BASE);
  await ready(page);
  await step(page, 'session:no_date_rule_keeps_ambiguous_date', async () => {
    await load(page, path.resolve('demo/10_before.csv'));
    await tick(page, TRIM);
    await applyRules(page);
    await press(page, 'Prepara esportazioni');
    await download(page, XLSX_BUTTON, 'nodate_report.xlsx');
  });
  await step(page, 'session:replace_file_invalidates_result', async () => {
    await page.locator('input[type=file]').setInputFiles(path.resolve('demo/04_italian_amounts.csv'));
    // Replacing a file first removes the previous upload, which clears the
    // dataset without the "settings changed" notice; the requirement is that
    // nothing derived from the previous file stays visible or downloadable.
    await page.getByText('04_ital', {exact: false}).first().waitFor();
    await overviewHidden(page);
    await page.getByText(EMPTY_STATE, {exact: true}).waitFor();
    await press(page, 'Carica dataset');
    await page.getByText('Sorgente attiva: 04_italian_amounts.csv', {exact: true}).waitFor();
    await noDownloads(page);
    assert.equal(await page.locator('input[aria-label="date · data"]').count(), 0, 'columns of the previous source still shown');
    await applyRules(page);
    await press(page, 'Prepara esportazioni');
    await download(page, XLSX_BUTTON, 'switch_report.xlsx');
  });
  await step(page, 'session:csv_separator_change_invalidates_result', async () => {
    await choose(page, 'Separatore CSV', 'Virgola ,');
    await page.getByText(CHANGED, {exact: true}).waitFor();
    await overviewHidden(page);
    await choose(page, 'Separatore CSV', 'Punto e virgola ;');
    await page.getByRole('button', {name: 'Carica dataset', exact: true}).waitFor();
    await overviewHidden(page);
  });
  await step(page, 'session:csv_encoding_change_invalidates_result', async () => {
    await press(page, 'Carica dataset');
    await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor();
    await applyRules(page);
    await press(page, 'Prepara esportazioni');
    await page.getByRole('button', {name: XLSX_BUTTON, exact: true}).waitFor();
    await choose(page, 'Codifica CSV', 'utf-8');
    await page.getByText(CHANGED, {exact: true}).waitFor();
    await overviewHidden(page);
  });
  await step(page, 'session:xlsx_sheet_change_invalidates_result', async () => {
    await page.locator('input[type=file]').setInputFiles(path.join(output, 'multi_sheet.xlsx'));
    await page.getByRole('combobox', {name: 'Foglio Excel', exact: true}).waitFor();
    await press(page, 'Carica dataset');
    await page.getByRole('heading', {name: '2 · Data Overview', exact: true}).waitFor();
    await page.locator('input[aria-label="code · numero"]').waitFor({state: 'attached'});
    await applyRules(page);
    await press(page, 'Prepara esportazioni');
    await page.getByRole('button', {name: XLSX_BUTTON, exact: true}).waitFor();
    await choose(page, 'Foglio Excel', 'Notes');
    await page.getByText(CHANGED, {exact: true}).waitFor();
    await overviewHidden(page);
    await press(page, 'Carica dataset');
    await page.locator('input[aria-label="Synthetic notes · numero"]').waitFor({state: 'attached'});
    assert.equal(await page.locator('input[aria-label="code · numero"]').count(), 0, 'previous sheet schema still shown');
    await noDownloads(page);
  });
  await step(page, 'session:remove_file_clears_dataset', async () => {
    const remove = page.getByRole('button', {name: /^Remove multi_sheet\.xlsx$/});
    await reveal(remove);
    await remove.click();
    await page.getByText(EMPTY_STATE, {exact: true}).waitFor();
    await overviewHidden(page);
    assert.equal(await page.getByRole('button', {name: 'Carica dataset', exact: true}).count(), 0);
  });
  await context.close();
}

async function rejectionFlow() {
  const {context, page} = await openPage(DESKTOP, 'reduce');
  for (const file of ['09_empty.csv', '08_malformed.csv']) {
    await step(page, `reject:${file}`, async () => {
      await page.goto(BASE);
      await ready(page);
      await page.locator('input[type=file]').setInputFiles(path.resolve('demo', file));
      await press(page, 'Carica dataset');
      await page.locator('[data-testid="stAlertContainer"]').filter({hasText: /vuoto|non leggibile/}).waitFor();
      await noDownloads(page);
    });
  }
  await step(page, 'reject:file_upload_size_limit', async () => {
    await page.locator('input[type=file]').setInputFiles(path.join(output, 'oversize.csv'));
    await page.getByText(/File must be 10.*or smaller|must be.*10.*MB|limite|too large/i).first().waitFor();
  });
  await context.close();
}

async function narrowFlow(label, viewport, prefix) {
  const {context, page} = await openPage(viewport, 'no-preference');
  await step(page, `${label}:initial_screen`, async () => {
    await page.goto(BASE);
    await ready(page);
    const title = page.getByRole('heading', {name: 'Excel Cleaner Pro', exact: true});
    const box = await title.boundingBox();
    assert.ok(box && box.x >= 0 && box.x + box.width <= viewport.width + 1);
    await noPageOverflow(page);
    await shot(page, null, `${prefix}_upload.png`);
  });
  await step(page, `${label}:upload_and_profile`, async () => {
    await load(page, path.resolve('demo/10_before.csv'));
    await noPageOverflow(page);
  });
  await step(page, `${label}:rules`, async () => {
    await tick(page, TRIM);
    await openExpander(page, FORMATS);
    await choose(page, 'amount · numero', 'Italiano (1.234,56)');
    await choose(page, 'date · data', '%d/%m/%Y');
    await noPageOverflow(page);
    // Rule labels must be readable in full, not cut with an ellipsis.
    const cut = await page.locator('[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"]').evaluateAll(
      labels => labels.filter(label => label.scrollWidth > label.clientWidth + 1).map(label => label.textContent));
    assert.deepEqual(cut, [], 'truncated checkbox labels');
    await shot(page, '3 · Cleaning Rules', `${prefix}_rules.png`);
  });
  await step(page, `${label}:preview`, async () => {
    await applyRules(page);
    await page.getByText(/^Regole selezionate nell'ultima applicazione: 3\./).waitFor();
    await noPageOverflow(page);
    await shot(page, '4 · Preview Changes', `${prefix}_preview.png`);
  });
  await step(page, `${label}:export`, async () => {
    await press(page, 'Prepara esportazioni');
    await download(page, XLSX_BUTTON, `${label}_report.xlsx`);
    await noPageOverflow(page);
    await shot(page, '5 · Export', `${prefix}_export.png`);
  });
  await context.close();
}

async function main() {
  browser = await chromium.launch({headless: true, executablePath: process.env.ECP_CHROMIUM || undefined});
  try {
    await mainFlow('reduced', 'reduce', true);
    await mainFlow('animated', 'no-preference', false);
    await sameSessionFlow();
    await rejectionFlow();
    await narrowFlow('tablet', TABLET, '09_tablet');
    await narrowFlow('mobile', MOBILE, '05_mobile');
    assert.deepEqual(errors, []);
    assert.deepEqual(blocked, [], 'The interface must not request external assets');
  } catch (error) {
    if (lastPage && !lastPage.isClosed()) {
      await lastPage.screenshot({path: path.join(output, 'failure.png')}).catch(() => {});
      const text = await lastPage.locator('body').innerText().catch(() => '');
      await fs.writeFile(path.join(output, 'failure.txt'), `${error.stack}\n\n${text}`);
    }
    throw error;
  } finally {
    await fs.writeFile(path.join(output, 'browser_results.json'), JSON.stringify({
      timestamp: new Date().toISOString(), browser: browser.version(), checks, pageErrors: errors, blockedExternalOrigins: blocked,
    }, null, 2));
    await browser.close();
  }
}
module.exports = {stable, reveal, press, tick, choose, pick, openExpander, download, shot};
if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
