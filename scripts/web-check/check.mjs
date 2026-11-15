import { createServer } from 'node:http';
import { readFile, realpath, stat, mkdir, writeFile } from 'node:fs/promises';
import { resolve, relative, extname, sep, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';

const sha = data => createHash('sha256').update(data).digest('hex');
const idPattern = /^[a-zA-Z0-9_-]{1,48}$/;
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.woff2': 'font/woff2' };
const message = error => String(error?.message ?? error).slice(0, 3000);
const inside = (root, path) => { const rel = relative(root, path); return !isAbsolute(rel) && rel !== '..' && !rel.startsWith(`..${sep}`); };

export function validatePlan(plan) {
  finite(plan);
  if (plan?.schema !== 1 || !Array.isArray(plan.scenarios) || !plan.scenarios.length || plan.scenarios.length > 20)
    throw new Error('Plan requires schema=1 and 1–20 scenarios; empty plans cannot pass.');
  const ids = new Set(); let assertions = 0; let waits = 0;
  for (const scenario of plan.scenarios) {
    if (!idPattern.test(scenario.id) || ids.has(scenario.id)) throw new Error('Scenario IDs must be unique ASCII identifiers.');
    ids.add(scenario.id);
    if (!Array.isArray(scenario.steps) || !scenario.steps.length || scenario.steps.length > 100) throw new Error('Each scenario needs 1–100 steps.');
    let checks = 0;
    for (const step of scenario.steps) {
      if (!step || typeof step !== 'object') throw new Error('Invalid step.');
      switch (step.action) {
        case 'click': case 'tap': case 'expectText':
          if (typeof step.selector !== 'string' || !step.selector.trim()) throw new Error('Selector is required.');
          if (step.action === 'tap' && plan.touch !== true) throw new Error('tap requires touch=true.');
          if (step.action === 'expectText') { if (typeof step.equals !== 'string') throw new Error('expectText.equals must be a string.'); checks++; }
          break;
        case 'press': if (typeof step.key !== 'string' || !step.key) throw new Error('Key is required.'); break;
        case 'wait':
          if (!Number.isInteger(step.ms) || step.ms < 0 || step.ms > 5000) throw new Error('Wait must be 0–5000 ms.');
          waits += step.ms; break;
        case 'reload': break;
        case 'expectState':
          if (typeof step.path !== 'string' || !step.path || step.path.split('.').some(p => !p || ['__proto__', 'prototype', 'constructor'].includes(p)) || !Object.hasOwn(step, 'equals')) throw new Error('expectState needs a safe path and equals.');
          checks++; break;
        case 'screenshot': if (!idPattern.test(step.name)) throw new Error('Screenshot needs an ASCII name.'); break;
        default: throw new Error(`Unknown action: ${step.action}`);
      }
    }
    if (!checks) throw new Error(`Scenario ${scenario.id} has no assertions; screenshots alone cannot pass.`);
    assertions += checks;
  }
  if (waits > 60000) throw new Error('Plan explicit waits exceed 60 seconds.');
  const size = plan.viewport ?? { width: 960, height: 900 };
  if (Object.hasOwn(plan, 'touch') && typeof plan.touch !== 'boolean') throw new Error('touch must be a boolean.');
  if (!Number.isInteger(size.width) || !Number.isInteger(size.height) || size.width < 240 || size.width > 3840 || size.height < 240 || size.height > 3840) throw new Error('Invalid viewport.');
  return { assertions, viewport: size };
}

export async function staticFile(root, requestPath) {
  const decoded = decodeURIComponent(requestPath);
  if (decoded.includes('\\') || decoded.includes('\0') || decoded.split('/').some(part => part.startsWith('.'))) throw new Error('Hidden/traversal paths are denied.');
  const path = await realpath(resolve(root, `.${decoded === '/' ? '/index.html' : decoded}`));
  if (!inside(root, path) || !mime[extname(path).toLowerCase()] || !(await stat(path)).isFile()) throw new Error('Not a public static file.');
  return path;
}

export async function serve(project) {
  const root = await realpath(project);
  const served = new Map();
  const server = createServer(async (request, response) => {
    try {
      if (request.method !== 'GET' && request.method !== 'HEAD') { response.writeHead(405).end(); return; }
      const path = await staticFile(root, new URL(request.url, 'http://127.0.0.1').pathname);
      const data = await readFile(path);
      served.set(relative(root, path).split(sep).join('/'), sha(data));
      response.writeHead(200, { 'Content-Type': `${mime[extname(path).toLowerCase()]}; charset=utf-8`, 'Cache-Control': 'no-store' });
      response.end(request.method === 'HEAD' ? undefined : data);
    } catch { response.writeHead(404).end('Not found'); }
  });
  await new Promise((accept, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', accept); });
  return { url: `http://127.0.0.1:${server.address().port}`, served,
    close: () => new Promise((accept, reject) => server.close(error => error ? reject(error) : accept())) };
}

function finite(value, seen = new Set()) {
  if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('Game state contains a non-finite number.');
  if (value && typeof value === 'object') {
    if (seen.has(value)) throw new Error('Game state contains a cycle.');
    seen.add(value); for (const child of Object.values(value)) finite(child, seen); seen.delete(value);
  }
}
export async function withTimeout(promise, ms, label) {
  let timer;
  try {
    return await Promise.race([promise, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(`${label} timed out after ${ms}ms.`)), ms);
    })]);
  } finally { clearTimeout(timer); }
}
async function stateOf(page) {
  const state = await withTimeout(page.evaluate(() => {
    const value = typeof window.game?.getState === 'function' ? window.game.getState() : null;
    if (value && typeof value.then === 'function') throw new Error('getState must return a synchronous snapshot, not a Promise.');
    return value;
  }), 3000, 'State observation');
  finite(state); return state;
}
function valueAt(state, path) {
  let value = state;
  for (const key of path.split('.')) {
    if (value == null || !Object.hasOwn(value, key)) throw new Error(`State path does not exist: ${path}`);
    value = value[key];
  }
  return value;
}

