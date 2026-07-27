(() => {
  "use strict";

  const data = window.PAPERNOTE_DATA;
  if (!data) {
    document.body.innerHTML = "<p style='padding:2rem'>缺少 site/data.js，请先运行 python3 scripts/build_site.py。</p>";
    return;
  }

  const state = {
    mode: "theme",
    group: data.themes[0]?.id || "all",
    query: "",
    sort: "recent",
    academicYear: "all",
    academicInstitution: "",
  };

  const topicLabels = {
    "adaptive-red-teaming": "自适应红队",
    "agent-memory": "智能体记忆",
    "agent-security": "智能体安全",
    "android": "安卓",
    "api-misuse": "接口误用",
    "application-security": "应用安全",
    "authentication": "身份认证",
    "benchmark": "评测基准",
    "black-box-attack": "黑盒攻击",
    "coding-agent": "编程智能体",
    "data-integrity": "数据完整性",
    "desynchronization": "协议不同步",
    "em-side-channel": "电磁侧信道",
    "embedded-security": "嵌入式安全",
    "firmware-fuzzing": "固件模糊测试",
    "indirect-prompt-injection": "间接提示注入",
    "ios": "iOS",
    "ip-leakage": "网络地址泄漏",
    "java": "Java",
    "llm-security": "大模型安全",
    "mobile-security": "移动安全",
    "multi-agent-security": "多智能体安全",
    "network-side-channel": "网络侧信道",
    "operating-system-security": "操作系统安全",
    "passkeys": "通行密钥",
    "patch-mining": "补丁挖掘",
    "persistent-memory": "持久记忆",
    "persistent-state": "持久状态",
    "privacy": "隐私",
    "program-analysis": "程序分析",
    "prompt-injection": "提示注入",
    "protocol-security": "协议安全",
    "rag-security": "检索增强生成安全",
    "retrieval-poisoning": "检索投毒",
    "secure-code-generation": "安全代码生成",
    "self-hosted-agent": "自托管智能体",
    "sideloading": "侧载",
    "software-supply-chain": "软件供应链",
    "systematization-of-knowledge": "知识体系化",
    "tls": "TLS",
    "web-agent": "网页智能体",
    "web-to-app-tracking": "网页至应用追踪",
    "webauthn": "WebAuthn",
  };

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const elements = {
    stats: $("#stats"),
    filterTitle: $("#filterTitle"),
    filterList: $("#filterList"),
    resultCount: $("#resultCount"),
    cardList: $("#cardList"),
    contentTitle: $("#contentTitle"),
    contentEyebrow: $("#contentEyebrow"),
    search: $("#searchInput"),
    sort: $("#sortSelect"),
    academicYear: $("#academicYear"),
    empty: $("#emptyState"),
    dialog: $("#paperDialog"),
    dialogContent: $("#dialogContent"),
  };

  const escapeHtml = (value = "") => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const dateText = (value) => {
    if (!value) return "";
    const date = new Date(`${value}T00:00:00+08:00`);
    return new Intl.DateTimeFormat("zh-CN", { year: "numeric", month: "short", day: "numeric" }).format(date);
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

  const searchable = (item) => JSON.stringify(item).toLocaleLowerCase("zh-CN");

  function renderStats() {
    const stats = [
      ["收录论文", data.counts.papers],
      ["缓存精读", data.counts.cached],
      ["研究主题", data.counts.themes],
      ["学术单位", data.academic?.institutions?.length || 0],
      ["行业观点", data.counts.viewpoints],
    ];
    elements.stats.innerHTML = stats.map(([label, value]) =>
      `<div class="stat"><dt>${label}</dt><dd>${value}</dd></div>`
    ).join("");
    $("#cacheStatus").textContent = `${data.counts.cached} 篇论文可直接读取中文精读`;
    $("#generatedAt").textContent = new Date(data.generated_at).toLocaleString("zh-CN");
  }

  function groupsForMode() {
    if (state.mode === "week") return data.weeks;
    if (state.mode === "theme") return data.themes;
    if (state.mode === "academic") {
      return [
        { id: "all", label: "全部顶会类别", count: data.academic?.coverage?.scored_top_venue_papers || 0 },
        ...(data.academic?.categories || []).map((item) => ({
          ...item,
          count: (data.academic?.publications || []).filter((paper) => paper.venue_group === item.id).length,
        })),
      ];
    }
    return [{ id: "all", label: "全部观点", count: data.viewpoints.length }];
  }

  function renderFilters() {
    const groups = groupsForMode();
    elements.filterTitle.textContent =
      state.mode === "week"
        ? "周次"
        : state.mode === "theme"
          ? "论文主题"
          : state.mode === "academic"
            ? "顶会类别"
            : "观点来源";
    elements.filterList.innerHTML = groups.map((group) => `
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
      return inGroup && (!query || searchable(paper).includes(query));
    });
    papers = [...papers].sort((a, b) => {
      if (state.sort === "title") return a.title.localeCompare(b.title);
      return b.first_seen.localeCompare(a.first_seen) || a.title.localeCompare(b.title);
    });
    return papers;
  }

  function paperSummary(paper) {
    return paper.details?.question
      || paper.details?.recommendation
      || `${paper.authors.slice(0, 3).join("、")}${paper.authors.length > 3 ? " 等" : ""}`;
  }

  function renderPaperCard(paper) {
    return `
      <article class="paper-card" tabindex="0" role="button" data-paper="${escapeHtml(paper.id)}"
               aria-label="查看 ${escapeHtml(paper.title)} 的缓存精读">
        <div class="card-meta">
          <strong>${escapeHtml(paper.week)}</strong>
          <span>${escapeHtml((paper.venues || []).join(" · "))}</span><br>
          <span>${dateText(paper.first_seen)}</span>
        </div>
        <div class="card-body">
          <h3>${escapeHtml(paper.title)}</h3>
          <p class="card-summary">${escapeHtml(paperSummary(paper))}</p>
          <div class="tags">
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

  function renderAcademic() {
    const academic = data.academic || {};
    const query = state.query.toLocaleLowerCase("zh-CN");
    const institutions = [...(academic.institutions || [])]
      .filter((item) => !query || searchable(item).includes(query))
      .map((item) => ({ ...item, score: academicScore(item) }))
      .filter((item) => item.score > 0 || (state.group === "all" && state.academicYear === "all"))
      .sort((a, b) => b.score - a.score || b.papers.length - a.papers.length || a.name.localeCompare(b.name));
    const scholars = [...(academic.scholars || [])]
      .filter((item) => !query || searchable(item).includes(query))
      .map((item) => ({ ...item, score: academicScore(item) }))
      .filter((item) => item.score > 0 || (state.group === "all" && state.academicYear === "all"))
      .sort((a, b) => b.score - a.score || b.papers.length - a.papers.length || a.name.localeCompare(b.name));
    const graphNodes = institutions.slice(0, 12);
    const nodeNames = new Set(graphNodes.map((item) => item.name));
    const positions = new Map(graphNodes.map((item, index) => {
      const angle = (Math.PI * 2 * index / Math.max(graphNodes.length, 1)) - Math.PI / 2;
      const radiusX = graphNodes.length < 5 ? 260 : 340;
      const radiusY = graphNodes.length < 5 ? 150 : 195;
      return [item.name, {
        x: 450 + Math.cos(angle) * radiusX,
        y: 260 + Math.sin(angle) * radiusY,
      }];
    }));
    const edges = (academic.collaborations || []).filter((edge) =>
      nodeNames.has(edge.source)
      && nodeNames.has(edge.target)
      && edge.papers.some(academicPaperMatches)
    );
    if (!state.academicInstitution || !institutions.some((item) => item.name === state.academicInstitution)) {
      state.academicInstitution = institutions[0]?.name || "";
    }
    const selected = institutions.find((item) => item.name === state.academicInstitution);
    const partners = selected
      ? edges.filter((edge) => edge.source === selected.name || edge.target === selected.name)
        .map((edge) => ({
          name: edge.source === selected.name ? edge.target : edge.source,
          weight: edge.papers.filter(academicPaperMatches).length,
        }))
        .sort((a, b) => b.weight - a.weight || a.name.localeCompare(b.name))
      : [];

    elements.contentEyebrow.textContent = "ACADEMIC NETWORK";
    elements.contentTitle.textContent = "学术关系";
    elements.resultCount.textContent = `${institutions.length} 个单位`;
    elements.sort.hidden = true;
    elements.academicYear.hidden = false;
    elements.empty.hidden = institutions.length > 0;
    elements.cardList.innerHTML = institutions.length ? `
      <section class="academic-intro">
        <div>
          <p class="eyebrow">VERIFIED LOWER BOUND</p>
          <h3>用已核验论文连接单位、学者与合作关系</h3>
        </div>
        <p>${escapeHtml(academic.coverage?.score_definition || "")}</p>
        <dl>
          <div><dt>可解析论文</dt><dd>${academic.coverage?.papers_with_affiliations || 0}</dd></div>
          <div><dt>计分顶会论文</dt><dd>${academic.coverage?.scored_top_venue_papers || 0}</dd></div>
          <div><dt>合作单位</dt><dd>${academic.institutions?.length || 0}</dd></div>
        </dl>
      </section>
      <section class="network-section" aria-labelledby="networkTitle">
        <div class="subsection-heading">
          <div><p class="eyebrow">COLLABORATION MAP</p><h3 id="networkTitle">单位合作网络</h3></div>
          <p>节点优先展示当前筛选下分数较高的单位；连线粗细表示 papernote 库内共同论文数。</p>
        </div>
        <div class="network-board">
          <svg viewBox="0 0 900 520" role="img" aria-label="学术单位合作连线">
            ${edges.map((edge) => {
              const left = positions.get(edge.source);
              const right = positions.get(edge.target);
              const weight = edge.papers.filter(academicPaperMatches).length;
              return `<line x1="${left.x}" y1="${left.y}" x2="${right.x}" y2="${right.y}" style="--weight:${Math.min(weight, 4)}"></line>`;
            }).join("")}
          </svg>
          ${graphNodes.map((item) => {
            const point = positions.get(item.name);
            return `<button class="network-node ${item.name === state.academicInstitution ? "is-selected" : ""}"
              type="button" data-institution="${escapeHtml(item.name)}"
              style="--x:${point.x / 9}%;--y:${point.y / 5.2}%">
              <strong>${escapeHtml(item.name)}</strong><span>${item.score} 分 · ${item.papers.length} 篇</span>
            </button>`;
          }).join("")}
        </div>
        ${selected ? `
          <article class="network-detail">
            <div><p class="eyebrow">SELECTED GROUP</p><h3>${escapeHtml(selected.name)}</h3>
              <p>${selected.score} 分 · ${selected.papers.length} 篇库内论文 · ${selected.scholars.length} 位关联学者</p>
            </div>
            <div><strong>关联学者</strong><p>${selected.scholars.slice(0, 16).map(escapeHtml).join("、")}</p></div>
            <div><strong>主要合作单位</strong><p>${partners.length ? partners.slice(0, 8).map((item) => `${escapeHtml(item.name)}（${item.weight}）`).join("、") : "当前筛选下暂无跨单位合作边"}</p></div>
          </article>` : ""}
      </section>
      <section class="rankings">
        <div>
          <div class="subsection-heading compact"><div><p class="eyebrow">INSTITUTIONS</p><h3>单位优先检索序列</h3></div></div>
          <ol class="ranking-list">
            ${institutions.slice(0, 12).map((item, index) => `
              <li><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(item.name)}</strong>
              <small>${item.scholars.length} 位学者 · ${item.papers.length} 篇库内论文</small></div><b>${item.score}</b></li>
            `).join("")}
          </ol>
        </div>
        <div>
          <div class="subsection-heading compact"><div><p class="eyebrow">SCHOLARS</p><h3>学者优先检索序列</h3></div></div>
          <ol class="ranking-list">
            ${scholars.slice(0, 12).map((item, index) => `
              <li><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(item.name)}</strong>
              <small>${item.institutions.map(escapeHtml).join(" · ")}</small></div><b>${item.score}</b></li>
            `).join("")}
          </ol>
        </div>
      </section>
    ` : "";
    $$(".network-node").forEach((button) => {
      button.addEventListener("click", () => {
        state.academicInstitution = button.dataset.institution;
        renderAcademic();
      });
    });
  }

  function renderContent() {
    elements.academicYear.hidden = state.mode !== "academic";
    if (state.mode === "academic") {
      renderAcademic();
      return;
    }
    if (state.mode === "viewpoints") {
      const query = state.query.toLocaleLowerCase("zh-CN");
      const items = data.viewpoints.filter((item) => !query || searchable(item).includes(query));
      elements.contentEyebrow.textContent = "INDUSTRY NOTES";
      elements.contentTitle.textContent = "行业观点";
      elements.resultCount.textContent = `${items.length} 条`;
      elements.cardList.innerHTML = items.map(renderViewpointCard).join("");
      elements.sort.hidden = true;
      elements.empty.hidden = items.length > 0;
      return;
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
      const open = () => openPaper(card.dataset.paper);
      card.addEventListener("click", open);
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          open();
        }
      });
    });
  }

  function detailSection(label, value) {
    return value ? `<section class="detail-section"><h3>${label}</h3><p>${escapeHtml(value)}</p></section>` : "";
  }

  function openPaper(id) {
    const paper = data.papers.find((item) => item.id === id);
    if (!paper) return;
    const details = paper.details || {};
    const sourceLinks = details.original_links?.length
      ? details.original_links
      : (paper.urls || []).map((url, index) => ({
          label: index ? `相关链接 ${index + 1}` : "访问论文来源",
          url,
        }));
    elements.dialogContent.innerHTML = `
      <p class="eyebrow">${escapeHtml(paper.theme_label)} · ${escapeHtml(paper.week)}</p>
      <h2 class="dialog-title">${escapeHtml(paper.title)}</h2>
      <p class="dialog-byline">
        ${escapeHtml(paper.authors.join("、"))}<br>
        ${escapeHtml(details.venue_status || `${(paper.venues || []).join(" · ")} · ${paperStatusLabel(paper)}`)}
      </p>
      ${detailSection("方向", details.direction)}
      ${detailSection("关键词", details.keywords)}
      ${detailSection("单位与作者", details.author_affiliations)}
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
    elements.dialog.showModal();
  }

  function render() {
    renderFilters();
    renderContent();
  }

  $$(".mode-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      state.mode = tab.dataset.mode;
      state.group = groupsForMode()[0]?.id || "all";
      if (state.mode === "academic") state.academicInstitution = "";
      $$(".mode-tab").forEach((item) => item.classList.toggle("is-active", item === tab));
      render();
    });
  });

  elements.search.addEventListener("input", () => {
    state.query = elements.search.value.trim();
    renderContent();
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
  $(".dialog-close").addEventListener("click", () => elements.dialog.close());
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
