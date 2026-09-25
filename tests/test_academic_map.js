const assert = require('node:assert/strict');
const { aggregate } = require('../site/academic-map.js');
const pubs = [{ id: 'p1', year: 2026, venue_group: 'security' }, { id: 'p2', year: 2025, venue_group: '' }];
const nodes = [
  { id: 'a', name: 'A', country_code: 'USA', papers: ['p1', 'p2'] },
  { id: 'b', name: 'B', country_code: 'USA', papers: ['p1'] },
  { id: 'c', name: 'C', country_code: 'CHN', papers: ['p1'] },
  { id: 'd', name: 'Unknown', papers: ['p2'] },
];
const edges = [
  { source: 'a', target: 'b', papers: [pubs[0]] },
  { source: 'a', target: 'c', papers: [pubs[0]] },
  { source: 'b', target: 'c', papers: [pubs[0]] },
  { source: 'a', target: 'd', papers: [pubs[1]] },
];
let map = aggregate(nodes, edges, pubs, () => true);
assert.equal(map.countries.find(c => c.id === 'USA').count, 2);
assert.equal(map.countries.find(c => c.id === 'CHN').count, 1);
assert.equal(map.routes.find(r => r.source === 'CHN').count, 1, 'Multiple institution pairs must not inflate country coauthorship');
assert.equal(map.routes.find(r => r.source === 'CHN').pairs.length, 2);
assert.equal(map.unmapped, 1);
assert.ok(map.routes.every(r => r.source !== r.target), 'Map routes must not loop back to the same country');
map = aggregate(nodes, edges, pubs, p => p.year === 2025);
assert.equal(map.countries.length, 1);
assert.equal(map.countries[0].count, 1, 'Unscored preprints remain visible in all-category year view');
assert.equal(map.routes.length, 0);
map = aggregate(nodes, edges, pubs, p => p.venue_group === 'security', 'b');
assert.equal(map.unmapped, 0);
assert.equal(map.routes.find(r => r.source === 'CHN').pairs.length, 1, 'Focus uses only this institution’s edges');
map = aggregate(nodes.filter(n => n.id === 'a'), edges, pubs, () => true);
assert.equal(map.routes.length, 0, 'Search must not retain edges to excluded institutions');
assert.deepEqual(aggregate([], edges, pubs, () => true), { countries: [], routes: [], unmapped: 0 });
console.log('Academic map: deduplication, filtering, focus, unknown locations and empty state passed.');