export async function runChecks({ project, planPath, out, executable, channel }) {
  project = resolve(project); planPath = resolve(planPath); out = resolve(out);
  if (out === project) throw new Error('Output must not replace the project root.');
  // A new evidence directory prevents stale screenshots/reports being mistaken for this run.
  await mkdir(out, { recursive: false });
  const report = { schema: 1, toolVersion: '1.4.0', status: 'failed', startedAt: new Date().toISOString(), project,
    environment: { platform: process.platform, node: process.version }, scenarios: [], servedFiles: [],
    limits: ['Only this plan and viewport are checked.', 'No judgement of fun, balance, art quality, native engines, physical devices or release readiness.'] };
  let browser; let server;
  try {
    const planBytes = await readFile(planPath);
    const plan = JSON.parse(planBytes);
    const { viewport } = validatePlan(plan);
    report.planSha256 = sha(planBytes); report.viewport = viewport; report.touch = plan.touch === true;
    if (!(await stat(resolve(project, 'index.html'))).isFile()) throw new Error('Project needs index.html.');
    let chromium;
    try { ({ chromium } = await import('playwright')); }
    catch { report.status = 'not_run'; throw new Error('Playwright is unavailable. Run npm ci in the web-check directory.'); }
    try { browser = await chromium.launch({ headless: true, timeout: 30000, ...(executable ? { executablePath: resolve(executable) } : {}), ...(channel ? { channel } : {}) }); }
    catch (error) { report.status = 'not_run'; throw new Error(`Browser unavailable: ${message(error)}`); }
    report.environment.browser = browser.version();
    server = await serve(project);
    const deadline = Date.now() + 120000;
    for (const scenario of plan.scenarios) {
      const result = { id: scenario.id, status: 'failed', steps: [], errors: [], warnings: [], screenshots: [] };
      report.scenarios.push(result);
      const context = await browser.newContext({ viewport, hasTouch: plan.touch === true });
      const page = await context.newPage();
      page.setDefaultTimeout(3000); page.setDefaultNavigationTimeout(15000);
      page.on('pageerror', error => result.errors.push(`pageerror: ${message(error)}`));
      page.on('console', item => { if (item.type() === 'error') result.errors.push(`console: ${item.text().slice(0, 1500)}`); else if (item.type() === 'warning') result.warnings.push(item.text().slice(0, 1500)); });
      page.on('requestfailed', request => { if (request.failure()?.errorText !== 'net::ERR_ABORTED') result.errors.push(`requestfailed: ${request.url()}`); });
      page.on('response', response => { if (response.status() >= 400) result.errors.push(`HTTP ${response.status()}: ${response.url()}`); });
      const capture = async name => {
        const filename = `${scenario.id}-${name}.png`;
        await page.screenshot({ path: resolve(out, filename), fullPage: true, timeout: 5000 });
        result.screenshots.push({ path: filename, sha256: sha(await readFile(resolve(out, filename))) });
      };
      try {
        if (Date.now() > deadline) throw new Error('Run exceeded the 120-second action budget.');
        await page.goto(server.url, { waitUntil: 'load' });
        for (const [index, step] of scenario.steps.entries()) {
          if (Date.now() > deadline) throw new Error('Run exceeded the 120-second action budget.');
          const executed = { index, action: step.action, status: 'failed' }; result.steps.push(executed);
          switch (step.action) {
            case 'click': await page.locator(step.selector).click(); break;
            case 'tap': await page.locator(step.selector).tap(); break;
            case 'press': await page.keyboard.press(step.key); break;
            case 'wait': await page.waitForTimeout(step.ms); break;
            case 'reload': await page.reload({ waitUntil: 'load' }); break;
            case 'screenshot': await capture(`${index}-${step.name}`); break;
            case 'expectText': {
              const locator = page.locator(step.selector); await locator.waitFor({ state: 'visible' });
              const actual = (await locator.textContent()).trim();
              executed.actual = actual; executed.expected = step.equals;
              if (actual !== step.equals) throw new Error(`Text mismatch at ${step.selector}: ${JSON.stringify(actual)} != ${JSON.stringify(step.equals)}`);
              break;
            }
            case 'expectState': {
              const until = Math.min(deadline, Date.now() + 3000); let actual;
              do {
                const state = await stateOf(page);
                if (state === null) throw new Error('expectState needs a read-only window.game.getState() observation hook.');
                actual = valueAt(state, step.path);
                if (isDeepStrictEqual(actual, step.equals)) break;
                await page.waitForTimeout(50);
              } while (Date.now() < until);
              executed.actual = actual; executed.expected = step.equals;
              if (!isDeepStrictEqual(actual, step.equals)) throw new Error(`State mismatch at ${step.path}: ${JSON.stringify(actual)} != ${JSON.stringify(step.equals)}`);
              break;
            }
          }
          executed.status = 'passed';
        }
        result.finalState = await stateOf(page);
        await capture('final');
        if (result.errors.length) throw new Error('Browser errors were recorded.');
        result.status = 'passed';
      } catch (error) {
        result.errors.push(message(error));
        try { await capture('failure'); } catch (captureError) { result.warnings.push(`Screenshot unavailable: ${message(captureError)}`); }
      } finally { await context.close(); }
    }
    report.status = report.scenarios.every(item => item.status === 'passed') ? 'passed' : 'failed';
  } catch (error) { report.error = message(error); }
  finally {
    if (server) { report.servedFiles = [...server.served].sort().map(([path, sha256]) => ({ path, sha256 })); await server.close(); }
    if (browser) await browser.close();
    report.finishedAt = new Date().toISOString();
    await writeFile(resolve(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  }
  return report;
}

async function main(args) {
  const options = {};
  for (let i = 0; i < args.length; i += 2) {
    const name = { '--project': 'project', '--plan': 'planPath', '--out': 'out', '--executable': 'executable', '--channel': 'channel' }[args[i]];
    if (!name || !args[i + 1] || options[name]) throw new Error('Usage: node check.mjs --project DIR --plan FILE --out NEW_DIR [--channel chrome|msedge | --executable FILE]');
    options[name] = args[i + 1];
  }
  if (!options.project || !options.planPath || !options.out || (options.executable && options.channel)) throw new Error('project, plan and out are required; choose at most one browser override.');
  const report = await runChecks(options);
  console.log(JSON.stringify({ status: report.status, scenarios: report.scenarios.length, report: resolve(options.out, 'report.json'), error: report.error ?? null }));
  return report.status === 'passed' ? 0 : report.status === 'not_run' ? 2 : 1;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).then(code => { process.exitCode = code; }).catch(error => { console.error(message(error)); process.exitCode = 1; });
}
