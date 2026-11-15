import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, copyFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { validatePlan, staticFile, serve, runChecks, withTimeout } from './check.mjs';

const valid = () => ({ schema: 1, scenarios: [{ id: 'boot', steps: [{ action: 'expectText', selector: 'h1', equals: 'Game' }] }] });
async function fixture(t) {
  const root = await mkdtemp(join(tmpdir(), 'game-director-web-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  await writeFile(join(root, 'index.html'), '<h1>Game</h1>');
  return root;
}

test('nonempty assertion plan is accepted', () => assert.equal(validatePlan(valid()).assertions, 1));
test('an observation that never settles is interrupted', async () => {
  await assert.rejects(() => withTimeout(new Promise(() => {}), 25, 'observation'), /timed out/);
  assert.equal(await withTimeout(Promise.resolve(7), 100, 'observation'), 7);
});
test('empty plans and screenshot-only scenarios cannot pass', () => {
  assert.throws(() => validatePlan({ schema: 1, scenarios: [] }));
  const p = valid(); p.scenarios[0].steps = [{ action: 'screenshot', name: 'boot' }];
  assert.throws(() => validatePlan(p), /no assertions/);
});
test('duplicate IDs, unknown steps, unbounded waits and invalid state paths fail', () => {
  const dup = valid(); dup.scenarios.push(structuredClone(dup.scenarios[0])); assert.throws(() => validatePlan(dup));
  for (const step of [{ action: 'forceWin' }, { action: 'wait', ms: 60000 }, { action: 'expectState', path: '__proto__.x', equals: 1 }]) {
    const p = valid(); p.scenarios[0].steps.unshift(step); assert.throws(() => validatePlan(p));
  }
});
test('viewport, finite values and touch requirements are validated', () => {
  const p = valid(); p.viewport = { width: 0, height: 800 }; assert.throws(() => validatePlan(p));
  const q = valid(); q.scenarios[0].steps.push({ action: 'expectState', path: 'energy', equals: Infinity }); assert.throws(() => validatePlan(q));
  const r = valid(); r.scenarios[0].steps.unshift({ action: 'tap', selector: 'button' }); assert.throws(() => validatePlan(r));
  r.touch = true; assert.equal(validatePlan(r).assertions, 1);
});
test('static files exclude secrets, traversal and unsupported files', async t => {
  const root = await fixture(t);
  await writeFile(join(root, '.env'), 'PRIVATE_FIXTURE');
  await writeFile(join(root, 'private.txt'), 'PRIVATE_FIXTURE');
  assert.equal(await staticFile(root, '/'), join(root, 'index.html'));
  for (const path of ['/.env', '/%2e%2e/private.txt', '/private.txt', '/bad%xx']) await assert.rejects(() => staticFile(root, path));
});
test('static server binds loopback, serves real bytes, records hashes and closes', async t => {
  const root = await fixture(t); const server = await serve(root);
  try {
    assert.match(server.url, /^http:\/\/127\.0\.0\.1:/);
    assert.equal(await (await fetch(server.url)).text(), '<h1>Game</h1>');
    assert.equal(server.served.get('index.html').length, 64);
    assert.equal((await fetch(server.url + '/.env')).status, 404);
  } finally { await server.close(); }
  await assert.rejects(() => fetch(server.url));
});

test('WASM is served with its exact MIME type and compiles through streaming', async t => {
  const root = await fixture(t);
  await writeFile(join(root, 'core.wasm'), new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]));
  const server = await serve(root);
  try {
    const response = await fetch(server.url + '/core.wasm');
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('content-type'), 'application/wasm');
    const { instance } = await WebAssembly.instantiateStreaming(response);
    assert.ok(instance instanceof WebAssembly.Instance);
  } finally { await server.close(); }
});

test('game data, Ogg and icons preserve binary bytes and typed headers', async t => {
  const root = await fixture(t);
  const data = new Uint8Array([0, 1, 127, 128, 255]);
  const types = { 'pack.pck': 'application/octet-stream', 'game.data': 'application/octet-stream',
    'game.bin': 'application/octet-stream', 'sound.ogg': 'audio/ogg', 'favicon.ico': 'image/x-icon' };
  for (const name of Object.keys(types)) await writeFile(join(root, name), data);
  await writeFile(join(root, 'core.wasm.gz'), data);
  const server = await serve(root);
  try {
    for (const [name, type] of Object.entries(types)) {
      const response = await fetch(server.url + '/' + name);
      assert.equal(response.status, 200, name);
      assert.equal(response.headers.get('content-type'), type, name);
      assert.deepEqual(new Uint8Array(await response.arrayBuffer()), data, name);
      assert.equal(server.served.get(name).length, 64);
    }
    assert.equal((await fetch(server.url + '/core.wasm.gz')).status, 404);
    assert.equal((await fetch(server.url + '/.env')).status, 404);
  } finally { await server.close(); }
});
test('invalid plan writes failed report before any browser is needed', async t => {
  const root = await fixture(t); const planPath = join(root, 'plan.json');
  await writeFile(planPath, '{"schema":1,"scenarios":[]}');
  const out = join(root, 'evidence');
  const report = await runChecks({ project: root, planPath, out });
  assert.equal(report.status, 'failed'); assert.deepEqual(report.scenarios, []);
  assert.equal(JSON.parse(await readFile(join(out, 'report.json'))).status, 'failed');
});
test('existing evidence is preserved rather than overwritten', async t => {
  const root = await fixture(t); const out = join(root, 'old'); await mkdir(out);
  await writeFile(join(out, 'report.json'), 'previous evidence');
  await assert.rejects(() => runChecks({ project: root, planPath: join(root, 'plan.json'), out }));
  assert.equal(await readFile(join(out, 'report.json'), 'utf8'), 'previous evidence');
});
test('isolated checker without Playwright exits 2 and records not_run', async t => {
  const root = await fixture(t); const planPath = join(root, 'plan.json');
  await writeFile(planPath, JSON.stringify(valid()));
  const script = join(root, 'isolated-check.mjs');
  await copyFile(fileURLToPath(new URL('./check.mjs', import.meta.url)), script);
  const out = join(root, 'missing-tool');
  const result = spawnSync(process.execPath, [script, '--project', root, '--plan', planPath, '--out', out], { encoding: 'utf8', timeout: 15000 });
  assert.equal(result.status, 2, result.stderr + result.stdout);
  const report = JSON.parse(await readFile(join(out, 'report.json')));
  assert.equal(report.status, 'not_run'); assert.equal(report.scenarios.length, 0);
});
