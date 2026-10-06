# 论文内容讨论记录｜2026-W41 来源覆盖与正文缺口

- **记录类型**：待正文核验
- **记录状态**：待补充
- **记录来源**：本期自动化要求记录来源均衡、软配额偏离和缺少正文的候选

## 本期检索边界

- **统计窗口**：2026-09-29 至 2026-10-05；2026-10-06 执行与核验。
- **近 4 期新收录**：W37–W40 共 40 篇，其中安全组 34 篇（85%）、软件与系统组 3 篇（7.5%）、人工智能组 3 篇（7.5%）。W37–W39 的 30 篇均来自 IEEE S&P；W40 已恢复 4/3/3 分布。
- **轮换策略**：安全组从 USENIX Security、CCS 开始；软件与系统组从 ISSTA、FSE、ASE 开始；人工智能组从 ACL、ICML、CVPR 开始。三组列出的会议均完成扫描，S&P 继续主动降权。
- **本期软配额**：安全组 4 篇、软件与系统组 3 篇、人工智能组 3 篇；最终完成 4/3/3。安全组由 CCS 1 篇、NDSS 2 篇、USENIX Security 1 篇组成，单会未超过 2 篇。

## 会议来源覆盖

“候选数”只统计通过安全主题相关性初筛的项目，不代表会议全部论文数量。

| 来源组 | 会议 | 初筛候选 | 入选 | 未入选或未继续原因 |
| --- | --- | ---: | ---: | --- |
| 安全 | USENIX Security | 4 | 1 | 保留文件系统符号链接实证研究；其余候选按配额留作后续轮换 |
| 安全 | ACM CCS | 4 | 1 | 保留获杰出论文奖且正文、代码齐备的 SyzSpec；其余候选与近期主题重合或优先级较低 |
| 安全 | NDSS | 4 | 2 | 两篇分别覆盖身份混淆与内核内存利用，达到单会软上限 |
| 安全 | IEEE S&P | 2 | 0 | W37–W39 已连续集中收录，本期继续纠正四期来源偏差 |
| 软件与系统 | ISSTA | 6 | 2 | 两篇正文齐备；另两篇到期候选仍缺公开正文，进入下方清单 |
| 软件与系统 | FSE | 6 | 0 | 已扫描安全、模糊测试和供应链议题，配额内优先 ISSTA 与 ASE 的证据完整候选 |
| 软件与系统 | ASE | 6 | 1 | 保留 JavaScript 依赖能力分析；其余候选主题重合或会议尚未开始 |
| 软件与系统 | PLDI | 0 | 0 | 未发现同时满足安全相关性、接收身份与正文门槛的新候选 |
| 软件与系统 | POPL | 0 | 0 | 未发现同时满足三项门槛的新候选 |
| 软件与系统 | SOSP | 2 | 0 | 完成接收列表扫描，系统贡献的安全相关性低于入选项 |
| 软件与系统 | OOPSLA | 1 | 0 | 候选安全贡献优先级低于入选项 |
| 软件与系统 | ICSE | 4 | 0 | 已扫描研究轨及安全相关研讨会，未发现更适合本期的正文候选 |
| 软件与系统 | OSDI | 2 | 0 | 已扫描正式议程，候选安全主题与本期入选项重合 |
| 软件与系统 | FM | 1 | 0 | 已扫描研究轨，安全相关候选缺少本期所需的直接实证贡献 |
| 人工智能 | ACL | 4 | 1 | 保留系统提示供应链投毒研究，正文与 DOI 齐备 |
| 人工智能 | ICML | 4 | 1 | 保留提示注入的角色混淆机制研究，正文与软件链接齐备 |
| 人工智能 | CVPR | 3 | 1 | 保留多模态智能体 CAPTCHA 研究，官方开放正文齐备 |
| 人工智能 | NeurIPS | 2 | 0 | 已扫描 2026 下载页；与本期提示注入主题重合，留待后续轮换 |
| 人工智能 | ICCV | 3 | 0 | 已扫描 2025 官方开放论文集，时效与主题优先级低于入选项 |
| 人工智能 | ICLR | 3 | 0 | 已扫描 OpenReview，候选在配额内优先级较低 |
| 人工智能 | AAAI | 2 | 0 | 已扫描正式论文与奖项页，候选与本期主题重合 |
| 补充 | arXiv | 2 | 0 | 检索到 2610.04269、2610.05266 等当周预印本；缺少同行评审身份，本期优先正式会议论文 |

## 第二阶段精读候选

