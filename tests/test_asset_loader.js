const assert = require('node:assert/strict');
const { createLoader } = require('../site/asset-loader.js');
(async () => {
  let calls = 0;
  const loader = createLoader(async () => { calls++; return { ok: true, json: async () => ({ title: '论文' }) }; });
  const [a, b] = await Promise.all([loader.load('paper.json'), loader.load('paper.json')]);
  assert.equal(calls, 1, 'Concurrent detail requests share one fetch');
  assert.strictEqual(a, b);
  await loader.load('paper.json');
  assert.equal(calls, 1, 'Reopening details uses the session cache');
  let attempts = 0;
  const retry = createLoader(async () => {
    attempts++;
    return attempts === 1 ? { ok: false, status: 503 } : { ok: true, json: async () => ({ recovered: true }) };
  });
  await assert.rejects(retry.load('retry.json'), /503/);
  assert.deepEqual(await retry.load('retry.json'), { recovered: true });
  assert.equal(attempts, 2);
  await assert.rejects(loader.load(''), /Missing/);
  console.log('Asset loader: concurrent deduplication, caching and retry passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
