/* Shared map aggregation, also exercised by Node regression tests. */
(function (root) {
  function aggregate(institutions, collaborations, publications, matches, focus = '') {
    const nodes = new Map(institutions.map(item => [item.id, item]));
    const papers = new Map(publications.filter(matches).map(item => [item.id, item]));
    const countries = new Map();
    let unmapped = 0;
    for (const item of institutions) {
      const ids = item.papers.filter(id => papers.has(id));
      if (!ids.length) continue;
      if (!item.country_code) { unmapped++; continue; }
      if (!countries.has(item.country_code)) countries.set(item.country_code, { id: item.country_code, papers: new Set(), institutions: [] });
      const country = countries.get(item.country_code);
      ids.forEach(id => country.papers.add(id));
      country.institutions.push(item);
    }
    const routes = new Map();
    for (const edge of collaborations) {
      if (focus && edge.source !== focus && edge.target !== focus) continue;
      const left = nodes.get(edge.source), right = nodes.get(edge.target);
      if (!left?.country_code || !right?.country_code) continue;
      if (left.country_code === right.country_code) continue;
      const ids = edge.papers.filter(p => papers.has(p.id)).map(p => p.id);
      if (!ids.length) continue;
      const pair = [left.country_code, right.country_code].sort();
      const key = pair.join(':');
      if (!routes.has(key)) routes.set(key, { source: pair[0], target: pair[1], papers: new Set(), pairs: [] });
      const route = routes.get(key);
      ids.forEach(id => route.papers.add(id));
      route.pairs.push({ source: left.name, target: right.name, count: ids.length });
    }
    return { countries: [...countries.values()].map(c => ({ ...c, count: c.papers.size })), routes: [...routes.values()].map(r => ({ ...r, count: r.papers.size })), unmapped };
  }
  root.PAPERNOTE_MAP = { aggregate };
  if (typeof module !== 'undefined') module.exports = root.PAPERNOTE_MAP;
})(typeof window === 'undefined' ? globalThis : window);
