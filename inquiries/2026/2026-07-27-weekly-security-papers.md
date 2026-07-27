# 2026-07-27 每周安全论文检索记录

## 任务可见问询

- 生成 2026-W31 智能体安全、移动安全与应用安全论文动态，并同步仓库、索引与网页。
- “本周范围”不是只限最近七天首次公开；此前遗漏、已经正式发表且值得补齐的论文也可在本期收录，但必须标明原始公开时间和“基线补录”。
- 维护知名学术单位与学者关系库，用正式核验的年度安全四大、软件工程 CCF-A 和 AI CCF-A 论文数形成优先检索分数。
- 学术关系库公开显示在 papernote 网页；当前覆盖不完整时，分数必须标为“已核验下界”，不能伪装成完整机构排名。
- 无法稳定取得或解析正文的候选形成单独名单，由用户后续补充 PDF；没有全文时不推断方法和实验。
- 每次任务结束时，把聊天中形成的可复用要点固化到自动化计划卡和仓库工作流说明。

## 本次检索问询与来源

1. arXiv `cs.CR` 2026-07-21 至 2026-07-27 最近列表：筛查智能体、移动、应用与软件供应链安全候选。
2. `site:usenix.org/conference/usenixsecurity25 agent prompt injection`：补查 USENIX Security 2025 智能体安全正式论文。
3. `site:usenix.org/conference/usenixsecurity25/presentation Android OR iOS OR mobile OR web vulnerability`：补查移动与应用安全正式论文。
4. USENIX Security 2025 官方论文页与 PDF：
   - [Make Agent Defeat Agent](https://www.usenix.org/conference/usenixsecurity25/presentation/liu-fengyu)
   - [Cloak, Honey, Trap](https://www.usenix.org/conference/usenixsecurity25/presentation/ayzenshteyn)
   - [TapTrap](https://www.usenix.org/conference/usenixsecurity25/presentation/beer)
   - [XSSky](https://www.usenix.org/conference/usenixsecurity25/presentation/shi-youkun)
5. arXiv 官方正文：
   - [IssueTrojanBench](https://arxiv.org/abs/2607.20759)
   - [RECEIPT](https://arxiv.org/abs/2607.18575)
6. 待检索清单候选：
   - [Towards Long-Horizon Agents: A Survey](https://www.preprints.org/manuscript/202607.1328)

## 筛选结果

- 正式接收基线补录 4 篇：AgentFuzz、CHeaT、TapTrap、XSSky。
- 本周预印收录 2 篇：IssueTrojanBench、RECEIPT。
- *Towards Long-Horizon Agents: A Survey* 因安全仅为通用综述的一部分、缺少独立安全方法或实证而暂缓，保留在待检索清单。
- 其他无法完成全文核验的候选写入 `2026-07-27-manual-paper-downloads.md`，不进入索引。

## 历史状态回查

回查既有索引中 5 篇仅有 arXiv 来源的预印本和带作者自述研讨会信息的条目。未找到会议官方论文列表、正式论文集或 DOI 页面支持状态升级，因此本期不改动原条目与原卡片。
