(() => {
  "use strict";

  const data = window.PAPERNOTE_DATA;
  if (!data) {
    document.body.innerHTML = "<p style='padding:2rem'>缺少 site/data.js，请先运行 python3 scripts/build_site.py。</p>";
    return;
  }

  const state = {
    mode: "week",
    paperMode: "week",
    group: data.weeks[0]?.id || "all",
    query: "",
    sort: "recent",
    academicYear: "all",
    academicInstitution: "",
    dialogTrail: [],
    filtersExpanded: false,
    mapFocus: false,
  };

  const topicLabels = Object.fromEntries(
    Object.entries(data.taxonomy?.topics || {}).map(([id, item]) => [id, item.label])
  );

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const elements = {
    stats: $("#stats"),
    distribution: $("#distributionCard"),
    filterTitle: $("#filterTitle"),
    filterList: $("#filterList"),
    filterToggle: $("#filterToggle"),
    resultCount: $("#resultCount"),
    cardList: $("#cardList"),
    contentTitle: $("#contentTitle"),
    contentEyebrow: $("#contentEyebrow"),
    search: $("#searchInput"),
    sort: $("#sortSelect"),
    academicYear: $("#academicYear"),
    paperViewTabs: $("#paperViewTabs"),
    empty: $("#emptyState"),
    dialog: $("#paperDialog"),
    dialogContent: $("#dialogContent"),
    dialogBack: $(".dialog-back"),
  };

  const scholarsById = new Map(
    (data.scholar_names || data.academic?.scholars || []).map((scholar) => [scholar.id, scholar])
  );
  const scholarIdsByName = new Map();
  scholarsById.forEach((scholar) => {
    [scholar.name, scholar.publication_name].filter(Boolean).forEach((name) => {
      scholarIdsByName.set(name, scholar.id);
    });
  });
  const scholarIdsByPaperId = new Map(Object.entries(data.paper_authors || {}).map(([id, authors]) => [id, [...new Set(authors)]]));
  const papersById = new Map(data.papers.map(paper => [paper.id, paper]));
  const fullDetails = new Map();
  const searchWeeks = new Map();
  const searchCache = new WeakMap();
  let academicRequest;
  let dialogRequest = 0;
  let contentRequest = 0;

  async function ensureAcademic() {
    if (data.academic?.institutions) return;
    if (!academicRequest) academicRequest = window.PAPERNOTE_ASSETS.load(data.assets.academic).then(academic => {
      data.academic = academic;
      academic.scholars.forEach(scholar => scholarsById.set(scholar.id, scholar));
    }).catch(error => { academicRequest = null; throw error; });
    return academicRequest;
  }

  function loadContent(task) {
    const request = ++contentRequest;
    elements.empty.hidden = true;
    elements.cardList.innerHTML = '<p class="load-status" role="status">正在加载内容…</p>';
    task.then(() => { if (request === contentRequest) render(); }).catch(() => {
      if (request !== contentRequest) return;
      elements.cardList.innerHTML = '<p class="load-status" role="status">内容加载失败，请检查网络后重试。</p><button type="button" class="filter-toggle" id="retryContent">重新加载</button>';
      $("#retryContent").addEventListener("click", render);
    });
  }


  const escapeHtml = (value = "") => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const dateText = (value) => {
    if (!value) return "";
    if (/^\d{4}$/.test(value)) return `${value} 年`;
    const matched = value.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
    if (!matched) return value;
    const [, year, month, day] = matched;
    const date = new Date(`${year}-${month}-${day || "01"}T00:00:00+08:00`);
    const options = day
      ? { year: "numeric", month: "short", day: "numeric" }
      : { year: "numeric", month: "short" };
    return new Intl.DateTimeFormat("zh-CN", options).format(date);
  };

  const statusLabel = (status = "") => {
    if (status.includes("preprint")) return "预印";
    if (status.includes("accepted") || status.includes("prepublication")) return "接收";
    return status;
  };

  const paperStatusLabel = (paper) => {
    const weeklyStatus = paper.details?.venue_status || "";
    return weeklyStatus.includes("｜")
      ? weeklyStatus.split("｜").at(-1)
      : statusLabel(paper.status);
  };

  const paperTags = (paper) => {
    const keywords = paper.details?.keywords
      ? paper.details.keywords.split(/[、，,]/).map((item) => item.trim()).filter(Boolean)
      : [];
    return keywords.length
      ? keywords
      : (paper.topics || []).map((topic) => topicLabels[topic] || topic);
  };

  const searchable = (item) => {
    if (!searchCache.has(item)) searchCache.set(item, JSON.stringify(item).toLocaleLowerCase("zh-CN"));
    return searchCache.get(item);
  };

  function renderStats() {
    const stats = [
      ["收录论文", data.counts.papers],
      ["缓存精读", data.counts.cached],
      ["主领域", data.counts.themes],
      ["学术单位", data.counts.institutions || 0],
      ["行业观点", data.counts.viewpoints],
    ];
    elements.stats.innerHTML = stats.map(([label, value]) =>
      `<div class="stat"><dt>${label}</dt><dd>${value}</dd></div>`
    ).join("");
  }

  const distributionColors = [
    "#cb694f", "#d9954e", "#d0b562", "#6f9a88",
    "#668ba2", "#85749a", "#ad6c82", "#7b8f73",
  ];

  const countBy = (items, labelFor) => {
    const counts = new Map();
    items.forEach((item) => {
      const label = labelFor(item) || "其他";
      counts.set(label, (counts.get(label) || 0) + 1);
    });
    return [...counts].map(([label, count]) => ({ label, count }))
      .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label, "zh-CN"));
  };

  const wholePercentages = (entries, total) => {
    if (!total) return entries.map(() => 0);
    const shares = entries.map((item, index) => {
      const exact = item.count / total * 100;
      return { index, value: Math.floor(exact), remainder: exact - Math.floor(exact) };
    });
    let unassigned = 100 - shares.reduce((sum, item) => sum + item.value, 0);
    [...shares]
      .sort((a, b) => b.remainder - a.remainder || a.index - b.index)
      .slice(0, unassigned)
      .forEach((item) => { shares[item.index].value += 1; });
    return shares.map((item) => item.value);
  };

  const conferenceName = (paper) => ((paper.venues || ["其他 / 未标注"])[0] || "其他 / 未标注")
    .replace(/\s+20\d{2}\b/g, "")
    .trim();

  const viewpointOrganization = (item) => {
    const source = item.source || "其他";
    if (source.startsWith("Microsoft ")) return "Microsoft";
    if (source.startsWith("Google Threat Intelligence")) return "Google / Mandiant";
    return source;
  };

  function distributionForMode() {
    if (state.mode === "viewpoints") {
      return {
        kicker: "观点来源",
        summary: `${data.viewpoints.length} 条观点`,
        unit: "条",
        entries: countBy(data.viewpoints, viewpointOrganization),
      };
    }
    if (state.mode === "academic") {
      const categoryLabels = Object.fromEntries(
        (data.academic?.categories || []).map((item) => [item.id, item.label])
      );
      categoryLabels.security = "安全四大";
      categoryLabels.software = "软件工程";
      categoryLabels.ai = "人工智能";
      const publications = data.academic?.publications || [];
      return {
        kicker: "论文领域",
        summary: `${data.academic?.coverage?.scored_top_venue_papers || 0} 篇纳入顶会统计`,
        unit: "篇",
        entries: countBy(publications, (paper) => categoryLabels[paper.venue_group] || "预印 / 其他"),
      };
    }
    return {
      kicker: "论文来源",
      summary: `${data.counts.cached}/${data.counts.papers} 篇精读可用`,
      unit: "篇",
      entries: countBy(data.papers, conferenceName),
    };
  }

  function renderDistribution() {
    const distribution = distributionForMode();
    const total = distribution.entries.reduce((sum, item) => sum + item.count, 0);
    const percentages = wholePercentages(distribution.entries, total);
    let cursor = 0;
    const segments = distribution.entries.map((item, index) => {
      const start = cursor;
      cursor += total ? item.count / total * 100 : 0;
      return `${distributionColors[index % distributionColors.length]} ${start.toFixed(2)}% ${cursor.toFixed(2)}%`;
    });
    const ariaParts = distribution.entries.map((item, index) =>
      `${item.label} ${item.count}${distribution.unit}，占 ${percentages[index]}%`
    );

    elements.distribution.innerHTML = `
      <div class="distribution-head">
        <div>
          <p class="distribution-kicker">${escapeHtml(distribution.kicker)}</p>
          <strong>${escapeHtml(distribution.summary)}</strong>
        </div>
        <span>构成</span>
      </div>
      <div class="distribution-chart" role="img"
           aria-label="${escapeHtml(`${distribution.kicker}：${ariaParts.join("；")}`)}"
           style="background: conic-gradient(${segments.join(", ")})">
        <span><b>${total}</b><small>${distribution.unit}</small></span>
      </div>
      <ol class="distribution-legend">
        ${distribution.entries.map((item, index) => {
          return `
            <li>
              <i style="background:${distributionColors[index % distributionColors.length]}" aria-hidden="true"></i>
              <span title="${escapeHtml(item.label)}">${escapeHtml(item.label)}</span>
              <b>${item.count}</b>
              <small>${percentages[index]}%</small>
            </li>
          `;
        }).join("")}
      </ol>
    `;
  }

  function groupsForMode() {
    if (state.mode === "week") return data.weeks;
    if (state.mode === "theme") return data.themes;
    if (state.mode === "academic") {
      return [
        { id: "all", label: "全部学科领域", count: data.academic?.coverage?.scored_top_venue_papers || 0 },
        ...(data.academic?.categories || []).map((item) => ({
          ...item,
          count: (data.academic?.publications || []).filter((paper) => paper.venue_group === item.id).length,
        })),
      ];
    }
    const sourceTypes = new Map();
    data.viewpoints.forEach((item) => {
      sourceTypes.set(item.source_type, (sourceTypes.get(item.source_type) || 0) + 1);
    });
    return [
      { id: "all", label: "全部来源", count: data.viewpoints.length },
      ...[...sourceTypes].map(([id, count]) => ({ id, label: id, count })),
    ];
  }

  function renderFilters() {
    const groups = groupsForMode();
    elements.filterTitle.textContent =
      state.mode === "week"
        ? "周次"
        : state.mode === "theme"
          ? "主领域"
          : state.mode === "academic"
            ? "学科领域"
            : "来源类型";
    elements.filterToggle.hidden = groups.length <= 5;
    elements.filterToggle.setAttribute("aria-expanded", String(state.filtersExpanded));
    elements.filterToggle.textContent = state.filtersExpanded ? "收起 · 显示前 5 条" : `展开全部 ${groups.length} 条`;
    elements.filterList.innerHTML = (state.filtersExpanded ? groups : groups.slice(0, 5)).map((group) => `
      <button class="filter-button ${state.group === group.id ? "is-active" : ""}"
              type="button" data-group="${escapeHtml(group.id)}">
        <span>${escapeHtml(group.label)}</span>
        <span class="filter-count">${group.count}</span>
      </button>
    `).join("");
    $$(".filter-button").forEach((button) => {
      button.addEventListener("click", () => {
        state.group = button.dataset.group;
        render();
      });
    });
  }

  function visiblePapers() {
    const query = state.query.toLocaleLowerCase("zh-CN");
    let papers = data.papers.filter((paper) => {
      const inGroup = state.mode === "week"
        ? paper.week === state.group
        : paper.theme === state.group;
      return inGroup && (!query || (searchWeeks.get(paper.week)?.[paper.id] || searchable(paper)).includes(query));
    });
    papers = [...papers].sort((a, b) => {
      if (state.sort === "title") return a.title.localeCompare(b.title);
      return (b.card_date?.value || "").localeCompare(a.card_date?.value || "")
        || a.title.localeCompare(b.title);
    });
    return papers;
  }

  function paperSummary(paper) {
    return paper.details?.question
      || paper.details?.recommendation
      || `${paper.authors.slice(0, 3).join("、")}${paper.authors.length > 3 ? " 等" : ""}`;
  }

  function glossaryMarkup(entries = []) {
    if (!entries.length) return "";
    const rows = entries.map((entry) => `
      <div><dt>${escapeHtml(entry.term)}</dt><dd>${escapeHtml(entry.definition)}</dd></div>
    `).join("");
    return `<section class="detail-section glossary-section"><h3>名词解释</h3><dl>${rows}</dl></section>`;
  }

  function scholarButton(name, extraClass = "") {
    const scholarId = scholarIdsByName.get(name);
    if (!scholarId) return `<span>${escapeHtml(name)}</span>`;
    const scholar = scholarsById.get(scholarId);
    return `<button class="scholar-link ${extraClass}" type="button" data-open-scholar="${escapeHtml(scholarId)}">${escapeHtml(scholar?.name || name)}</button>`;
  }

  function scholarButtonById(scholarId, extraClass = "") {
    const scholar = scholarsById.get(scholarId);
    return scholar
      ? `<button class="scholar-link ${extraClass}" type="button" data-open-scholar="${escapeHtml(scholarId)}">${escapeHtml(scholar.name)}</button>`
      : "";
  }

  function paperAuthorButtons(paper) {
    const scholarIds = scholarIdsByPaperId.get(paper.id);
    return scholarIds?.length
      ? scholarIds.map((scholarId) => scholarButtonById(scholarId)).filter(Boolean).join("、")
      : paper.authors.map((author) => scholarButton(author)).join("、");
  }

  function renderPaperCard(paper) {
    return `
      <article class="paper-card" data-paper="${escapeHtml(paper.id)}">
        <div class="card-meta">
          <strong>${escapeHtml(paper.week)}</strong>
          <span>${escapeHtml((paper.venues || []).join(" · "))}</span><br>
          <span title="${escapeHtml(paper.card_date?.label || "论文公开时间")}">${dateText(paper.card_date?.value)}</span>
        </div>
        <div class="card-body">
          <h3><button class="paper-title-button" type="button" data-open-paper="${escapeHtml(paper.id)}">${escapeHtml(paper.title)}</button></h3>
          <p class="paper-author-list">${paperAuthorButtons(paper)}</p>
          <p class="card-summary">${escapeHtml(paperSummary(paper))}</p>
          <div class="tags">
            <span class="tag domain">${escapeHtml(paper.theme_label)}</span>
            ${paperTags(paper).slice(0, 4).map((topic) => `<span class="tag">${escapeHtml(topic)}</span>`).join("")}
            <span class="tag status">${escapeHtml(paperStatusLabel(paper))}</span>
          </div>
        </div>
      </article>
    `;
  }

  function renderViewpointCard(item) {
    return `
      <article class="paper-card viewpoint-card">
        <div class="card-meta">
          <strong>${dateText(item.published_at)}</strong>
          <span>${escapeHtml(item.source)}</span>
        </div>
        <div class="card-body">
          <h3><a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.title)}</a></h3>
          <p class="card-summary">${escapeHtml(item.summary)}</p>
          <dl class="viewpoint-evidence">
            <div><dt>内容类型</dt><dd>${escapeHtml(item.content_type)}</dd></div>
            <div><dt>证据基础</dt><dd>${escapeHtml(item.evidence_basis)}</dd></div>
            <div><dt>局限</dt><dd>${escapeHtml(item.limitations)}</dd></div>
            <div><dt>利益相关</dt><dd>${escapeHtml(item.commercial_interest)}</dd></div>
          </dl>
          <ul class="highlights">
            ${item.highlights.map((point) => `<li>${escapeHtml(point)}</li>`).join("")}
          </ul>
          <div class="tags">${item.topics.map((topic) => `<span class="tag">${escapeHtml(topic)}</span>`).join("")}</div>
          <a class="source-link" href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">阅读原文 ↗</a>
          ${item.project_url ? `<a class="source-link" href="${escapeHtml(item.project_url)}" target="_blank" rel="noreferrer">项目仓库 ↗</a>` : ""}
        </div>
      </article>
    `;
  }

  function academicScore(item) {
    const years = state.academicYear === "all"
      ? Object.values(item.annual_scores || {})
      : [item.annual_scores?.[state.academicYear]].filter(Boolean);
    return years.reduce((sum, year) =>
      sum + (state.group === "all" ? (year.total || 0) : (year[state.group] || 0)), 0);
  }

  function academicPaperMatches(paper) {
    const yearMatches = state.academicYear === "all" || String(paper.year) === state.academicYear;
    const categoryMatches = state.group === "all" || paper.venue_group === state.group;
    return yearMatches && categoryMatches;
  }

  function renderWorldMap(institutions, edges, publications) {
    const world = window.PAPERNOTE_WORLD || [];
    const geography = new Map(world.map(country => [country.id, country]));
    const map = window.PAPERNOTE_MAP.aggregate(institutions, edges, publications, academicPaperMatches,
      state.mapFocus ? state.academicInstitution : "");
    const counts = new Map(map.countries.map(country => [country.id, country]));
    const max = Math.max(1, ...map.countries.map(country => country.count));
    const countries = [...map.countries].sort((a, b) => b.count - a.count);
    const routes = map.routes;
    const countryName = id => geography.get(id)?.name || id;
    const focusName = institutions.find(item => item.id === state.academicInstitution)?.name || "";
    return `<p class="map-scope">${state.mapFocus ? `${escapeHtml(focusName)} · 合作关系` : "全部单位 · 合作关系"}${routes.length ? "" : " · 当前范围暂无可定位的合作连线"}</p><div class="world-map-board">
      <div class="map-summary"><strong>${countries.length}</strong> 个国家 / 地区 <span>·</span> ${map.unmapped} 个单位待补所在地</div>
      <svg class="world-map" viewBox="0 0 900 380" role="group" aria-label="全球论文分布与合作地图">
        <g class="map-grid" aria-hidden="true">${[-60, -30, 0, 30, 60].map(lat => `<path d="M0,${(85-lat)*2.5}H900"/>`).join("")}${[-120,-60,0,60,120].map(lon => `<path d="M${(lon+180)*2.5},0V380"/>`).join("")}</g>
        <g>${world.map(country => {
          const count = counts.get(country.id)?.count || 0;
          const fill = count ? `hsl(165 32% ${83 - 52 * (max === 1 ? 1 : Math.sqrt((count - 1) / (max - 1)))}%)` : "#e4e9e2";
          return `<path class="map-land" d="${country.path}" fill="${fill}" ${count ? `data-map-country="${country.id}" role="button" tabindex="0" aria-label="${escapeHtml(country.name)}：${count} 篇论文"` : ""}><title>${escapeHtml(country.name)} · ${count ? `${count} 篇库内论文` : "暂无已定位论文"}</title></path>`;
        }).join("")}</g>
        <g class="map-routes">${routes.map(route => {
          const a = geography.get(route.source), b = geography.get(route.target);
          if (!a || !b) return "";
          const distance = Math.hypot(a.x-b.x,a.y-b.y);
          const path = `M${a.x},${a.y}Q${(a.x+b.x)/2},${Math.max(8,(a.y+b.y)/2-Math.min(110,distance*.3))} ${b.x},${b.y}`;
          return `<path data-route-source="${route.source}" data-route-target="${route.target}" d="${path}" style="stroke-width:${Math.min(1.8, 0.45 + 0.3 * Math.sqrt(route.count))}"><title>${escapeHtml(countryName(route.source))} ↔ ${escapeHtml(countryName(route.target))}：${route.count} 篇共同论文；${route.pairs.length} 组单位合作</title></path>`;
        }).join("")}</g>
        <g>${countries.filter(country => !geography.get(country.id)?.path).map(country => {
          const point = geography.get(country.id);
          if (!point) return "";
          return `<text class="map-small-country" data-map-country="${country.id}" x="${point.x}" y="${point.y}" tabindex="0" role="button" aria-label="${escapeHtml(point.name)}：${country.count} 篇论文">${escapeHtml(point.name)}</text>`;
        }).join("")}</g>
      </svg>
      <div class="map-legend"><span><i class="no-data"></i>暂无已定位论文</span><span>1 篇</span><i class="color-scale"></i><span>${max} 篇</span><span class="route-key">⌒ 跨国 / 地区合作</span></div>
    </div>
    <p class="sr-only map-hover-status" role="status"></p>`;
  }

  function bindMapHover() {
    const board = $(".world-map");
    if (!board) return;
    const status = $(".map-hover-status");
    const paths = [...board.querySelectorAll(".map-routes path")];
    const countries = [...board.querySelectorAll("[data-map-country]")];
    const routesByCountry = new Map();
    paths.forEach(path => {
      new Set([path.dataset.routeSource, path.dataset.routeTarget]).forEach(code => {
        if (!routesByCountry.has(code)) routesByCountry.set(code, []);
        routesByCountry.get(code).push(path);
      });
    });
    let active = "";
    function show(code) {
      if (code === active) return;
      (routesByCountry.get(active) || []).forEach(path => path.classList.remove("is-visible"));
      active = code;
      const visible = routesByCountry.get(code) || [];
      visible.forEach(path => path.classList.add("is-visible"));
      countries.forEach(node => node.classList.toggle("is-selected", node.dataset.mapCountry === code));
      const name = countries.find(node => node.dataset.mapCountry === code)?.getAttribute("aria-label");
      status.textContent = code ? `${name || code} · ${visible.length ? `${visible.length} 条合作连线` : "当前范围暂无可定位的合作连线"}` : "";
    }
    countries.forEach(node => {
      node.addEventListener("pointerenter", event => { if (event.pointerType !== "touch") show(node.dataset.mapCountry); });
      node.addEventListener("pointerleave", event => { if (event.pointerType !== "touch") show(""); });
      node.addEventListener("focus", () => show(node.dataset.mapCountry));
      node.addEventListener("blur", () => show(""));
      node.addEventListener("pointerdown", event => {
        if (event.pointerType === "touch") { event.preventDefault(); show(active === node.dataset.mapCountry ? "" : node.dataset.mapCountry); }
      });
      node.addEventListener("keydown", event => {
        if (event.key === "Escape") show("");
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); show(node.dataset.mapCountry); }
      });
    });
    board.addEventListener("pointerleave", event => { if (event.pointerType !== "touch") show(""); });
    board.addEventListener("pointerdown", event => { if (!event.target.closest("[data-map-country]")) show(""); });
  }

  function renderAcademic() {
    if (!data.academic?.institutions) { loadContent(ensureAcademic()); return; }
    const academic = data.academic || {};
    const query = state.query.toLocaleLowerCase("zh-CN");
    const matchingIds = new Set((academic.publications || []).filter(academicPaperMatches).map(paper => paper.id));
    const institutions = [...(academic.institutions || [])]
      .filter((item) => !query || searchable(item).includes(query))
      .map((item) => ({ ...item, score: academicScore(item) }))
      .filter((item) => item.papers.some(id => matchingIds.has(id)))
      .sort((a, b) => b.score - a.score || b.papers.length - a.papers.length || a.name.localeCompare(b.name));
    const scholars = [...(academic.scholars || [])]
      .filter((item) => !query || searchable(item).includes(query))
      .map((item) => ({ ...item, score: academicScore(item) }))
      .filter((item) => item.papers.some(id => matchingIds.has(id)))
      .sort((a, b) => b.score - a.score || b.papers.length - a.papers.length || a.name.localeCompare(b.name));
    const nodeIds = new Set(institutions.map((item) => item.id));
    const edges = (academic.collaborations || []).filter((edge) =>
      nodeIds.has(edge.source)
      && nodeIds.has(edge.target)
      && edge.papers.some(academicPaperMatches)
    );
    if (!state.academicInstitution || !institutions.some((item) => item.id === state.academicInstitution)) {
      state.academicInstitution = institutions[0]?.id || "";
    }
    const countryRanking = window.PAPERNOTE_MAP.aggregate(institutions, [], academic.publications || [], academicPaperMatches).countries
      .sort((a, b) => b.count - a.count || a.id.localeCompare(b.id));
    const countryNames = new Map((window.PAPERNOTE_WORLD || []).map(item => [item.id, item.name]));
    const selected = institutions.find((item) => item.id === state.academicInstitution);
    const partners = selected
      ? edges.filter((edge) => edge.source === selected.id || edge.target === selected.id)
        .map((edge) => ({
          id: edge.source === selected.id ? edge.target : edge.source,
          weight: edge.papers.filter(academicPaperMatches).length,
        }))
        .map((item) => ({
          ...item,
          name: institutions.find((institution) => institution.id === item.id)?.name || item.id,
        }))
        .sort((a, b) => b.weight - a.weight || a.name.localeCompare(b.name))
      : [];

    elements.contentEyebrow.textContent = "ACADEMIC NETWORK";
    elements.contentTitle.textContent = "学术关系";
    elements.resultCount.textContent = `${institutions.length} 个单位 · ${scholars.length} 位学者`;
    elements.sort.hidden = true;
    elements.academicYear.hidden = false;
    elements.empty.hidden = institutions.length > 0;
    elements.cardList.innerHTML = institutions.length ? `
      <section class="network-section" aria-label="学术合作关系">
        <div class="map-controls">
          <label>查看单位 <select id="mapInstitution" aria-label="查看单位">${institutions.map(item => `<option value="${escapeHtml(item.id)}" ${item.id === state.academicInstitution ? "selected" : ""}>${escapeHtml(item.name)}</option>`).join("")}</select></label>
          <button type="button" id="mapFocus" aria-pressed="${state.mapFocus}">${state.mapFocus ? "显示全部合作" : "展开该单位的合作"}</button>
        </div>
        ${selected ? `
          <article class="network-detail">
            <div><p class="eyebrow">SELECTED GROUP</p><h3>${escapeHtml(selected.name)}</h3>
              <p>${selected.score} 分 · ${selected.papers.filter(id => matchingIds.has(id)).length} 篇当前筛选论文 · ${selected.scholars.length} 位关联学者</p>
            </div>
            <div><strong>关联学者</strong><p>${selected.scholars.slice(0, 16).map((name) => scholarButton(name)).join("、")}</p></div>
            <div><strong>主要合作单位</strong><p>${partners.length ? partners.map((item) => `<button class="scholar-link" type="button" data-map-institution="${escapeHtml(item.id)}">${escapeHtml(item.name)}（${item.weight}）</button>`).join("、") : "当前筛选下暂无跨单位合作边"}</p></div>
          </article>` : ""}
        ${renderWorldMap(institutions, edges, academic.publications || [])}
      </section>
      <section class="rankings">
        <div>
          <div class="subsection-heading compact"><div><p class="eyebrow">COUNTRIES / REGIONS</p><h3>国家 / 地区排名</h3></div></div>
          <ol class="ranking-list country-ranking">
            ${countryRanking.slice(0, 10).map((item, index) => `
              <li><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(countryNames.get(item.id) || item.id)}</strong>
              <small>${item.institutions.length} 个单位 · 去重论文数（含预印）</small></div><b>${item.count}</b></li>
            `).join("")}
          </ol>
        </div>
        <div>
          <div class="subsection-heading compact"><div><p class="eyebrow">INSTITUTIONS</p><h3>单位优先检索序列</h3></div></div>
          <ol class="ranking-list">
            ${institutions.slice(0, 10).map((item, index) => `
              <li><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(item.name)}</strong>
              <small>${item.scholars.length} 位学者 · ${item.papers.length} 篇库内论文</small></div><b>${item.score}</b></li>
            `).join("")}
          </ol>
        </div>
        <div>
          <div class="subsection-heading compact"><div><p class="eyebrow">SCHOLARS</p><h3>学者优先检索序列</h3></div></div>
          <ol class="ranking-list">
            ${scholars.slice(0, 10).map((item, index) => `
              <li><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${scholarButton(item.name, "ranking-scholar-link")}</strong>
              <small>${item.institutions.map(escapeHtml).join(" · ")}</small></div><b>${item.score}</b></li>
            `).join("")}
          </ol>
        </div>
      </section>
    ` : "";
    $("#mapInstitution")?.addEventListener("change", (event) => {
      state.academicInstitution = event.target.value;
      state.mapFocus = true;
      renderAcademic();
    });
    $("#mapFocus")?.addEventListener("click", () => {
      state.mapFocus = !state.mapFocus;
      renderAcademic();
    });
    bindMapHover();
    $$("[data-map-institution]").forEach(button => button.addEventListener("click", () => {
      state.academicInstitution = button.dataset.mapInstitution;
      state.mapFocus = true;
      renderAcademic();
    }));
    bindScholarLinks(elements.cardList);
  }

  function renderContent() {
    ++contentRequest;
    elements.academicYear.hidden = state.mode !== "academic";
    elements.paperViewTabs.hidden = !["week", "theme"].includes(state.mode);
    if (state.mode === "academic") {
      renderAcademic();
      return;
    }
    if (state.mode === "viewpoints") {
      const query = state.query.toLocaleLowerCase("zh-CN");
      const items = data.viewpoints
        .filter((item) =>
          (state.group === "all" || item.source_type === state.group)
          && (!query || searchable(item).includes(query))
        )
        .sort((a, b) =>
          b.published_at.localeCompare(a.published_at)
          || a.title.localeCompare(b.title, "zh-CN")
        );
      elements.contentEyebrow.textContent = "INDUSTRY NOTES";
      elements.contentTitle.textContent = "行业观点";
      elements.resultCount.textContent = `${items.length} 条`;
      elements.cardList.innerHTML = items.map(renderViewpointCard).join("");
      elements.sort.hidden = true;
      elements.empty.hidden = items.length > 0;
      return;
    }

    if (state.query) {
      const weeks = [...new Set(data.papers.filter(paper => state.mode === "week" ? paper.week === state.group : paper.theme === state.group).map(paper => paper.week))];
      const missing = weeks.filter(week => !searchWeeks.has(week));
      if (missing.length) {
        loadContent(Promise.all(missing.map(async week => {
          const text = await window.PAPERNOTE_ASSETS.load(data.assets.search[week]);
          searchWeeks.set(week, Object.fromEntries(Object.entries(text).map(([id, value]) => [id, value.toLocaleLowerCase("zh-CN")])));
        })));
        return;
      }
    }
    const papers = visiblePapers();
    const group = groupsForMode().find((item) => item.id === state.group);
    elements.contentEyebrow.textContent = state.mode === "week" ? "WEEKLY READING" : "TOPIC COLLECTION";
    elements.contentTitle.textContent = group?.label || "论文";
    elements.resultCount.textContent = `${papers.length} 篇`;
    elements.cardList.innerHTML = papers.map(renderPaperCard).join("");
    elements.sort.hidden = false;
    elements.empty.hidden = papers.length > 0;

    $$(".paper-card[data-paper]").forEach((card) => {
      card.addEventListener("click", (event) => {
        if (event.target.closest("button, a")) return;
        openDialogEntity("paper", card.dataset.paper, true);
      });
    });
    bindEntityLinks(elements.cardList);
  }

  function detailSection(label, value) {
    return value ? `<section class="detail-section"><h3>${label}</h3><p>${escapeHtml(value)}</p></section>` : "";
  }

  function affiliationSection(value) {
    if (!value) return "";
    const rows = value.split("；").map((row) => {
      const [institution, authorText = ""] = row.split("：", 2);
      const authors = authorText.split("、").filter(Boolean).map((name) => scholarButton(name)).join("、");
      return `<li><strong>${escapeHtml(institution)}</strong>${authors ? `：${authors}` : ""}</li>`;
    });
    return `<ul class="affiliation-list dialog-affiliations" aria-label="作者所属单位">${rows.join("")}</ul>`;
  }

  function renderPaperDialog(id) {
    const paper = papersById.get(id);
    if (!paper) return false;
    const details = fullDetails.get(id) || paper.details || {};
    const sourceLinks = details.original_links?.length
      ? details.original_links
      : (paper.urls || []).map((url, index) => ({
          label: index ? `相关链接 ${index + 1}` : "访问论文来源",
          url,
        }));
    elements.dialogContent.innerHTML = `
      <p class="eyebrow">${escapeHtml(paper.theme_label)} · ${escapeHtml(paper.week)}</p>
      <h2 class="dialog-title">${escapeHtml(paper.title)}</h2>
      ${details.author_affiliations ? affiliationSection(details.author_affiliations) : `<p class="dialog-affiliations">${paperAuthorButtons(paper)}</p>`}
      <p class="dialog-byline">
        ${escapeHtml(details.venue_status || `${(paper.venues || []).join(" · ")} · ${paperStatusLabel(paper)}`)}
      </p>
      ${details.easycatch?.length ? `<section class="detail-section easycatch"><h3>Easycatch</h3>${details.easycatch.map(paragraph => `<p>${escapeHtml(paragraph)}</p>`).join("")}</section>` : ""}
      ${detailSection("方向", details.direction)}
      ${detailSection("关键词", details.keywords)}
      ${glossaryMarkup(details.glossary)}
      ${detailSection("公开或更新时间", details.public_date)}
      ${detailSection("核心问题", details.question)}
      ${detailSection("方法与贡献", details.method)}
      ${detailSection("方法示例", details.method_example)}
      ${detailSection("实验与证据", details.evidence)}
      ${detailSection("局限与风险", details.limitations)}
      ${detailSection("实践关系", details.practice)}
      ${detailSection("推荐理由", details.recommendation)}
      ${!paper.cached ? detailSection("缓存状态", "索引中已有元数据，但当前周报缓存里尚无对应精读。") : ""}
      <div class="dialog-actions">
        ${sourceLinks.map((link, index) => `
          <a class="${index ? "secondary" : ""}" href="${escapeHtml(link.url)}" target="_blank" rel="noreferrer">
            ${escapeHtml(link.label || `原文链接 ${index + 1}`)} ↗
          </a>
        `).join("")}
      </div>
    `;
    return true;
  }

  function renderScholarDialog(id) {
    const scholar = scholarsById.get(id);
    if (!scholar) return false;
    elements.dialogContent.innerHTML = `
      <p class="eyebrow">SCHOLAR PROFILE · VERIFIED LIBRARY VIEW</p>
      <h2 class="dialog-title">${escapeHtml(scholar.name)}</h2>
      <p class="dialog-byline">
        ${scholar.publication_name && scholar.publication_name !== scholar.name
          ? `论文署名：${escapeHtml(scholar.publication_name)}<br>`
          : ""}
        ${scholar.institutions.map(escapeHtml).join(" · ") || "单位待核验"}
      </p>
      <dl class="dialog-scholar-stats">
        <div><dt>库内论文</dt><dd>${scholar.papers.length}</dd></div>
        <div><dt>已核验计分</dt><dd>${scholar.verified_score || 0}</dd></div>
        <div><dt>最近年份</dt><dd>${scholar.recent_papers?.[0]?.year || "—"}</dd></div>
      </dl>
      <section class="detail-section">
        <h3>最近入库</h3>
        <ol class="dialog-recent-papers">
          ${(scholar.recent_papers || []).slice(0, 3).map((paper) => `
            <li>
              <button type="button" data-open-paper="${escapeHtml(paper.id)}">${escapeHtml(paper.title)}</button>
              <small>${escapeHtml(paper.venue || "")}${paper.year ? ` · ${paper.year}` : ""}</small>
            </li>
          `).join("") || "<li>暂无可展示论文</li>"}
        </ol>
      </section>
      <div class="dialog-actions">
        ${scholar.homepage
          ? `<a href="${escapeHtml(scholar.homepage)}" target="_blank" rel="noreferrer">访问个人主页 ↗</a>`
          : `<span class="homepage-pending">个人主页待核验</span>`}
      </div>
    `;
    return true;
  }

  async function renderDialogEntity() {
    const current = state.dialogTrail.at(-1);
    if (!current) return;
    const request = ++dialogRequest;
    elements.dialogBack.hidden = state.dialogTrail.length < 2;
    if (!elements.dialog.open) elements.dialog.showModal();
    elements.dialogContent.innerHTML = '<p role="status">正在加载详情…</p>';
    try {
      if (current.type === "scholar") await ensureAcademic();
      else if (!fullDetails.has(current.id)) {
        const paper = papersById.get(current.id);
        if (!paper) throw new Error("Unknown paper");
        fullDetails.set(current.id, await window.PAPERNOTE_ASSETS.load(paper.details_url));
      }
    } catch (error) {
      if (request !== dialogRequest || !elements.dialog.open) return;
      elements.dialogContent.innerHTML = '<p role="status">详情加载失败，请检查网络后重试。</p><button type="button" id="retryDetail">重新加载</button>';
      $("#retryDetail").addEventListener("click", renderDialogEntity);
      return;
    }
    if (request !== dialogRequest || !elements.dialog.open) return;
    const rendered = current.type === "paper"
      ? renderPaperDialog(current.id)
      : renderScholarDialog(current.id);
    if (!rendered) return;
    elements.dialogBack.hidden = state.dialogTrail.length < 2;
    bindEntityLinks(elements.dialogContent);
    if (!elements.dialog.open) elements.dialog.showModal();
    elements.dialog.scrollTop = 0;
  }

  function openDialogEntity(type, id, reset = false) {
    const key = `${type}:${id}`;
    if (reset) state.dialogTrail = [];
    const existingIndex = state.dialogTrail.findIndex((item) => item.key === key);
    if (existingIndex >= 0) {
      state.dialogTrail = state.dialogTrail.slice(0, existingIndex + 1);
    } else {
      state.dialogTrail.push({ type, id, key });
    }
    renderDialogEntity();
  }

  function bindScholarLinks(container) {
    container.querySelectorAll("[data-open-scholar]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        openDialogEntity("scholar", button.dataset.openScholar, !elements.dialog.open);
      });
    });
  }

  function bindEntityLinks(container) {
    bindScholarLinks(container);
    container.querySelectorAll("[data-open-paper]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        openDialogEntity("paper", button.dataset.openPaper, !elements.dialog.open);
      });
    });
  }

  elements.filterToggle.addEventListener("click", () => {
    state.filtersExpanded = !state.filtersExpanded;
    renderFilters();
  });

  function render() {
    renderDistribution();
    renderFilters();
    renderContent();
  }

  $$(".mode-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      state.mode = tab.dataset.section === "papers" ? state.paperMode : tab.dataset.section;
      state.filtersExpanded = false;
      state.group = groupsForMode()[0]?.id || "all";
      if (state.mode === "academic") state.academicInstitution = "";
      $$(".mode-tab").forEach((item) => item.classList.toggle("is-active", item === tab));
      render();
    });
  });
  $$(".paper-view-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      state.paperMode = tab.dataset.mode;
      state.mode = state.paperMode;
      state.filtersExpanded = false;
      state.group = groupsForMode()[0]?.id || "all";
      $$(".paper-view-tab").forEach((item) => item.classList.toggle("is-active", item === tab));
      render();
    });
  });

  let searchTimer;
  elements.search.addEventListener("input", () => {
    state.query = elements.search.value.trim();
    ++contentRequest;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(renderContent, 150);
  });
  elements.sort.addEventListener("change", () => {
    state.sort = elements.sort.value;
    renderContent();
  });
  elements.academicYear.innerHTML = [
    `<option value="all">全部年份</option>`,
    ...(data.academic?.years || []).map((year) => `<option value="${escapeHtml(year)}">${escapeHtml(year)} 年</option>`),
  ].join("");
  elements.academicYear.addEventListener("change", () => {
    state.academicYear = elements.academicYear.value;
    state.academicInstitution = "";
    renderAcademic();
  });
  $("#clearSearch").addEventListener("click", () => {
    state.query = "";
    elements.search.value = "";
    renderContent();
    elements.search.focus();
  });
  elements.dialogBack.addEventListener("click", () => {
    if (state.dialogTrail.length > 1) {
      state.dialogTrail.pop();
      renderDialogEntity();
    }
  });
  $(".dialog-close").addEventListener("click", () => elements.dialog.close());
  elements.dialog.addEventListener("close", () => {
    ++dialogRequest;
    state.dialogTrail = [];
    elements.dialogBack.hidden = true;
  });
  elements.dialog.addEventListener("click", (event) => {
    if (event.target === elements.dialog) elements.dialog.close();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== elements.search) {
      event.preventDefault();
      elements.search.focus();
    }
  });

  renderStats();
  render();
})();
