# 论文内容讨论记录｜2026-W40 来源覆盖与正文缺口

- **记录类型**：待正文核验
- **记录状态**：待补充
- **记录来源**：用户要求本期缺少正文、身份对应或可靠外部证据的项目写入 inquiries

## 本期检索边界

- **统计窗口**：2026-09-22 至 2026-09-28；2026-09-29 执行与核验。
- **近 4 期新收录**：W36–W39 共 40 篇，全部来自 IEEE S&P 2026；安全组 100%，软件与系统组 0%，人工智能组 0%。历史状态更新不计入新收录。
- **轮换策略**：安全组从 CCS、NDSS 开始；软件与系统组从 ASE、ISSTA 开始；人工智能组从 NeurIPS、ACL 开始。S&P 与 USENIX Security 仍完成扫描，但不继续扩大最近四期的单一来源偏差。
- **本期软配额**：安全组 4 篇、软件与系统组 3 篇、人工智能组 3 篇；最终严格完成 4/3/3。安全组由 CCS 2 篇、NDSS 2 篇组成，单会未超过 2 篇。

## 会议来源覆盖

“候选数”只统计通过主题相关性初筛的项目，不代表会议全部论文数量。

| 来源组 | 会议 | 初筛候选 | 入选 | 未入选或未继续原因 |
| --- | --- | ---: | ---: | --- |
| 安全 | ACM CCS | 4 | 2 | 其余候选在主题覆盖、证据密度或配额内优先级较低 |
| 安全 | NDSS | 5 | 2 | 其余候选留作后续轮换，避免单会集中 |
| 安全 | IEEE S&P | 3 | 0 | W36–W39 已连续集中收录，本期优先纠偏 |
| 安全 | USENIX Security | 3 | 0 | 已完成扫描；在 4 篇安全组额度内优先 CCS、NDSS |
| 软件与系统 | ASE | 3 | 1 | 其余候选的安全贡献或正文证据优先级较低 |
| 软件与系统 | ISSTA | 6 | 2 | 另有 2 篇安全相关论文缺少公开正文，进入下方待核验清单 |
| 软件与系统 | PLDI | 0 | 0 | 未发现同时满足安全相关性与正文门槛的新候选 |
| 软件与系统 | POPL | 0 | 0 | 未发现同时满足安全相关性与正文门槛的新候选 |
| 软件与系统 | FSE | 2 | 0 | 安全相关性或证据密度低于本期入选项 |
| 软件与系统 | SOSP | 0 | 0 | 未发现本期可核验的新候选 |
| 软件与系统 | OOPSLA | 1 | 0 | 主题优先级低于入选项 |
| 软件与系统 | ICSE | 2 | 0 | 主题优先级低于入选项 |
| 软件与系统 | OSDI | 1 | 0 | 已扫描技术议程；未发现更适合本期的安全论文 |
| 软件与系统 | FM | 0 | 0 | 未发现本期可核验的新候选 |
| 人工智能 | NeurIPS | 5 | 3 | 正式论文集与正文齐备；其余候选因配额和主题重叠未入选 |
| 人工智能 | ACL | 2 | 0 | 已扫描 Anthology；在 3 篇额度内优先证据更完整的 NeurIPS 候选 |
| 人工智能 | CVPR | 2 | 0 | 已扫描 Open Access；候选与智能体攻击主题重叠 |
| 人工智能 | ICCV | 1 | 0 | 已扫描 Open Access；未发现优先级更高的新候选 |
| 人工智能 | ICML | 2 | 0 | 已扫描 PMLR；候选在配额内优先级较低 |
| 人工智能 | ICLR | 2 | 0 | 已扫描 OpenReview；候选在配额内优先级较低 |
| 人工智能 | AAAI | 0 | 0 | 未发现正文与接收身份均可核验的本期候选 |
| 补充 | arXiv | 4 | 0 | 仅用于补充发现；本期 3 篇软件组入选项虽有 arXiv 正文，均由会议官方列表确认接收，不按纯预印处理 |

## 第二阶段精读候选

