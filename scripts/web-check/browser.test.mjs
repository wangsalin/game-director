import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { runChecks } from './check.mjs';

// Separate opt-in browser tests. Keep reports, including failed attempts.
const root = process.env.WEB_CHECK_TEST_ROOT
  ? resolve(process.env.WEB_CHECK_TEST_ROOT) : await mkdtemp(join(tmpdir(), 'game-director-browser-'));
if (process.env.WEB_CHECK_TEST_ROOT) await mkdir(root);
const browser = process.env.WEB_CHECK_EXECUTABLE ? { executable: process.env.WEB_CHECK_EXECUTABLE } : {};

async function fixture(id, html, steps) {
  const directory = join(root, id); await mkdir(directory);
  const project = join(directory, 'project'); await mkdir(project);
  await writeFile(join(project, 'index.html'), html);
  const planPath = join(directory, 'plan.json');
  await writeFile(planPath, JSON.stringify({ schema: 1, scenarios: [{ id, steps }] }));
  return { project, planPath, out: join(directory, 'evidence'), ...browser };
}

test('Chromium instantiates streamed WASM and reads actual game-data bytes', async t => {
  const options = await fixture('wasm', `<!doctype html><meta charset="utf-8"><link rel="icon" href="data:,">
    <h1>Loading</h1><script type="module">
    const state = { scene: 'loading', bytes: [] };
    window.game = Object.freeze({ getState: () => structuredClone(state) });
    const { instance } = await WebAssembly.instantiateStreaming(fetch('core.wasm'));
    if (!(instance instanceof WebAssembly.Instance)) throw new Error('WASM was not instantiated');
    state.bytes = Array.from(new Uint8Array(await (await fetch('game.data')).arrayBuffer()));
    state.scene = 'ready'; document.querySelector('h1').textContent = 'WASM ready';
    </script>`, [
    { action: 'expectState', path: 'scene', equals: 'ready' },
    { action: 'expectState', path: 'bytes', equals: [0, 127, 128, 255] },
    { action: 'expectText', selector: 'h1', equals: 'WASM ready' },
  ]);
  await writeFile(join(options.project, 'core.wasm'), new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]));
  await writeFile(join(options.project, 'game.data'), new Uint8Array([0, 127, 128, 255]));
  t.diagnostic(`Reports retained at ${options.out}`);
  const report = await runChecks(options);
  assert.equal(report.status, 'passed', JSON.stringify(report));
  assert.deepEqual(report.scenarios[0].errors, []);
});

test('a successful DOM assertion cannot hide a real missing-resource error', async t => {
  const options = await fixture('missing-resource',
    '<!doctype html><link rel="icon" href="data:,"><h1>Ready</h1><script src="missing.js"></script>',
    [{ action: 'expectText', selector: 'h1', equals: 'Ready' }]);
  t.diagnostic(`Reports retained at ${options.out}`);
  const report = await runChecks(options);
  assert.equal(report.status, 'failed', JSON.stringify(report));
  assert.equal(report.scenarios[0]?.steps[0]?.status, 'passed');
  assert.ok(report.scenarios[0].errors.some(error => error.startsWith('HTTP 404:')));
});