| 来源组 | 论文 | 身份证据 | 正文来源 |
| --- | --- | --- | --- |
| 安全 | SyzSpec: Specification Generation for Linux Kernel Fuzzing via Under-Constrained Symbolic Execution | CCS 2025 正式论文、DOI 10.1145/3719027.3744811 | 作者公开 PDF 与项目仓库 |
| 安全 | One Email, Many Faces: A Deep Dive into Identity Confusion in Email Aliases | NDSS 2026 官方论文页、DOI 10.14722/ndss.2026.230148 | NDSS 官方 PDF |
| 安全 | Cross-Cache Attacks for the Linux Kernel via PCP Massaging | NDSS 2026 官方论文页、DOI 10.14722/ndss.2026.240862 | NDSS 官方 PDF |
| 安全 | Wormholes in the File System: Understanding the Misunderstanding of Symlinks | USENIX Security 2026 官方论文页 | USENIX 官方 PDF |
| 软件与系统 | The Illusion of Success: Learning-Based Android Malware Detectors (Replicability Study) | ISSTA 2026 官方 Research Papers 页面 | 作者公开 PDF |
| 软件与系统 | Secrets Unlocked: Evaluating LLMs for Secrets Detection in Android Apps | ISSTA 2026 官方 Research Papers 页面 | 作者公开 PDF |
| 软件与系统 | Defensive Capability Analysis for JavaScript Libraries | ASE 2026 官方 Research Papers 页面 | 作者公开 PDF |
| 人工智能 | PARASITE: Conditional System Prompt Poisoning to Hijack LLMs | ACL 2026 Anthology、DOI 10.18653/v1/2026.acl-long.668 | ACL Anthology 官方 PDF |
| 人工智能 | Prompt Injection as Role Confusion | ICML 2026 PMLR 正式论文集 | PMLR 官方 PDF |
| 人工智能 | DualMirage: Hunting Stealthy Multimodal LLM Agents via CAPTCHAs with Contour and Adversarial Illusions | CVPR 2026 官方开放论文集 | CVF 官方 PDF |

10 篇均已按 DOI、正式 URL和规范化标题与现有索引去重；接收身份来自会议官方页面、正式论文集或 DOI，正文可用性已逐项确认。

## 待正文核验

### Ghosts in the Memory: Detecting Unintended Sensitive Data in Android Apps

- **关联论文 ID**：未入库
- **可靠来源**：ISSTA 2026 官方论文页
- **已核验事实**：官方页面确认题目、作者和 Research Papers 身份；截至 2026-10-06 仍只有摘要，没有论文链接。
- **局限与未决问题**：无法核验 ANDROID-MRI 的内核插桩、RASP 绕过实验、50 个应用的抽样偏差和披露证据。
- **后续处理**：`papers/watchlist.jsonl` 已顺延至 2026-W42，会议结束后复查作者版、机构仓库和 PACMSE。

### How Safe is Your Screen? Understanding and Detecting Privacy Leaks in Sensitive Activities

- **关联论文 ID**：未入库
- **可靠来源**：ISSTA 2026 官方论文页
- **已核验事实**：官方页面确认题目、作者和 Research Papers 身份；截至 2026-10-06 仍只有摘要，没有论文链接。
- **局限与未决问题**：无法核验 ASSA 的静态分析与 LLM 判定流程、5,667 个应用的样本构造、敏感页面判定误差和披露证据。
- **后续处理**：`papers/watchlist.jsonl` 已顺延至 2026-W42，会议结束后复查作者版、机构仓库和 PACMSE。

## 行业固定来源池扫描

| 来源 | 初筛候选 | 第二阶段保留 | 处理说明 |
| --- | ---: | ---: | --- |
| Google Project Zero | 0 | 0 | 未发现窗口内新的完整技术条目 |
| Google Threat Intelligence / Mandiant | 0 | 0 | 未发现窗口内正文和独立证据均足的新报告 |
| Microsoft Security | 3 | 1 | 保留 Zimbra CVE-2026-73570 攻击链；其余条目按来源多样性排除 |
| Palo Alto Unit 42 | 2 | 1 | 保留 Kubernetes Operator 权限实测与开源分析器；NetScaler 简报的独立方法材料较少 |
| Cisco Talos | 3 | 0 | UAT-11587 等条目证据充分，但近期已连续收录 Talos，按来源轮换暂缓 |
| 腾讯玄武 | 0 | 0 | 归档页无窗口内新条目 |
| 腾讯科恩 | 0 | 0 | 未找到正文可访问的新技术条目 |
| Anthropic | 1 | 1 | 保留协调漏洞披露仪表盘；精读时区分候选、外部复核、维护者确认和修复四类计数 |
| OpenAI | 1 | 1 | 保留协同模型蒸馏活动；精读时明确请求量表示尝试量，不代表成功提取量 |
| NIST | 2 | 1 | 保留 5G 假基站测试白皮书草案；标注征求意见稿状态 |
| CISA | 0 | 0 | 窗口内以漏洞通告和训练资源为主，缺少适合观点库的完整方法材料 |
| Gartner | 1 | 0 | 摘要与付费材料不足以核验方法和数据 |
| Forrester | 1 | 0 | 可访问内容不足以支持独立核验 |
| IDC | 0 | 0 | 未找到正文可访问且含方法或数据的新条目 |

行业候选最终保留 5 篇，覆盖厂商威胁研究、云原生权限、AI 漏洞发现、模型安全运营和政府测试指南；均已按规范 URL、标题、来源、日期与现有观点库去重。