| 来源组 | 论文 | 身份证据 | 正文来源 |
| --- | --- | --- | --- |
| 安全 | BFId: Identity Inference Attacks Utilizing Beamforming Feedback Information | CCS 2025 官方接收列表、DOI 10.1145/3719027.3765062 | KIT 机构仓库作者版 |
| 安全 | Be Aware of What You Let Pass: Demystifying URL-based Authentication Bypass Vulnerability in Java Web Applications | CCS 2025 官方接收列表、DOI 10.1145/3719027.3765199 | 作者公开 PDF |
| 安全 | ACE: A Security Architecture for LLM-Integrated App Systems | NDSS 2026 官方论文页、DOI 10.14722/ndss.2026.230352 | NDSS 官方 PDF |
| 安全 | BLERP: BLE Re-Pairing Attacks and Defenses | NDSS 2026 官方论文页 | NDSS 官方 PDF；第二阶段从正文核验 DOI |
| 软件与系统 | Inferring 1-Minimal Trigger Configurations for Assessing Linux Kernel CVE Triggerability | ISSTA 2026 官方列表 | arXiv:2608.15225 正文 |
| 软件与系统 | Checked-In Secret Detection: Strings Are All You Need | ISSTA 2026 官方列表 | arXiv:2608.04523 正文 |
| 软件与系统 | Learning to Triage Vulnerability Reports from Program Analysis: An Empirical Study in Node.js | ASE 2026 官方列表 | arXiv:2510.20739 正文 |
| 人工智能 | Security Challenges in AI Agent Deployment: Insights from a Large Scale Public Competition | NeurIPS 2025 官方论文集、DOI 10.52202/085713-2676 | NeurIPS 官方 PDF |
| 人工智能 | SECODEPLT: A Unified Benchmark for Evaluating the Security Risks and Capabilities of Code GenAI | NeurIPS 2025 官方论文集、DOI 10.52202/085713-0447 | NeurIPS 官方 PDF |
| 人工智能 | MIP against Agent: Malicious Image Patches Hijacking Multimodal OS Agents | NeurIPS 2025 官方论文集、DOI 10.52202/085713-0625 | NeurIPS 官方 PDF |

10 篇均已按 DOI、arXiv ID、正式 URL、规范化标题与现有索引去重。正式接收身份来自会议官方列表、官方论文集或 DOI；正文可用性在进入精读前逐项确认。

## 待正文核验

### Ghosts in the Memory: Detecting Unintended Sensitive Data in Android Apps

- **关联论文 ID**：未入库
- **可靠来源**：ISSTA 2026 官方论文页
- **已核验事实**：官方页面确认题目、作者和 Research Papers 身份，只公开摘要，当前未找到作者版、机构仓库版或正式论文正文。
- **局限与未决问题**：无法核验 ANDROID-MRI 的内核插桩设计、实验对照、50 个应用的抽样偏差和漏洞披露证据。
- **后续处理**：已写入 `papers/watchlist.jsonl`，状态为 `awaiting-public-fulltext`，目标周 2026-W41。

### How Safe is Your Screen? Understanding and Detecting Privacy Leaks in Sensitive Activities

- **关联论文 ID**：未入库
- **可靠来源**：ISSTA 2026 官方论文页
- **已核验事实**：官方页面确认题目、作者和 Research Papers 身份，只公开摘要，当前未找到作者版、机构仓库版或正式论文正文。
- **局限与未决问题**：无法核验 ASSA 的静态分析与 LLM 判定流程、5,667 个应用样本构造、敏感页面判定误差及披露证据。
- **后续处理**：已写入 `papers/watchlist.jsonl`，状态为 `awaiting-public-fulltext`，目标周 2026-W41。

## 行业固定来源池扫描

| 来源 | 初筛候选 | 第二阶段保留 | 处理说明 |
| --- | ---: | ---: | --- |
| Google Project Zero | 0 | 0 | 未发现窗口内新的完整技术条目 |
| Google Threat Intelligence / Mandiant | 2 | 1 | 保留 CI/CD 基础设施加固；同源 AI 基础设施条目因来源集中未保留 |
| Microsoft Security | 2 | 0 | 近期高优先级内容已在前期覆盖，窗口内无更强新证据 |
| Palo Alto Unit 42 | 2 | 1 | 保留 AWS 暴露凭证隔离实测；排除偏市场传播条目 |
| Cisco Talos | 1 | 1 | 保留 Closed Quorum 静态分析，并在精读中区分样本能力与真实部署证据 |
| 腾讯玄武 | 0 | 0 | 归档页无窗口内新条目 |
| 腾讯科恩 | 0 | 0 | 未找到正文可访问的新技术条目 |
| Anthropic | 2 | 1 | 保留 2026-09 威胁情报报告；同月已收录事件不重复 |
| OpenAI | 2 | 1 | 保留 Path to Astra，待核验评测口径与厂商自述边界 |
| NIST | 1 | 0 | 相关令牌指南已在 W39 收录，无重复加入 |
| CISA | 0 | 0 | 窗口内以通告为主，缺少适合观点库的完整方法材料 |
| Gartner | 1 | 0 | 摘要与付费材料不足以核验方法和数据 |
| Forrester | 1 | 0 | 市场报告正文不可充分核验，排除 |
| IDC | 0 | 0 | 未找到正文可访问且含方法或数据的新条目 |

行业候选共保留 5 篇，均已按规范 URL、标题、来源与日期和现有观点库去重；正文分析留待第二阶段。
