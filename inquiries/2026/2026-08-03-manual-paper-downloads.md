# 待人工补充论文正文｜2026-08-03

本名单只记录本期能由正式会议页面确认题目与接收状态、但无法取得公开全文的论文。当前仅依据官方摘要，不据此补全方法、实验、作者单位映射或结论。

## 高优先级

### Cloud-Native Carjacking: Fleet-wide Compromise via Telematics Authorization Failures

- **可靠来源**：[USENIX Security 2026 官方页面](https://www.usenix.org/conference/usenixsecurity26/presentation/liu-yangyang)
- **当前可见范围**：官方题目、作者与摘要；会议原文仍受访问限制。
- **为什么优先**：涉及车联网后端授权、跨车辆权限提升和远程控制，直接关系移动与物联网安全；摘要声称覆盖三家主要车企平台，需要全文核验攻击前提与影响边界。
- **需要补充**：作者公开版或会议 PDF。
- **需要核验的章节或证据**：威胁模型；种子车辆与认证材料获取条件；MQTT、HTTPS、SMS 三条路径的对象绑定缺陷；车辆与平台样本范围；远程控制、媒体访问和后备命令的复现实验；厂商披露与修复状态；伦理与局限。

### Relay and Betray: Exploiting Client-Side Authority in Multi-User Mixed Reality

- **可靠来源**：[USENIX Security 2026 官方页面](https://www.usenix.org/conference/usenixsecurity26/presentation/ali)
- **当前可见范围**：官方题目、作者与摘要；会议原文仍受访问限制。
- **为什么优先**：摘要报告对 20 个多人混合现实应用的系统测量，涵盖监控、对象篡改、安全功能绕过、拒绝服务和身份冒充，但不能仅凭摘要判断各类别证据强度。
- **需要补充**：作者公开版或会议 PDF。
- **需要核验的章节或证据**：应用选择与版本；客户端状态同步模型和安全不变量；运行时插桩与恶意头像方法；五类攻击的逐项复现；隐私和安全影响边界；厂商披露；跨平台可迁移性与局限。

## 状态复核

### Not In My Git Yard: Catching Backdoors at Commit and Release Time

- **可靠来源**：[arXiv 原文](https://arxiv.org/abs/2607.26719)、[ASE 2026 官方站点](https://conf.researchr.org/track/ase-2026/ase-2026-research-track)、[稿件所列 DOI](https://doi.org/10.1145/3832783.3834352)
- **当前判断**：全文可读并已按预印收录；稿件声明将发表于 ASE 2026，但本期官方程序返回访问拒绝，DOI 解析为 404，不能独立核验正式状态。
- **后续动作**：官方程序或 ACM DOI 可访问后，更新现有索引条目和 W32 卡片为“ASE 2026｜接收”，不要新增重复记录。
