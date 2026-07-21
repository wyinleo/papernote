# 2026-W30 智能体、移动与应用安全论文动态

- **日期**：2026-07-21 20:19（北京时间）
- **原始问题**：每周检索自上次成功运行以来新发布、正式接收、实质更新或值得重点关注的智能体安全、移动安全与应用安全论文；按安全四大、软件工程 CCF-A、AI CCF-A、arXiv 的优先级筛选，生成中文精选周报，与本地索引去重并提交/推送 papernote 仓库。
- **本次可见检索问询**：
  - USENIX Security ’26 官方会议页、Cycle 1 accepted papers、技术议程和候选论文会前 PDF；
  - IEEE S&P 2026、ACM CCS 2026、NDSS 2026 官方 accepted/program 页面；
  - ISSTA 2026 官方 accepted papers，重点核验 agent、Android/OpenHarmony、privacy、secure code generation；
  - arXiv 官方 API：`cat:cs.CR AND submittedDate:[202607170000 TO 202607212359]`，按提交时间降序，返回 74 条；
  - 对候选逐篇核对 arXiv 元数据、作者单位、实验规模、局限、会议备注与公开 artifact。
- **答复摘要**：精选 7 篇：2 篇正式接收论文（USENIX Security ’26、ISSTA 2026）和 5 篇明确标为“arXiv 未同行评审”的预印本。主趋势为真实检索链路攻击、agent data 字段级信任、持久记忆/自状态、adaptive red teaming，以及 EM 辅助黑盒固件 fuzzing。选出 3 篇重点精读，并把只有题目、缺少摘要/全文的 ISSTA 移动安全论文留作跟踪。
- **关联论文 ID**：usenix-sec26-chang-retrieval-barrier；issta26-chen-insecure-memory；arxiv-2607-05120-agent-data-injection；arxiv-2607-18063-adaptive-adversaries；arxiv-2607-14611-bad-memory；arxiv-2607-17986-self-state-attacks；arxiv-2607-16487-fuzz-emup
- **去重与状态说明**：以 2026-07-17 W29 仓库提交作为上一成功基线；按 DOI、arXiv ID、正式 URL、规范化标题检查现有 8 条索引，无重复。由于自动化 memory 缺失，本次另补录 3 篇基线遗漏论文，并在周报中保留其原始发布日期，不将其伪称为本周新论文。
- **后续追踪**：等待 ISSTA 2026 移动/Agent 安全论文公开摘要、PACMSE DOI 或作者预印本；USENIX Security ’26 大会首日复核 Cycle 2 embargo 论文；arXiv 条目若正式发表则更新原索引而不新增重复记录。
